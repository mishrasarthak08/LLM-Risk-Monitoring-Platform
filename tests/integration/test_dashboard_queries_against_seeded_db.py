import os
import uuid
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.app.models.tenant import Organization, Project
from backend.app.models.trace import Trace, Span
from backend.app.models.drift import DriftEvent

@pytest.fixture(scope="module")
def db_session():
    db_url = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://localhost:5432/veritas_ai_dev"
    )
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_dashboard_aggregations(db_session):
    """
    Seeds the database with traces and drift incidents.
    Executes standard 'dashboard' queries against the modern schema and asserts the aggregations are correct.
    """
    # 1. Setup tenant & project
    org = Organization(id=uuid.uuid4(), name="Dashboard Test Org", slug=f"dash-org-{uuid.uuid4().hex[:6]}")
    db_session.add(org)
    db_session.commit()

    project = Project(id=uuid.uuid4(), organization_id=org.id, name="Dashboard Test Project", slug="dash-proj")
    db_session.add(project)
    db_session.commit()

    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    # 2. Seed modern Traces (Today: 2 success, 1 error; Yesterday: 1 success)
    def make_trace(created_at, status="SUCCESS", error=None, cost=0.01):
        return Trace(
            id=uuid.uuid4(),
            project_id=project.id,
            trace_type="production",
            feature_name="dashboard_test_feature",
            input_payload={"prompt": "Test prompt"},
            output_text="Test response",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cost_usd=cost,
            latency_ms=250,
            status=status,
            error_message=error,
            created_at=created_at
        )

    t1 = make_trace(now, cost=0.05)
    t2 = make_trace(now, cost=0.05)
    t3 = make_trace(now, status="ERROR", error="RateLimitError", cost=0.0)
    t4 = make_trace(yesterday, cost=0.10)

    db_session.add_all([t1, t2, t3, t4])
    db_session.commit()

    # 3. Seed Drift Event
    event = DriftEvent(
        id=uuid.uuid4(),
        project_id=project.id,
        feature_name="dashboard_test_feature",
        metric_name="output_length_ks",
        test_type="KS_TEST",
        statistic_value=0.012,
        threshold=0.05,
        p_value=0.012,
        severity="WARNING",
        triage_status="OPEN",
        window_start=yesterday,
        window_end=now,
        sample_size=100
    )
    db_session.add(event)
    db_session.commit()

    # 4. Execute Dashboard Queries
    sql_daily_stats = text("""
        SELECT 
            DATE(created_at) as day,
            SUM(cost_usd) as total_cost,
            COUNT(*) as total_requests,
            SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) as error_count
        FROM traces
        WHERE project_id = :proj_id
        GROUP BY DATE(created_at)
        ORDER BY day DESC
    """)
    res = db_session.execute(sql_daily_stats, {"proj_id": project.id}).fetchall()

    today_stats = [r for r in res if r.day == now.date()][0]
    assert float(today_stats.total_cost) == 0.10
    assert today_stats.total_requests == 3
    assert today_stats.error_count == 1

    # Query B: Open Drift Events
    sql_drift = text("""
        SELECT COUNT(*) as open_events
        FROM drift_events
        WHERE project_id = :proj_id AND triage_status = 'OPEN'
    """)
    res_drift = db_session.execute(sql_drift, {"proj_id": project.id}).fetchone()
    assert res_drift.open_events == 1

    # Clean up test tenant
    db_session.query(Trace).filter_by(project_id=project.id).delete()
    db_session.query(DriftEvent).filter_by(project_id=project.id).delete()
    db_session.query(Project).filter_by(id=project.id).delete()
    db_session.query(Organization).filter_by(id=org.id).delete()
    db_session.commit()
