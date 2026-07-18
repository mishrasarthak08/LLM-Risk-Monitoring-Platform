import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import JSON, ARRAY, Numeric, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
# We use string type mapping for postgres-specific TSTZRANGE
from sqlalchemy.dialects.postgresql import TSTZRANGE


class Base(DeclarativeBase):
    pass


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(Text)
    prompt_text: Mapped[str] = mapped_column(Text)
    version_label: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[str] = mapped_column(Text)
    git_commit_sha: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(Text)
    temperature: Mapped[Optional[float]] = mapped_column(
        Numeric, nullable=True)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    other_params: Mapped[Optional[dict[str, Any]]
                         ] = mapped_column(JSON, nullable=True)
    content_hash: Mapped[str] = mapped_column(Text)


class GoldenSetVersion(Base):
    __tablename__ = "golden_set_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    version_number: Mapped[int] = mapped_column(Integer)
    feature_name: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(Text)
    case_count: Mapped[int] = mapped_column(Integer)
    storage_uri: Mapped[str] = mapped_column(Text)
    change_summary: Mapped[str] = mapped_column(Text)
    approved_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class GoldenSetCase(Base):
    __tablename__ = "golden_set_cases"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    golden_set_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("golden_set_versions.id"))
    case_hash: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    expected_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_criteria: Mapped[Optional[dict[str, Any]]
                              ] = mapped_column(JSON, nullable=True)
    severity: Mapped[str] = mapped_column(Text)
    tags: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text), nullable=True)
    source: Mapped[str] = mapped_column(Text)
    added_by: Mapped[str] = mapped_column(Text)
    added_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    notes: Mapped[str] = mapped_column(Text)


class RunTrace(Base):
    __tablename__ = "run_traces"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    trace_type: Mapped[str] = mapped_column(Text)
    feature_name: Mapped[str] = mapped_column(Text)
    prompt_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_versions.id"))
    model_config_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_configs.id"))
    golden_set_version_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("golden_set_versions.id"), nullable=True)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    output_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)
    cost_usd: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 6), nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_span_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class JudgeVersion(Base):
    __tablename__ = "judge_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    rubric_content_hash: Mapped[str] = mapped_column(Text)
    rubric_text: Mapped[str] = mapped_column(Text)
    judge_model_config_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_configs.id"))
    calibration_status: Mapped[str] = mapped_column(Text)
    last_kappa_score: Mapped[Optional[float]
                             ] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class JudgeScore(Base):
    __tablename__ = "judge_scores"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    run_trace_id: Mapped[UUID] = mapped_column(ForeignKey("run_traces.id"))
    judge_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("judge_versions.id"))
    dimension: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Numeric)
    rationale: Mapped[str] = mapped_column(Text)
    raw_judge_response: Mapped[Optional[dict[str, Any]]
                               ] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class RegressionRun(Base):
    __tablename__ = "regression_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    trigger: Mapped[str] = mapped_column(Text)
    baseline_prompt_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_versions.id"))
    candidate_prompt_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_versions.id"))
    baseline_model_config_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_configs.id"))
    candidate_model_config_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_configs.id"))
    golden_set_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("golden_set_versions.id"))
    judge_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("judge_versions.id"))
    status: Mapped[str] = mapped_column(Text)
    summary_stats: Mapped[Optional[dict[str, Any]]
                          ] = mapped_column(JSON, nullable=True)
    gate_decision: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_uri: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ci_run_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)


class RegressionCaseResult(Base):
    __tablename__ = "regression_case_results"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    regression_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("regression_runs.id"))
    golden_set_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("golden_set_cases.id"))
    baseline_run_trace_id: Mapped[UUID] = mapped_column(
        ForeignKey("run_traces.id"))
    candidate_run_trace_id: Mapped[UUID] = mapped_column(
        ForeignKey("run_traces.id"))
    baseline_score: Mapped[float] = mapped_column(Numeric)
    candidate_score: Mapped[float] = mapped_column(Numeric)
    delta: Mapped[float] = mapped_column(Numeric)
    case_verdict: Mapped[str] = mapped_column(Text)
    error_pattern: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DriftReferenceDistribution(Base):
    __tablename__ = "drift_reference_distributions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(Text)
    metric: Mapped[str] = mapped_column(Text)
    distribution_summary: Mapped[dict[str, Any]] = mapped_column(JSON)
    built_from_window: Mapped[Any] = mapped_column(TSTZRANGE)
    superseded_by: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("drift_reference_distributions.id"), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class DriftEvent(Base):
    __tablename__ = "drift_events"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    feature_name: Mapped[str] = mapped_column(Text)
    metric: Mapped[str] = mapped_column(Text)
    window_start: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True))
    window_end: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True))
    reference_distribution_id: Mapped[UUID] = mapped_column(
        ForeignKey("drift_reference_distributions.id"))
    statistic_value: Mapped[float] = mapped_column(Numeric)
    threshold: Mapped[float] = mapped_column(Numeric)
    severity: Mapped[str] = mapped_column(Text)
    sample_size: Mapped[int] = mapped_column(Integer)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    acknowledged_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
