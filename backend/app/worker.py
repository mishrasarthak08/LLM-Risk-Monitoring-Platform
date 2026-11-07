"""
VERITAS AI — Background Distributed Worker & Continuous Drift Monitor
Powered by Celery and Redis.
"""
import uuid
import datetime
from typing import Optional, List, Dict, Any
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.tenant import Project
from backend.app.models.trace import Trace
from backend.app.models.drift import DriftReferenceDistribution, DriftEvent
from backend.app.statistics.drift_detectors import (
    population_stability_index,
    kolmogorov_smirnov_shift,
    two_proportion_z_shift
)
from backend.app.services.audit_service import record_audit_event

# Initialize Celery app
celery_app = Celery(
    "veritas_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    worker_prefetch_multiplier=1,
)

# Optional Periodic Beat Schedule
celery_app.conf.beat_schedule = {
    "continuous-hourly-drift-monitor": {
        "task": "backend.app.worker.run_scheduled_drift_analysis",
        "schedule": crontab(minute=0),  # Top of every hour
        "args": ()
    }
}


@celery_app.task(name="backend.app.worker.run_scheduled_drift_analysis")
def run_scheduled_drift_analysis(project_id_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluates rolling production traffic over the past 24 hours against baseline distributions.
    Computes PSI, Kolmogorov-Smirnov, and Two-Proportion Z tests.
    Logs DriftEvent if PSI >= 0.25 (CRITICAL), PSI >= 0.10 (WARNING), or KS p < 0.05.
    """
    db: Session = SessionLocal()
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(hours=24)
    total_events_created = 0
    projects_analyzed = 0

    try:
        query = db.query(Project).filter(Project.is_active == True)
        if project_id_str:
            query = query.filter(Project.id == uuid.UUID(project_id_str))
        
        projects = query.all()

        for project in projects:
            projects_analyzed += 1
            # Retrieve reference distributions for project
            ref_dists = db.query(DriftReferenceDistribution).filter(
                DriftReferenceDistribution.project_id == project.id,
                DriftReferenceDistribution.is_active == True
            ).all()

            for ref in ref_dists:
                traces = db.query(Trace).filter(
                    Trace.project_id == project.id,
                    Trace.feature_name == ref.feature_name,
                    Trace.created_at >= cutoff
                ).all()

                if not traces or len(traces) < 20:
                    continue

                if ref.metric_name == "output_length":
                    cur_vals = [len(t.output_text or "") for t in traces if t.output_text]
                    ref_vals = ref.distribution_summary.get("values", [])
                    if len(cur_vals) >= 20 and len(ref_vals) >= 20:
                        # 1. PSI Test
                        psi_res = population_stability_index(ref_vals, cur_vals, bins=10, min_sample_size=20)
                        # 2. KS Shift Test
                        ks_res = kolmogorov_smirnov_shift(ref_vals, cur_vals, p_value_threshold=0.05, min_sample_size=20)

                        if psi_res["psi"] >= 0.10 or ks_res["is_drift"]:
                            severity = "CRITICAL" if psi_res["psi"] >= 0.25 else "WARNING"
                            evt = DriftEvent(
                                id=uuid.uuid4(),
                                project_id=project.id,
                                feature_name=ref.feature_name,
                                metric_name="output_length",
                                window_start=cutoff,
                                window_end=now,
                                sample_size=len(cur_vals),
                                test_type="PSI_AND_KS",
                                statistic_value=psi_res["psi"],
                                threshold=0.25,
                                p_value=ks_res.get("p_value", 0.0),
                                severity=severity,
                                triage_status="OPEN",
                                resolution_notes=f"Scheduled drift scan detected shift: PSI={psi_res['psi']:.4f}, KS-stat={ks_res['ks_statistic']:.4f}"
                            )
                            db.add(evt)
                            total_events_created += 1

                elif ref.metric_name == "refusal_rate":
                    cur_refusals = sum(1 for t in traces if t.status in ("REFUSAL", "ERROR"))
                    cur_total = len(traces)
                    ref_refusals = ref.distribution_summary.get("refusals", 2)
                    ref_total = ref.distribution_summary.get("total", 100)

                    z_res = two_proportion_z_shift(ref_refusals, ref_total, cur_refusals, cur_total, p_value_threshold=0.05)
                    if z_res["is_drift"]:
                        evt = DriftEvent(
                            id=uuid.uuid4(),
                            project_id=project.id,
                            feature_name=ref.feature_name,
                            metric_name="refusal_rate",
                            window_start=cutoff,
                            window_end=now,
                            sample_size=cur_total,
                            test_type="TWO_PROP_Z",
                            statistic_value=z_res["z_statistic"],
                            threshold=0.05,
                            p_value=z_res["p_value"],
                            severity=z_res["severity"],
                            triage_status="OPEN",
                            resolution_notes=f"Refusal rate shifted from {ref_refusals/ref_total:.1%} to {cur_refusals/cur_total:.1%}"
                        )
                        db.add(evt)
                        total_events_created += 1

            # Log audit event for scan
            record_audit_event(
                db=db,
                project_id=project.id,
                actor_email="system.celery@veritas.internal",
                event_type="SCHEDULED_DRIFT_ANALYSIS_COMPLETED",
                payload={
                    "window_start": cutoff.isoformat(),
                    "window_end": now.isoformat(),
                    "events_flagged": total_events_created
                }
            )

        db.commit()
        return {
            "status": "success",
            "projects_analyzed": projects_analyzed,
            "drift_events_created": total_events_created,
            "timestamp": now.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

