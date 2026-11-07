import os
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.tenant import Organization, Project
from backend.app.models.trace import Trace, Span
from backend.app.services.trace_service import ingest_trace


def test_full_trace_lifecycle():
    """
    Test the complete trace lifecycle:
    Ingest a trace with nested spans, assert matching row lands in traces,
    with non-null cost_usd, auto-calculated tokens, and correctly linked child spans.
    """
    db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://localhost:5432/veritas_ai_dev")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # 1. Setup tenant & project
        org = Organization(id=uuid.uuid4(), name="Lifecycle Test Org", slug=f"lc-org-{uuid.uuid4().hex[:6]}")
        session.add(org)
        session.commit()

        project = Project(id=uuid.uuid4(), organization_id=org.id, name="Lifecycle Test Project", slug="lc-proj")
        session.add(project)
        session.commit()

        # 2. Ingest trace with 3 nested spans
        spans_data = [
            {"name": "retrieval_agent", "span_type": "retrieval", "latency_ms": 120, "tokens": 80},
            {"name": "financial_calculator", "span_type": "tool", "latency_ms": 45, "tokens": 0},
            {"name": "credit_memo_generation", "span_type": "llm", "latency_ms": 480, "tokens": 220}
        ]

        trace = ingest_trace(
            db=session,
            project_id=project.id,
            feature_name="credit_memo_drafting",
            input_payload={"borrower": "Acme Corp", "revenue": 10000000},
            output_text="Credit memo drafted successfully for Acme Corp.",
            trace_type="production",
            model_name="gemini-1.5-flash",
            input_tokens=150,
            output_tokens=150,
            latency_ms=645,
            status="SUCCESS",
            spans_data=spans_data
        )

        assert trace is not None
        assert trace.id is not None
        assert trace.feature_name == "credit_memo_drafting"
        assert trace.total_tokens == 300
        assert float(trace.cost_usd) > 0.0

        # 3. Query DB to verify parent Trace and child Spans
        persisted_trace = session.query(Trace).filter_by(id=trace.id).first()
        assert persisted_trace is not None
        assert persisted_trace.cost_usd > 0.0

        # Child spans verification
        child_spans = session.query(Span).filter_by(trace_id=trace.id).all()
        assert len(child_spans) == 3
        span_names = [s.name for s in child_spans]
        assert "retrieval_agent" in span_names
        assert "financial_calculator" in span_names
        assert "credit_memo_generation" in span_names

        # Cleanup
        session.query(Span).filter_by(trace_id=trace.id).delete()
        session.query(Trace).filter_by(id=trace.id).delete()
        session.query(Project).filter_by(id=project.id).delete()
        session.query(Organization).filter_by(id=org.id).delete()
        session.commit()
