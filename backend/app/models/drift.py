"""
VERITAS AI — Statistical Drift Detection & Incident Desk Models
"""
import uuid
import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Numeric, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, GUID, TimestampMixin


class DriftReferenceDistribution(Base, TimestampMixin):
    __tablename__ = "drift_reference_distributions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)  # output_length, refusal_rate, judge_score_fa
    distribution_summary: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    window_start: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class DriftEvent(Base, TimestampMixin):
    __tablename__ = "drift_events"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    feature_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    window_start: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)

    test_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PSI, KS_TEST, TWO_PROP_Z
    statistic_value: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    p_value: Mapped[Optional[float]] = mapped_column(Numeric(8, 4), nullable=True)
    severity: Mapped[str] = mapped_column(String(50), default="WARNING")  # CRITICAL, WARNING, INFO

    triage_status: Mapped[str] = mapped_column(String(50), default="OPEN", index=True)
    # OPEN, INVESTIGATING, CONFIRMED_ISSUE, BENIGN_SHIFT, FALSE_POSITIVE, RESOLVED
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    triage_logs: Mapped[List["DriftTriageLog"]] = relationship("DriftTriageLog", back_populates="drift_event", cascade="all, delete-orphan")


class DriftTriageLog(Base, TimestampMixin):
    __tablename__ = "drift_triage_logs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    drift_event_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("drift_events.id", ondelete="CASCADE"), index=True)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    previous_status: Mapped[str] = mapped_column(String(50), nullable=False)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)

    drift_event: Mapped["DriftEvent"] = relationship("DriftEvent", back_populates="triage_logs")
