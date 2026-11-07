import os
import uuid
import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.tenant import Organization, Project
from backend.app.models.trace import Trace
from backend.app.models.drift import DriftReferenceDistribution, DriftEvent
from backend.app.services.drift_service import evaluate_production_drift


def test_drift_scheduler_writes_events():
    """
    Asserts that if the current window diverges from the reference distribution,
    evaluate_production_drift correctly calculates drift and writes a DriftEvent row.
    """
    db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://localhost:5432/veritas_ai_dev")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Setup org & project
        org = Organization(id=uuid.uuid4(), name="Drift Test Org", slug=f"drift-org-{uuid.uuid4().hex[:6]}")
        session.add(org)
        session.commit()

        project = Project(id=uuid.uuid4(), organization_id=org.id, name="Drift Test Project", slug="drift-proj")
        session.add(project)
        session.commit()

        feature_name = "test_credit_memo"
        now = datetime.datetime.now(datetime.timezone.utc)

        # 1. Seed Reference Distribution with long texts (1000-1100 chars)
        ref_dist = DriftReferenceDistribution(
            id=uuid.uuid4(),
            project_id=project.id,
            feature_name=feature_name,
            metric_name="output_length",
            distribution_summary={"values": [1000, 1050, 1100, 950, 1020] * 5},
            window_start=now - datetime.timedelta(days=7),
            window_end=now - datetime.timedelta(days=1),
            sample_size=25,
            is_active=True
        )
        session.add(ref_dist)
        session.commit()

        # 2. Seed Current Traffic with very short texts (10-15 chars, >= 20 traces)
        traces = [
            Trace(
                id=uuid.uuid4(),
                project_id=project.id,
                feature_name=feature_name,
                trace_type="production",
                input_payload={"test": i},
                output_text="Short output",
                status="SUCCESS",
                created_at=now - datetime.timedelta(minutes=i * 5)
            )
            for i in range(25)
        ]
        session.add_all(traces)
        session.commit()

        # 3. Execute Drift Evaluation
        events = evaluate_production_drift(
            db=session,
            project_id=project.id,
            feature_name=feature_name,
            rolling_hours=24
        )

        assert len(events) >= 1
        length_event = next((e for e in events if e.metric_name == "output_length"), None)
        assert length_event is not None
        assert length_event.test_type == "KS_TEST"
        assert length_event.p_value < 0.05
        assert length_event.triage_status == "OPEN"

        # Verify persisted in database
        saved_events = session.query(DriftEvent).filter_by(project_id=project.id).all()
        assert len(saved_events) >= 1

        # Cleanup
        session.query(Trace).filter_by(project_id=project.id).delete()
        session.query(DriftEvent).filter_by(project_id=project.id).delete()
        session.query(DriftReferenceDistribution).filter_by(project_id=project.id).delete()
        session.query(Project).filter_by(id=project.id).delete()
        session.query(Organization).filter_by(id=org.id).delete()
        session.commit()
