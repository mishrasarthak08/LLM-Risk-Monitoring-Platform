"""
VERITAS AI — Prompt Registry & Version Control Models
"""
import uuid
import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Text, Integer, Numeric, JSON, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, GUID, TimestampMixin


class ModelConfig(Base, TimestampMixin):
    __tablename__ = "model_configs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # gemini, openai, anthropic, simulated
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    temperature: Mapped[float] = mapped_column(Numeric(4, 2), default=0.0)
    max_tokens: Mapped[int] = mapped_column(Integer, default=1024)
    other_params: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)


class Prompt(Base, TimestampMixin):
    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), nullable=True)

    versions: Mapped[List["PromptVersion"]] = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project_id", "slug", name="uq_project_prompt_slug"),
    )


class PromptVersion(Base, TimestampMixin):
    __tablename__ = "prompt_versions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    prompt_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("prompts.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "v1.0.0"
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    template_variables: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    system_instruction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    git_commit_sha: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("prompt_id", "version_number", name="uq_prompt_version_number"),
    )

