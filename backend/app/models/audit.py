"""
VERITAS AI — Cryptographic Audit Trail & Governance Evidence Models
"""
import uuid
import datetime
from typing import Optional, Any
from sqlalchemy import String, Text, BigInteger, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.models.base import Base, GUID, TimestampMixin


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    sequence_number: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    # PROMPT_VERSION_CREATED, PROMPT_PUBLISHED, DATASET_VERSION_APPROVED,
    # REGRESSION_GATE_EXECUTED, GATE_DECISION_OVERRIDE, DRIFT_EVENT_TRIAGED,
    # CALIBRATION_CERTIFIED, CONFIG_MODIFIED

    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    record_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    __table_args__ = (
        Index("ix_audit_project_seq", "project_id", "sequence_number", unique=True),
    )

