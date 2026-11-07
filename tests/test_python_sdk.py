"""
VERITAS AI — Test Suite: Python SDK End-to-End Tracing & Ingestion
"""
import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

# Add SDK path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../sdk/python")))

from veritas import Veritas, VeritasConfigurationError
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.tenant import Project, APIKey, Organization
from backend.app.core.security import generate_api_key

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_sdk_project():
    db = SessionLocal()
    org = db.query(Organization).first()
    if not org:
        org = Organization(id=uuid.uuid4(), name="SDK Test Org", slug="sdk-test-org")
        db.add(org)
        db.commit()

    proj = Project(
        id=uuid.uuid4(),
        organization_id=org.id,
        name="SDK Integration Project",
        slug=f"sdk-proj-{uuid.uuid4().hex[:6]}",
        description="Created for Python SDK end-to-end verification"
    )
    db.add(proj)
    db.commit()

    raw_key, prefix, hashed = generate_api_key()
    api_key_obj = APIKey(
        id=uuid.uuid4(),
        project_id=proj.id,
        name="SDK Test Key",
        key_prefix=prefix,
        hashed_key=hashed,
        is_active=True
    )
    db.add(api_key_obj)
    db.commit()

    db_key = raw_key
    yield proj, db_key
    db.close()


def test_veritas_sdk_configuration():
    # Missing API key must raise VeritasConfigurationError
    with pytest.raises(VeritasConfigurationError):
        Veritas(api_key="")


def test_veritas_sdk_trace_context(setup_sdk_project):
    proj, raw_key = setup_sdk_project

    # Create SDK client in synchronous delivery mode
    v_client = Veritas(
        api_key=raw_key,
        base_url="http://testserver/api/v1",
        sync_mode=True
    )

    # Mock the internal urllib request with FastAPI TestClient
    def mock_deliver(payload):
        res = client.post(
            "/api/v1/traces/ingest",
            json=payload,
            headers={"X-API-Key": raw_key}
        )
        assert res.status_code == 200
        return True

    v_client._deliver_with_retry = mock_deliver

    feature = "customer_refund_agent"
    with v_client.trace(name=feature, model_name="gpt-4o") as t:
        t.log_input({
            "customer_id": "cust_123",
            "query": "Please process refund for SSN: 987-65-4321.",
            "card": "4111-2222-3333-4444"
        })

        with t.span("database_lookup", span_type="db_query") as s:
            s.log_input({"table": "orders", "id": 55})
            s.log_output({"status": "eligible"})

        t.log_output("Refund of $50 approved under store policy.")
        t.log_tokens(input_tokens=85, output_tokens=32)

    # Verify captured trace in backend via GET /traces
    res = client.get(
        f"/api/v1/traces?feature={feature}",
        headers={"X-API-Key": raw_key}
    )
    assert res.status_code == 200
    traces = res.json()
    assert len(traces) >= 1
    latest = traces[0]

    assert latest["feature_name"] == feature
    assert latest["status"] == "SUCCESS"
    assert latest["input_tokens"] == 85
    assert latest["output_tokens"] == 32
    assert latest["latency_ms"] >= 1
    # Verify client-side PII redaction
    assert latest["input_payload"]["query"] == "Please process refund for SSN: [REDACTED_SSN]."
    assert latest["input_payload"]["card"] == "[REDACTED_CARD]"


def test_veritas_sdk_decorator(setup_sdk_project):
    proj, raw_key = setup_sdk_project

    v_client = Veritas(
        api_key=raw_key,
        base_url="http://testserver/api/v1",
        sync_mode=True
    )

    def mock_deliver(payload):
        res = client.post(
            "/api/v1/traces/ingest",
            json=payload,
            headers={"X-API-Key": raw_key}
        )
        assert res.status_code == 200
        return True

    v_client._deliver_with_retry = mock_deliver

    @v_client.traced(feature_name="automated_summarizer")
    def summarize_article(text: str) -> str:
        return f"Summary of: {text[:20]}..."

    result = summarize_article("Annual Financial Review for Corporate Lending Covenants.")
    assert "Summary of:" in result

