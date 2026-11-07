"""
VERITAS AI — Continuous Statistical Drift & Incident Service
"""
import uuid
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.drift import DriftReferenceDistribution, DriftEvent, DriftTriageLog
from backend.app.models.trace import Trace
from backend.app.statistics.drift_detectors import (
    population_stability_index,
    kolmogorov_smirnov_shift,
    two_proportion_z_shift
)
from backend.app.services.audit_service import record_audit_event


def evaluate_production_drift(
    db: Session,
    project_id: uuid.UUID,
    feature_name: str,
    rolling_hours: int = 24
) -> List[DriftEvent]:
    """
    Evaluates rolling production traffic against pinned baseline distributions.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(hours=rolling_hours)

    traces = db.query(Trace).filter(
        Trace.project_id == project_id,
        Trace.feature_name == feature_name,
        Trace.created_at >= cutoff
    ).all()

    events_created: List[DriftEvent] = []
    if not traces:
        return events_created

    # 1. Output Length Drift (KS Test)
    cur_lengths = [len(t.output_text or "") for t in traces if t.output_text]
    ref_dist = db.query(DriftReferenceDistribution).filter(
        DriftReferenceDistribution.project_id == project_id,
        DriftReferenceDistribution.feature_name == feature_name,
        DriftReferenceDistribution.metric_name == "output_length",
        DriftReferenceDistribution.is_active == True
    ).first()

    ref_lengths = ref_dist.distribution_summary.get("values", []) if ref_dist else []
    if ref_lengths and len(cur_lengths) >= 20:
        ks_res = kolmogorov_smirnov_shift(ref_lengths, cur_lengths, p_value_threshold=0.05, min_sample_size=20)
        if ks_res["is_drift"]:
            evt = DriftEvent(
                id=uuid.uuid4(),
                project_id=project_id,
                feature_name=feature_name,
                metric_name="output_length",
                window_start=cutoff,
                window_end=now,
                sample_size=len(cur_lengths),
                test_type="KS_TEST",
                statistic_value=ks_res["ks_statistic"],
                threshold=0.05,
                p_value=ks_res["p_value"],
                severity=ks_res["severity"],
                triage_status="OPEN"
            )
            db.add(evt)
            events_created.append(evt)

    # 2. Refusal Rate Drift (Two-Proportion Z Test)
    cur_refusals = sum(1 for t in traces if t.status in ("REFUSAL", "ERROR"))
    cur_total = len(traces)

    ref_refusal_dist = db.query(DriftReferenceDistribution).filter(
        DriftReferenceDistribution.project_id == project_id,
        DriftReferenceDistribution.feature_name == feature_name,
        DriftReferenceDistribution.metric_name == "refusal_rate",
        DriftReferenceDistribution.is_active == True
    ).first()

    ref_refusals = ref_refusal_dist.distribution_summary.get("refusals", 2) if ref_refusal_dist else 2
    ref_total = ref_refusal_dist.distribution_summary.get("total", 100) if ref_refusal_dist else 100

    z_res = two_proportion_z_shift(ref_refusals, ref_total, cur_refusals, cur_total, p_value_threshold=0.05)
    if z_res["is_drift"]:
        evt = DriftEvent(
            id=uuid.uuid4(),
            project_id=project_id,
            feature_name=feature_name,
            metric_name="refusal_rate",
            window_start=cutoff,
            window_end=now,
            sample_size=cur_total,
            test_type="TWO_PROP_Z",
            statistic_value=z_res["z_statistic"],
            threshold=0.05,
            p_value=z_res["p_value"],
            severity=z_res["severity"],
            triage_status="OPEN"
        )
        db.add(evt)
        events_created.append(evt)

    db.commit()
    return events_created


def update_drift_triage(
    db: Session,
    project_id: uuid.UUID,
    event_id: uuid.UUID,
    new_status: str,
    notes: str,
    author_email: str
) -> DriftEvent:
    event = db.query(DriftEvent).filter(
        DriftEvent.project_id == project_id,
        DriftEvent.id == event_id
    ).first()
    if not event:
        raise ValueError("Drift event not found.")

    old_status = event.triage_status
    event.triage_status = new_status
    event.resolution_notes = notes
    event.acknowledged_by = author_email
    if new_status in ("RESOLVED", "CONFIRMED_ISSUE", "BENIGN_SHIFT", "FALSE_POSITIVE"):
        event.resolved_at = datetime.datetime.now(datetime.timezone.utc)

    log = DriftTriageLog(
        id=uuid.uuid4(),
        drift_event_id=event.id,
        author_email=author_email,
        previous_status=old_status,
        new_status=new_status,
        notes=notes
    )
    db.add(log)
    db.commit()
    db.refresh(event)

    record_audit_event(
        db=db,
        project_id=project_id,
        actor_email=author_email,
        event_type="DRIFT_EVENT_TRIAGED",
        payload={
            "drift_event_id": str(event.id),
            "metric_name": event.metric_name,
            "previous_status": old_status,
            "new_status": new_status,
            "notes": notes
        }
    )

    return event

