"""
VERITAS AI — Tracing & Observability Service
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.app.models.trace import Trace, Span
from backend.app.core.redactor import sanitize_payload
from backend.app.core.pricing import compute_cost_usd


def ingest_trace(
    db: Session,
    project_id: uuid.UUID,
    feature_name: str,
    input_payload: Dict[str, Any],
    output_text: Optional[str] = None,
    trace_type: str = "production",
    prompt_version_id: Optional[uuid.UUID] = None,
    model_config_id: Optional[uuid.UUID] = None,
    model_name: str = "gemini-2.5-flash",
    input_tokens: int = 0,
    output_tokens: int = 0,
    latency_ms: int = 0,
    status: str = "SUCCESS",
    error_message: Optional[str] = None,
    metadata_json: Optional[Dict[str, Any]] = None,
    spans_data: Optional[List[Dict[str, Any]]] = None
) -> Trace:
    """
    Persists a trace with automated PII/credential sanitization and exact cost computation.
    """
    clean_input = sanitize_payload(input_payload)
    clean_output = sanitize_payload(output_text) if output_text else None
    clean_meta = sanitize_payload(metadata_json) if metadata_json else None

    total_tokens = input_tokens + output_tokens
    cost = compute_cost_usd(model_name, input_tokens, output_tokens)

    trace = Trace(
        id=uuid.uuid4(),
        project_id=project_id,
        feature_name=feature_name,
        trace_type=trace_type,
        prompt_version_id=prompt_version_id,
        model_config_id=model_config_id,
        input_payload=clean_input,
        output_text=clean_output,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cost_usd=cost,
        latency_ms=latency_ms,
        status=status,
        error_message=error_message,
        metadata_json=clean_meta
    )
    db.add(trace)

    if spans_data:
        for span_dict in spans_data:
            span = Span(
                id=uuid.uuid4(),
                trace_id=trace.id,
                parent_span_id=span_dict.get("parent_span_id"),
                name=span_dict.get("name", "llm_operation"),
                span_type=span_dict.get("span_type", "llm_call"),
                input_data=sanitize_payload(span_dict.get("input_data")),
                output_data=sanitize_payload(span_dict.get("output_data")),
                latency_ms=span_dict.get("latency_ms", 0),
                tokens=span_dict.get("tokens", 0),
                error_message=span_dict.get("error_message")
            )
            db.add(span)

    db.commit()
    db.refresh(trace)
    return trace


def get_traces(
    db: Session,
    project_id: uuid.UUID,
    feature_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Trace]:
    query = db.query(Trace).filter(Trace.project_id == project_id)
    if feature_name:
        query = query.filter(Trace.feature_name == feature_name)
    if status:
        query = query.filter(Trace.status == status)
    return query.order_by(desc(Trace.created_at)).offset(offset).limit(limit).all()


def get_trace_by_id(db: Session, project_id: uuid.UUID, trace_id: uuid.UUID) -> Optional[Trace]:
    return db.query(Trace).filter(
        Trace.project_id == project_id,
        Trace.id == trace_id
    ).first()

