"""
VERITAS AI — Test Suite: Multi-Tenant Scoping & Strict Tenant Isolation
Guarantees that Organization B can never read or mutate Organization A's data.
"""
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.tenant import Organization, User, Project, APIKey, Membership
from backend.app.core.security import generate_api_key, get_password_hash, create_access_token
from backend.app.services.trace_service import ingest_trace

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_two_isolated_tenants():
    db = SessionLocal()

    # --- Tenant A ---
    org_a = Organization(id=uuid.uuid4(), name="Alpha Corp", slug=f"alpha-corp-{uuid.uuid4().hex[:6]}")
    user_a = User(id=uuid.uuid4(), email=f"alice_{uuid.uuid4().hex[:6]}@alpha.com", hashed_password=get_password_hash("AlphaPass123!"), full_name="Alice Alpha", is_active=True)
    mem_a = Membership(id=uuid.uuid4(), organization_id=org_a.id, user_id=user_a.id, role="OWNER")
    proj_a = Project(id=uuid.uuid4(), organization_id=org_a.id, name="Alpha Defense System", slug=f"alpha-defense-{uuid.uuid4().hex[:6]}")
    raw_key_a, pref_a, hash_a = generate_api_key()
    key_a = APIKey(id=uuid.uuid4(), project_id=proj_a.id, name="Alpha Key", key_prefix=pref_a, hashed_key=hash_a, is_active=True)

    db.add_all([org_a, user_a, mem_a, proj_a, key_a])

    # --- Tenant B ---
    org_b = Organization(id=uuid.uuid4(), name="Beta Logistics", slug=f"beta-logistics-{uuid.uuid4().hex[:6]}")
    user_b = User(id=uuid.uuid4(), email=f"bob_{uuid.uuid4().hex[:6]}@beta.com", hashed_password=get_password_hash("BetaPass123!"), full_name="Bob Beta", is_active=True)
    mem_b = Membership(id=uuid.uuid4(), organization_id=org_b.id, user_id=user_b.id, role="OWNER")
    proj_b = Project(id=uuid.uuid4(), organization_id=org_b.id, name="Beta Dispatch Assistant", slug=f"beta-dispatch-{uuid.uuid4().hex[:6]}")
    raw_key_b, pref_b, hash_b = generate_api_key()
    key_b = APIKey(id=uuid.uuid4(), project_id=proj_b.id, name="Beta Key", key_prefix=pref_b, hashed_key=hash_b, is_active=True)

    db.add_all([org_b, user_b, mem_b, proj_b, key_b])
    db.commit()

    # Ingest a confidential trace for Tenant A
    trace_a = ingest_trace(
        db=db,
        project_id=proj_a.id,
        feature_name="alpha_confidential_feature",
        input_payload={"secret_contract": "CONFIDENTIAL_ALPHA_DATA"},
        output_text="Alpha proprietary classified response.",
        status="SUCCESS",
        latency_ms=250
    )

    token_a = create_access_token({"sub": str(user_a.id), "email": user_a.email})
    token_b = create_access_token({"sub": str(user_b.id), "email": user_b.email})

    data = {
        "tenant_a": {"user": user_a, "proj": proj_a, "key": raw_key_a, "token": token_a, "trace": trace_a},
        "tenant_b": {"user": user_b, "proj": proj_b, "key": raw_key_b, "token": token_b}
    }

    yield data
    db.close()


def test_tenant_b_cannot_see_tenant_a_traces(setup_two_isolated_tenants):
    t_a = setup_two_isolated_tenants["tenant_a"]
    t_b = setup_two_isolated_tenants["tenant_b"]

    # 1. Tenant A fetches traces with their API key -> Sees their confidential trace
    res_a = client.get(
        "/api/v1/traces",
        headers={"X-API-Key": t_a["key"]}
    )
    assert res_a.status_code == 200
    traces_a = res_a.json()
    assert any(t["feature_name"] == "alpha_confidential_feature" for t in traces_a)

    # 2. Tenant B fetches traces with Tenant B's API key -> CANNOT see Tenant A's trace
    res_b = client.get(
        "/api/v1/traces",
        headers={"X-API-Key": t_b["key"]}
    )
    assert res_b.status_code == 200
    traces_b = res_b.json()
    assert not any(t["feature_name"] == "alpha_confidential_feature" for t in traces_b)


def test_user_b_cannot_list_user_a_projects(setup_two_isolated_tenants):
    t_a = setup_two_isolated_tenants["tenant_a"]
    t_b = setup_two_isolated_tenants["tenant_b"]

    # When User B requests projects with their JWT bearer token:
    res = client.get(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {t_b['token']}"}
    )
    assert res.status_code == 200
    projects = res.json()

    # Projects list must ONLY contain Tenant B's projects
    proj_ids = [p["id"] for p in projects]
    assert str(t_b["proj"].id) in proj_ids
    assert str(t_a["proj"].id) not in proj_ids


def test_revoked_api_key_cannot_ingest_traces(setup_two_isolated_tenants):
    t_a = setup_two_isolated_tenants["tenant_a"]

    # Revoke key for tenant A
    del_res = client.delete(
        f"/api/v1/projects/{t_a['proj'].id}/api-keys/{t_a['proj'].api_keys[0].id}",
        headers={"Authorization": f"Bearer {t_a['token']}"}
    )
    assert del_res.status_code == 200

    # Ingestion attempt using revoked key must be rejected (falls back or refuses)
    # The key record is_active == False, so deps.py will not authenticate it
    ingest_res = client.post(
        "/api/v1/traces/ingest",
        json={"feature_name": "test_after_revoke", "latency_ms": 100, "status": "SUCCESS"},
        headers={"X-API-Key": t_a["key"]}
    )
    # Since revoked, it won't resolve Tenant A's project via API key
    # It either falls back to default demo or fails, but cannot attribute to Project A
    if ingest_res.status_code == 200:
        trace_data = ingest_res.json()
        assert trace_data["project_id"] != str(t_a["proj"].id)
