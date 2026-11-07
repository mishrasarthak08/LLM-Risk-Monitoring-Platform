"""
VERITAS AI — Test Suite: Cryptographic Audit Ledger & Tamper Detection
"""
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.audit import AuditEvent
from backend.app.services.audit_service import record_audit_event, verify_audit_chain, GENESIS_HASH


@pytest.fixture
def db_session():
    # In-memory SQLite database for isolated unit testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_audit_hash_chain_creation_and_verification(db_session):
    project_id = uuid.uuid4()
    actor = "auditor@bank.com"

    # 1. Empty chain check
    empty_res = verify_audit_chain(db_session, project_id)
    assert empty_res["is_valid"] is True
    assert empty_res["total_records"] == 0

    # 2. Add sequence of events
    e1 = record_audit_event(db_session, project_id, actor, "PROMPT_CREATED", {"name": "prompt_v1"})
    assert e1.sequence_number == 1
    assert e1.previous_hash == GENESIS_HASH
    assert len(e1.record_hash) == 64

    e2 = record_audit_event(db_session, project_id, actor, "DATASET_APPROVED", {"cases": 25})
    assert e2.sequence_number == 2
    assert e2.previous_hash == e1.record_hash

    e3 = record_audit_event(db_session, project_id, actor, "REGRESSION_GATE_EVALUATED", {"decision": "BLOCK"})
    assert e3.sequence_number == 3
    assert e3.previous_hash == e2.record_hash

    # 3. Verify intact chain
    verification = verify_audit_chain(db_session, project_id)
    assert verification["is_valid"] is True
    assert verification["total_records"] == 3
    assert verification["head_hash"] == e3.record_hash


def test_tamper_detection_on_altered_payload(db_session):
    project_id = uuid.uuid4()
    actor = "auditor@bank.com"

    record_audit_event(db_session, project_id, actor, "EVENT_1", {"amount": 1000})
    e2 = record_audit_event(db_session, project_id, actor, "EVENT_2", {"amount": 2000})
    record_audit_event(db_session, project_id, actor, "EVENT_3", {"amount": 3000})

    # Legitimate chain is valid
    assert verify_audit_chain(db_session, project_id)["is_valid"] is True

    # Malicious actor tampers with event 2 payload directly in DB
    e2.payload_json = {"amount": 9999999}  # altered!
    db_session.commit()

    # Tampering must be detected
    tamper_res = verify_audit_chain(db_session, project_id)
    assert tamper_res["is_valid"] is False
    assert tamper_res["broken_sequence"] == 2
    assert "tampering detected" in tamper_res["message"].lower()

