"""
VERITAS AI — AI Observability & Traces Router
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.tenant import Project
from backend.app.models.trace import Trace
from backend.app.schemas.trace import TraceIngestRequest, TraceOut
from backend.app.services.trace_service import ingest_trace, get_traces, get_trace_by_id
from backend.app.api.deps import get_current_project

router = APIRouter(prefix="/traces", tags=["Observability & Traces"])


@router.post("/ingest", response_model=TraceOut)
def ingest_trace_endpoint(
    trace_req: TraceIngestRequest,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    spans_dicts = [s.model_dump() for s in trace_req.spans] if trace_req.spans else None
    trace = ingest_trace(
        db=db,
        project_id=project.id,
        feature_name=trace_req.feature_name,
        input_payload=trace_req.input_payload,
        output_text=trace_req.output_text,
        trace_type=trace_req.trace_type,
        prompt_version_id=trace_req.prompt_version_id,
        model_config_id=trace_req.model_config_id,
        model_name=trace_req.model_name,
        input_tokens=trace_req.input_tokens,
        output_tokens=trace_req.output_tokens,
        latency_ms=trace_req.latency_ms,
        status=trace_req.status,
        error_message=trace_req.error_message,
        metadata_json=trace_req.metadata_json,
        spans_data=spans_dicts
    )
    return trace


@router.get("", response_model=List[TraceOut])
def list_traces_endpoint(
    feature: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return get_traces(
        db=db,
        project_id=project.id,
        feature_name=feature,
        status=status,
        limit=limit,
        offset=offset
    )


@router.get("/{trace_id}", response_model=TraceOut)
def get_trace_detail_endpoint(
    trace_id: uuid.UUID,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    trace = get_trace_by_id(db=db, project_id=project.id, trace_id=trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return trace

