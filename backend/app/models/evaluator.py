"""
VERITAS AI — Evaluation Engine, Rubrics, Evaluators, and Evaluation Runs
"""
import uuid
import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Numeric, JSON, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, GUID, TimestampMixin


class Rubric(Base, TimestampMixin):
    __tablename__ = "rubrics"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dimensions: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    # [{"name": "factual_accuracy", "scale": [0, 1], "prompt": "...", "type": "binary"}]
    gating_dimensions: Mapped[list[str]] = mapped_column(JSON, default=list)

    __table_args__ = (
        UniqueConstraint("project_id", "slug", name="uq_project_rubric_slug"),
    )


class Evaluator(Base, TimestampMixin):
    __tablename__ = "evaluators"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    evaluator_type: Mapped[str] = mapped_column(String(50), default="llm_judge")  # llm_judge, deterministic, human
    rubric_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("rubrics.id", ondelete="SET NULL"), nullable=True)

    versions: Mapped[List["EvaluatorVersion"]] = relationship("EvaluatorVersion", back_populates="evaluator", cascade="all, delete-orphan")


class EvaluatorVersion(Base, TimestampMixin):
    __tablename__ = "evaluator_versions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    evaluator_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("evaluators.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    model_config_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("model_configs.id", ondelete="SET NULL"), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    calibration_status: Mapped[str] = mapped_column(String(50), default="PENDING")  # CALIBRATED, FAILED, PENDING, STALE
    last_kappa_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    evaluator: Mapped["Evaluator"] = relationship("Evaluator", back_populates="versions")


class EvaluationRun(Base, TimestampMixin):
    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    evaluator_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("evaluator_versions.id"), index=True)
    dataset_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("dataset_versions.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING")  # RUNNING, COMPLETED, FAILED
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0)
    summary_metrics: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    results: Mapped[List["EvaluationResult"]] = relationship("EvaluationResult", back_populates="evaluation_run", cascade="all, delete-orphan")


class EvaluationResult(Base, TimestampMixin):
    __tablename__ = "evaluation_results"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), index=True)
    trace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("traces.id", ondelete="SET NULL"), nullable=True)
    dataset_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("dataset_cases.id", ondelete="SET NULL"), nullable=True)

    dimension: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    max_score: Mapped[float] = mapped_column(Numeric(6, 3), default=1.0)
    is_passing: Mapped[bool] = mapped_column(Boolean, default=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_evaluator_output: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    evaluation_run: Mapped["EvaluationRun"] = relationship("EvaluationRun", back_populates="results")

