import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from monitoring.db.models import Base, RunTrace, DriftEvent, JudgeVersion, ModelConfig, PromptVersion

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("Please export DATABASE_URL")
    exit(1)

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

print("Populating database with mock data for dashboard visualization...")

import uuid
# Add a Model Config
config_id = uuid.uuid4()
config = ModelConfig(
    id=config_id,
    provider="google",
    model_name="gemini-2.5-flash",
    content_hash="mock_hash_1"
)
session.add(config)

# Add a Prompt Version
prompt_id = uuid.uuid4()
prompt = PromptVersion(
    id=prompt_id,
    feature_name="credit_memo_v1",
    content_hash="mock_hash_2",
    prompt_text="You are a helpful assistant.",
    version_label="v1",
    created_by="system"
)
session.add(prompt)
session.commit()

# Add a Judge Calibration
judge_id = uuid.uuid4()
judge = JudgeVersion(
    id=judge_id,
    rubric_content_hash="mock_hash_3",
    rubric_text="Evaluate this.",
    judge_model_config_id=config_id,
    calibration_status="calibrated",
    last_kappa_score=0.85,
    created_at=datetime.now(timezone.utc)
)
session.add(judge)

# Add some Drift Events
for i in range(3):
    event = DriftEvent(
        id=uuid.uuid4(),
        feature_name="credit_memo_v1",
        metric="compliance_score",
        window_start=datetime.now(timezone.utc) - timedelta(days=i),
        window_end=datetime.now(timezone.utc) - timedelta(days=i-1),
        statistic_value=0.04,
        threshold=0.05,
        sample_size=100,
        severity="medium" if i % 2 == 0 else "high"
    )
    session.add(event)

# Add some Run Traces
for i in range(20):
    trace = RunTrace(
        id=uuid.uuid4(),
        trace_type="inference",
        feature_name="credit_memo_v1",
        prompt_version_id=prompt_id,
        model_config_id=config_id,
        input_payload={"revenue": 1000 + i * 100},
        output_text="status: approved",
        latency_ms=1200 + i * 15,
        cost_usd=0.002,
        input_tokens=50,
        output_tokens=100,
        created_at=datetime.now(timezone.utc) - timedelta(hours=i)
    )
    session.add(trace)

session.commit()
print("Mock data inserted successfully! Your dashboard should now be populated.")
