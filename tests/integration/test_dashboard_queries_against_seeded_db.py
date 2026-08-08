import os
import uuid
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from monitoring.db.models import RunTrace, JudgeScore, DriftEvent, PromptVersion, ModelConfig, JudgeVersion

@pytest.fixture(scope="module")
def db_session():
    # Use the integration test DB
    os.environ["DATABASE_URL"] = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://dev_user:dev_password@127.0.0.1:5435/llm_monitoring_dev"
    )
    engine = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_dashboard_aggregations(db_session):
    """
    Seeds the database with traces, scores, and drift events.
    Executes standard 'dashboard' queries and asserts the aggregations are correct.
    """
    # 1. Clean up old data for this test run to prevent clashes
    test_feature = "dashboard_test_feature"
    db_session.query(JudgeScore).filter(JudgeScore.run_trace_id.in_(
        db_session.query(RunTrace.id).filter_by(feature_name=test_feature)
    )).delete(synchronize_session=False)
    db_session.query(RunTrace).filter_by(feature_name=test_feature).delete()
    db_session.query(DriftEvent).filter_by(feature_name=test_feature).delete()
    db_session.commit()

    # 2. Seed prerequisites
    prompt_id = uuid.uuid4()
    db_session.add(PromptVersion(
        id=prompt_id, feature_name=test_feature, content_hash="hash1",
        prompt_text="test", version_label="v1", created_by="test"
    ))
    model_id = uuid.uuid4()
    db_session.add(ModelConfig(
        id=model_id, provider="test", model_name="test_model", content_hash="mhash1"
    ))
    db_session.commit()
    
    judge_id = uuid.uuid4()
    db_session.add(JudgeVersion(
        id=judge_id, rubric_content_hash="rhash", rubric_text="rubric",
        judge_model_config_id=model_id, calibration_status="calibrated"
    ))
    db_session.commit()

    # 3. Seed Traces and Scores (Today and Yesterday)
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    # 2 Successful traces today, 1 failed today, 1 successful yesterday
    def make_trace(created_at, error=None, cost=0.01):
        t_id = uuid.uuid4()
        return RunTrace(
            id=t_id, trace_type="feature", feature_name=test_feature,
            prompt_version_id=prompt_id, model_config_id=model_id,
            input_payload={}, error=error, cost_usd=cost, created_at=created_at
        )
    
    t1 = make_trace(now, cost=0.05)
    t2 = make_trace(now, cost=0.05)
    t3 = make_trace(now, error="RateLimitError", cost=0.0)
    t4 = make_trace(yesterday, cost=0.1)
    
    db_session.add_all([t1, t2, t3, t4])
    db_session.commit()
    
    # Add judge scores to successful traces
    db_session.add(JudgeScore(
        id=uuid.uuid4(), run_trace_id=t1.id, judge_version_id=judge_id,
        dimension="factual_accuracy", score=1.0, rationale="good"
    ))
    db_session.add(JudgeScore(
        id=uuid.uuid4(), run_trace_id=t2.id, judge_version_id=judge_id,
        dimension="factual_accuracy", score=0.0, rationale="bad"
    ))
    db_session.commit()
    
    # Add Drift Event
    db_session.add(DriftEvent(
        id=uuid.uuid4(), feature_name=test_feature, metric="test_metric",
        window_start=yesterday, window_end=now, statistic_value=0.5,
        threshold=0.1, severity="critical", sample_size=100
    ))
    db_session.commit()
    
    # 4. Execute Queries
    # Query A: Daily Cost & Error Rate
    sql_daily_stats = text("""
        SELECT 
            DATE(created_at) as day,
            SUM(cost_usd) as total_cost,
            COUNT(*) as total_requests,
            SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) as error_count
        FROM run_traces
        WHERE feature_name = :feat
        GROUP BY DATE(created_at)
        ORDER BY day DESC
    """)
    res = db_session.execute(sql_daily_stats, {"feat": test_feature}).fetchall()
    
    # Evaluate Today
    today_stats = [r for r in res if r.day == now.date()][0]
    assert float(today_stats.total_cost) == 0.10
    assert today_stats.total_requests == 3
    assert today_stats.error_count == 1
    
    # Query B: Average Judge Score Today
    sql_judge_avg = text("""
        SELECT AVG(score) as avg_score
        FROM judge_scores js
        JOIN run_traces rt ON js.run_trace_id = rt.id
        WHERE rt.feature_name = :feat AND DATE(rt.created_at) = :today
    """)
    res_judge = db_session.execute(sql_judge_avg, {"feat": test_feature, "today": now.date()}).fetchone()
    assert float(res_judge.avg_score) == 0.5  # 1.0 and 0.0

    # Query C: Open Drift Events
    sql_drift = text("""
        SELECT COUNT(*) as open_events
        FROM drift_events
        WHERE feature_name = :feat AND acknowledged_at IS NULL
    """)
    res_drift = db_session.execute(sql_drift, {"feat": test_feature}).fetchone()
    assert res_drift.open_events == 1
