"""
VERITAS AI — Regression and CI Schemas
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class RegressionRunRequest(BaseModel):
    baseline_prompt_version_id: uuid.UUID
    candidate_prompt_version_id: uuid.UUID
    dataset_version_id: uuid.UUID
    evaluator_version_id: uuid.UUID
    trigger: str = "github_pr"
    ci_run_url: Optional[str] = None


class RegressionCaseResultOut(BaseModel):
    id: uuid.UUID
    dataset_case_id: uuid.UUID
    baseline_score: float
    candidate_score: float
    delta: float
    case_verdict: str

    model_config = ConfigDict(from_attributes=True)


class RegressionRunOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    trigger: str
    status: str
    gate_decision: str
    decision_reason: Optional[str]
    wilcoxon_p_value: Optional[float]
    effect_size: Optional[float]
    summary_stats: Optional[Dict[str, Any]]
    ci_run_url: Optional[str]
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    case_results: Optional[List[RegressionCaseResultOut]] = None

    model_config = ConfigDict(from_attributes=True)

