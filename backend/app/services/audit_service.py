"""
VERITAS AI — Cryptographic Audit Trail & Hash-Chain Service
Guarantees non-repudiation and detects historical tampering.
"""
import json
import hashlib
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.audit import AuditEvent
from backend.app.core.security import compute_sha256

GENESIS_HASH = "0" * 64


def record_audit_event(
    db: Session,
    project_id: uuid.UUID,
    actor_email: str,
    event_type: str,
    payload: Dict[str, Any]
) -> AuditEvent:
    """
    Appends a new audit record cryptographically linked to the previous record's hash.
    Hash_n = SHA-256(Hash_{n-1} + event_type + payload_json + sequence_number)
    """
    last_event = db.query(AuditEvent).filter(
        AuditEvent.project_id == project_id
    ).order_by(desc(AuditEvent.sequence_number)).first()

    if last_event:
        prev_hash = last_event.record_hash
        seq_num = last_event.sequence_number + 1
    else:
        prev_hash = GENESIS_HASH
        seq_num = 1

    payload_str = json.dumps(payload, sort_keys=True, default=str)
    hash_preimage = f"{prev_hash}:{event_type}:{payload_str}:{seq_num}"
    record_hash = hashlib.sha256(hash_preimage.encode("utf-8")).hexdigest()

    event = AuditEvent(
        id=uuid.uuid4(),
        project_id=project_id,
        sequence_number=seq_num,
        actor_email=actor_email,
        event_type=event_type,
        payload_json=payload,
        previous_hash=prev_hash,
        record_hash=record_hash
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def verify_audit_chain(db: Session, project_id: uuid.UUID) -> Dict[str, Any]:
    """
    Cryptographically verifies the integrity of the audit chain from genesis to head.
    Returns whether the chain is unbroken and identifies any tampered record.
    """
    events = db.query(AuditEvent).filter(
        AuditEvent.project_id == project_id
    ).order_by(AuditEvent.sequence_number.asc()).all()

    if not events:
        return {
            "is_valid": True,
            "total_records": 0,
            "broken_sequence": None,
            "tampered_record_id": None,
            "message": "Audit ledger is clean (no records)."
        }

    expected_prev_hash = GENESIS_HASH

    for idx, event in enumerate(events, start=1):
        # 1. Verify sequence number continuity
        if event.sequence_number != idx:
            return {
                "is_valid": False,
                "total_records": len(events),
                "broken_sequence": event.sequence_number,
                "tampered_record_id": str(event.id),
                "message": f"Sequence break: expected {idx}, found {event.sequence_number}."
            }

        # 2. Verify previous hash pointer
        if event.previous_hash != expected_prev_hash:
            return {
                "is_valid": False,
                "total_records": len(events),
                "broken_sequence": event.sequence_number,
                "tampered_record_id": str(event.id),
                "message": f"Hash chain broken at record {idx}. Previous hash does not match."
            }

        # 3. Recompute record hash
        payload_str = json.dumps(event.payload_json, sort_keys=True)
        hash_preimage = f"{event.previous_hash}:{event.event_type}:{payload_str}:{event.sequence_number}"
        recalculated_hash = hashlib.sha256(hash_preimage.encode("utf-8")).hexdigest()

        if recalculated_hash != event.record_hash:
            return {
                "is_valid": False,
                "total_records": len(events),
                "broken_sequence": event.sequence_number,
                "tampered_record_id": str(event.id),
                "message": f"Payload tampering detected at record {idx}. Hash mismatch."
            }

        expected_prev_hash = event.record_hash

    return {
        "is_valid": True,
        "total_records": len(events),
        "head_hash": expected_prev_hash,
        "message": f"Cryptographic integrity verified across {len(events)} immutable audit records."
    }

