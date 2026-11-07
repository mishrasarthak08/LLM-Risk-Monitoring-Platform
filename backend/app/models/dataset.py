"""
VERITAS AI — Benchmark & Golden Dataset Models
"""
import uuid
import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, JSON, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, GUID, TimestampMixin


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), nullable=True)

    versions: Mapped[List["DatasetVersion"]] = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project_id", "slug", name="uq_project_dataset_slug"),
    )


class DatasetVersion(Base, TimestampMixin):
    __tablename__ = "dataset_versions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("datasets.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    change_summary: Mapped[str] = mapped_column(Text, nullable=False)
    approved_by: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="versions")
    cases: Mapped[List["DatasetCase"]] = relationship("DatasetCase", back_populates="dataset_version", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("dataset_id", "version_number", name="uq_dataset_version_number"),
    )


class DatasetCase(Base, TimestampMixin):
    __tablename__ = "dataset_cases"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("dataset_versions.id", ondelete="CASCADE"), index=True)
    case_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # happy_path, edge_case, adversarial, known_failure
    severity: Mapped[str] = mapped_column(String(50), default="major")  # blocking, major, minor
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    expected_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_criteria: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)  # must_mention, must_not, numeric_bounds
    tags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="synthetic_benchmark")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    dataset_version: Mapped["DatasetVersion"] = relationship("DatasetVersion", back_populates="cases")

