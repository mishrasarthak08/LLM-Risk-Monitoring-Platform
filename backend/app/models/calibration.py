"""
VERITAS AI — Judge Calibration & Human Annotation Models
"""
import uuid
import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Numeric, JSON, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, GUID, TimestampMixin


class HumanAnnotation(Base, TimestampMixin):
    __tablename__ = "human_annotations"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    trace_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("traces.id", ondelete="SET NULL"), nullable=True)
    dataset_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("dataset_cases.id", ondelete="SET NULL"), nullable=True)

    annotator_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    dimension: Mapped[str] = mapped_column(String(100), nullable=False)
    human_score: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CalibrationRun(Base, TimestampMixin):
    __tablename__ = "calibration_runs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    evaluator_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("evaluator_versions.id"), index=True)

    status: Mapped[str] = mapped_column(String(50), default="COMPLETED")  # CALIBRATED, FAILED
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_kappa: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dimension_scores: Mapped[List["CalibrationDimensionScore"]] = relationship("CalibrationDimensionScore", back_populates="calibration_run", cascade="all, delete-orphan")


class CalibrationDimensionScore(Base, TimestampMixin):
    __tablename__ = "calibration_dimension_scores"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    calibration_run_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("calibration_runs.id", ondelete="CASCADE"), index=True)

    dimension: Mapped[str] = mapped_column(String(100), nullable=False)
    kappa_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    confusion_matrix: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    calibration_run: Mapped["CalibrationRun"] = relationship("CalibrationRun", back_populates="dimension_scores")

