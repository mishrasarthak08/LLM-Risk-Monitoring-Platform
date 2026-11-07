"""
VERITAS AI — Benchmark Dataset Schemas
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class DatasetCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class DatasetCaseOut(BaseModel):
    id: uuid.UUID
    case_hash: str
    category: str
    severity: str
    input_payload: Dict[str, Any]
    expected_output: Optional[str]
    expected_criteria: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class DatasetVersionOut(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    version_number: int
    version_label: str
    content_hash: str
    case_count: int
    change_summary: str
    approved_by: str
    created_at: datetime.datetime
    cases: Optional[List[DatasetCaseOut]] = None

    model_config = ConfigDict(from_attributes=True)


class DatasetOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    active_version_id: Optional[uuid.UUID]
    created_at: datetime.datetime
    versions: Optional[List[DatasetVersionOut]] = None

    model_config = ConfigDict(from_attributes=True)

