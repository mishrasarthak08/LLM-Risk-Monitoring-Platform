"""
VERITAS AI — Regression Suite & CI Gatekeeper Models
"""
import uuid
import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Numeric, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, GUID, TimestampMixin


class GatePolicy(Base, TimestampMixin):
    __tablename__ = "gate_policies"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_blocking_failures: Mapped[int] = mapped_column(Integer, default=0)
    max_major_failures: Mapped[int] = mapped_column(Integer, default=2)  # >= 3 blocks
    p_value_threshold: Mapped[float] = mapped_column(Numeric(4, 3), default=0.05)
    effect_size_threshold: Mapped[float] = mapped_column(Numeric(4, 3), default=0.20)  # Cliff's Delta / Rank-biserial


class RegressionRun(Base, TimestampMixin):
    __tablename__ = "regression_runs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    trigger: Mapped[str] = mapped_column(String(100), default="github_pr")  # github_pr, manual, scheduled

    baseline_prompt_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("prompt_versions.id"), nullable=False)
    candidate_prompt_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("prompt_versions.id"), nullable=False)
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("dataset_versions.id"), nullable=False)
    evaluator_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("evaluator_versions.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="RUNNING")  # RUNNING, COMPLETED, FAILED
    gate_decision: Mapped[str] = mapped_column(String(50), default="PENDING")  # ALLOW, BLOCK, ALLOW_WITH_WARNING
    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    wilcoxon_p_value: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True)
    effect_size: Mapped[Optional[float]] = mapped_column(Numeric(6, 4), nullable=True)

    summary_stats: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ci_run_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True)

    case_results: Mapped[List["RegressionCaseResult"]] = relationship("RegressionCaseResult", back_populates="regression_run", cascade="all, delete-orphan")


class RegressionCaseResult(Base, TimestampMixin):
    __tablename__ = "regression_case_results"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    regression_run_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("regression_runs.id", ondelete="CASCADE"), index=True)
    dataset_case_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("dataset_cases.id"), index=True)

    baseline_trace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("traces.id", ondelete="SET NULL"), nullable=True)
    candidate_trace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("traces.id", ondelete="SET NULL"), nullable=True)

    baseline_score: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    candidate_score: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    delta: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    case_verdict: Mapped[str] = mapped_column(String(50), nullable=False)
    # improved, unchanged, regressed, newly_failing, newly_passing

    regression_run: Mapped["RegressionRun"] = relationship("RegressionRun", back_populates="case_results")
