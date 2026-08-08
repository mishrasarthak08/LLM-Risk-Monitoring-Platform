import os
import time
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.feature.credit_memo import generate_credit_memo
from monitoring.db.models import RunTrace

# Ensure we use the test database
os.environ["DATABASE_URL"] = "postgresql+psycopg2://dev_user:dev_password@127.0.0.1:5435/llm_monitoring_dev"


from dotenv import load_dotenv
load_dotenv()

@patch("app.feature.credit_memo.call_llm")
def test_full_trace_lifecycle(mock_call_llm):
    """
    Call generate_credit_memo() and assert a matching row lands in run_traces,
    with a non-null cost_usd and correct parent_span_id linkage.
    """
    # Setup mock returns to avoid real LLM calls and rate limits
    mock_call_llm.return_value = ("Mocked credit memo content of sufficient length", {"total_tokens": 150})


    # Ensure traces queue is drained before test by waiting a bit if needed
    time.sleep(0.5)

    engine = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)

    # Call the top-level feature
    output = generate_credit_memo(
        prompt_template="Test prompt for integration test",
        input_payload={"revenue": 1000},
        model_config={"model_name": "gemini-2.5-flash"}
    )
    
    assert isinstance(output, str)
    assert len(output) > 10

    # Wait for the async writer to flush
    time.sleep(1.5)

    with Session() as session:
        # Check that traces were inserted
        traces = session.query(RunTrace).order_by(RunTrace.created_at.desc()).limit(20).all()

        # Identify the outer trace (parent_span_id is None) for credit_memo_drafting
        outer_trace = next((t for t in traces if t.parent_span_id is None and t.feature_name == "credit_memo_drafting"), None)
        assert outer_trace is not None
        assert outer_trace.feature_name == "credit_memo_drafting"
        
        # Identify child traces
        child_traces = [t for t in traces if t.parent_span_id == outer_trace.id]
        assert len(child_traces) == 3
        
        # Verify cost and usage were populated
        for trace in child_traces:
            assert (trace.input_tokens or 0) + (trace.output_tokens or 0) > 0
            assert trace.cost_usd > 0.0
