"""
VERITAS AI — Drift, Calibration, and Audit Schemas
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


# DRIFT
class DriftEventOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    feature_name: str
    metric_name: str
    window_start: datetime.datetime
    window_end: datetime.datetime
    sample_size: int
    test_type: str
    statistic_value: float
    threshold: float
    p_value: Optional[float]
    severity: str
    triage_status: str
    resolution_notes: Optional[str]
    acknowledged_by: Optional[str]
    resolved_at: Optional[datetime.datetime]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class DriftTriageUpdateRequest(BaseModel):
    new_status: str  # OPEN, INVESTIGATING, CONFIRMED_ISSUE, BENIGN_SHIFT, FALSE_POSITIVE, RESOLVED
    notes: str


# CALIBRATION
class HumanAnnotationCreate(BaseModel):
    dimension: str
    human_score: float
    trace_id: Optional[uuid.UUID] = None
    dataset_case_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class CalibrationDimensionScoreOut(BaseModel):
    dimension: str
    kappa_score: float
    threshold: float
    passed: bool
    sample_size: int
    confusion_matrix: Optional[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


class CalibrationRunOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    evaluator_version_id: uuid.UUID
    status: str
    sample_size: int
    overall_kappa: float
    passed: bool
    created_at: datetime.datetime
    dimension_scores: Optional[List[CalibrationDimensionScoreOut]] = None

    model_config = ConfigDict(from_attributes=True)


# AUDIT
class AuditEventOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    sequence_number: int
    actor_email: str
    event_type: str
    payload_json: Dict[str, Any]
    previous_hash: str
    record_hash: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class AuditVerifyOut(BaseModel):
    is_valid: bool
    total_records: int
    head_hash: Optional[str] = None
    broken_sequence: Optional[int] = None
    tampered_record_id: Optional[str] = None
    message: str

