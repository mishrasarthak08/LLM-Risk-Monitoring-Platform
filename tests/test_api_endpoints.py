"""
VERITAS AI — Test Suite: FastAPI REST Endpoints
Tests health check, project endpoints, trace ingestion, prompt versioning, regression, drift, and audit verification.
"""
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["platform"] == "VERITAS AI"


def test_projects_list_and_create():
    # 1. List projects
    res = client.get("/api/v1/projects")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) >= 1

    # 2. Create project
    slug = f"test-project-{uuid.uuid4().hex[:6]}"
    create_res = client.post("/api/v1/projects", json={
        "name": "Integration Test Project",
        "slug": slug,
        "description": "Created during pytest execution"
    })
    assert create_res.status_code == 200
    proj_data = create_res.json()
    assert proj_data["slug"] == slug


def test_trace_ingestion_and_retrieval():
    payload = {
        "feature_name": "credit_memo_v1",
        "input_payload": {"revenue": 500000, "debt_service": 80000, "ssn": "123-45-6789"},
        "output_text": "Approved underwriting credit memorandum for review.",
        "input_tokens": 150,
        "output_tokens": 90,
        "latency_ms": 750,
        "status": "SUCCESS"
    }

    # Ingest trace
    res = client.post("/api/v1/traces/ingest", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["feature_name"] == "credit_memo_v1"
    assert data["cost_usd"] > 0
    # SSN must be redacted by redactor
    assert data["input_payload"]["ssn"] == "[REDACTED_SSN]"

    # Retrieve trace by ID
    trace_id = data["id"]
    get_res = client.get(f"/api/v1/traces/{trace_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == trace_id


def test_audit_verification_endpoint():
    res = client.get("/api/v1/audit/verify")
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert "Cryptographic integrity verified" in data["message"]


def test_governance_report_generation():
    res = client.get("/api/v1/reports/governance-package")
    assert res.status_code == 200
    dossier = res.json()
    assert "metadata" in dossier
    assert "audit_chain_verification" in dossier
    assert dossier["audit_chain_verification"]["is_valid"] is True
    assert "prompt_inventory" in dossier
    assert "dataset_inventory" in dossier
    assert "regression_testing_evidence" in dossier
    assert "continuous_drift_evidence" in dossier


def test_regressions_csv_export():
    res = client.get("/api/v1/reports/regressions-csv")
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/csv; charset=utf-8"
    assert "run_id,created_at" in res.text

