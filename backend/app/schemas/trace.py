"""
VERITAS AI — Trace and Span Schemas
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class SpanIngest(BaseModel):
    name: str
    span_type: str = "llm_call"
    parent_span_id: Optional[uuid.UUID] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    latency_ms: int = 0
    tokens: int = 0
    error_message: Optional[str] = None


class TraceIngestRequest(BaseModel):
    feature_name: str
    input_payload: Dict[str, Any]
    output_text: Optional[str] = None
    trace_type: str = "production"
    prompt_version_id: Optional[uuid.UUID] = None
    model_config_id: Optional[uuid.UUID] = None
    model_name: str = "gemini-2.5-flash"
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    status: str = "SUCCESS"
    error_message: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    spans: Optional[List[SpanIngest]] = None


class SpanOut(BaseModel):
    id: uuid.UUID
    parent_span_id: Optional[uuid.UUID]
    name: str
    span_type: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    latency_ms: int
    tokens: int
    error_message: Optional[str]
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TraceOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    feature_name: str
    trace_type: str
    prompt_version_id: Optional[uuid.UUID]
    input_payload: Dict[str, Any]
    output_text: Optional[str]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: int
    status: str
    error_message: Optional[str]
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime.datetime
    spans: Optional[List[SpanOut]] = None

    model_config = ConfigDict(from_attributes=True)

