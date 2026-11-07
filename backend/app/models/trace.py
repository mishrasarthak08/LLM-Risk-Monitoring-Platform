"""
VERITAS AI — AI Observability, Traces and Nested Spans Models
"""
import uuid
import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Numeric, JSON, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, GUID, TimestampMixin


class Trace(Base, TimestampMixin):
    __tablename__ = "traces"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    feature_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    trace_type: Mapped[str] = mapped_column(String(50), default="production", index=True)  # production, regression, evaluation, manual

    prompt_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("prompt_versions.id", ondelete="SET NULL"), nullable=True)
    model_config_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("model_configs.id", ondelete="SET NULL"), nullable=True)

    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Numeric(12, 6), default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(50), default="SUCCESS", index=True)  # SUCCESS, ERROR, REFUSAL
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    spans: Mapped[List["Span"]] = relationship("Span", back_populates="trace", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_traces_project_created", "project_id", "created_at"),
        Index("ix_traces_feature_created", "feature_name", "created_at"),
    )


class Span(Base, TimestampMixin):
    __tablename__ = "spans"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("traces.id", ondelete="CASCADE"), index=True)
    parent_span_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    span_type: Mapped[str] = mapped_column(String(50), default="llm_call")  # llm_call, retrieval, guardrail, tool
    input_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    output_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    trace: Mapped["Trace"] = relationship("Trace", back_populates="spans")

