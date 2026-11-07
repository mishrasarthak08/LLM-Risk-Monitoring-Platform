"""
VERITAS AI — Governance & Regulatory Evidence Package Generator
Generates SR 11-7 / OCC 2011-12 evidence dossiers across JSON, CSV, and formatted reports.
"""
import uuid
import datetime
import io
import csv
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.prompt import Prompt, PromptVersion
from backend.app.models.dataset import Dataset, DatasetVersion
from backend.app.models.regression import RegressionRun
from backend.app.models.drift import DriftEvent
from backend.app.models.calibration import CalibrationRun
from backend.app.services.audit_service import verify_audit_chain


def generate_governance_package(
    db: Session,
    project_id: uuid.UUID,
    project_name: str = "Commercial Banking Credit Underwriting"
) -> Dict[str, Any]:
    """
    Assembles a comprehensive, defensible evidence package for Model Risk Management audits.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    audit_verification = verify_audit_chain(db, project_id)

    # 1. Prompts Inventory
    prompts = db.query(Prompt).filter(Prompt.project_id == project_id).all()
    prompt_inventory = []
    for p in prompts:
        versions = db.query(PromptVersion).filter(PromptVersion.prompt_id == p.id).all()
        prompt_inventory.append({
            "name": p.name,
            "slug": p.slug,
            "version_count": len(versions),
            "versions": [{
                "version_number": v.version_number,
                "label": v.version_label,
                "content_hash": v.content_hash,
                "author": v.author_email,
                "is_published": v.is_published,
                "created_at": v.created_at.isoformat() if v.created_at else None
            } for v in versions]
        })

    # 2. Datasets Inventory
    datasets = db.query(Dataset).filter(Dataset.project_id == project_id).all()
    dataset_inventory = []
    for d in datasets:
        versions = db.query(DatasetVersion).filter(DatasetVersion.dataset_id == d.id).all()
        dataset_inventory.append({
            "name": d.name,
            "slug": d.slug,
            "version_count": len(versions),
            "versions": [{
                "version_number": v.version_number,
                "label": v.version_label,
                "case_count": v.case_count,
                "content_hash": v.content_hash,
                "approved_by": v.approved_by,
                "created_at": v.created_at.isoformat() if v.created_at else None
            } for v in versions]
        })

    # 3. Regression History
    regressions = db.query(RegressionRun).filter(
        RegressionRun.project_id == project_id
    ).order_by(desc(RegressionRun.created_at)).limit(20).all()

    reg_summary = [{
        "run_id": str(r.id),
        "trigger": r.trigger,
        "gate_decision": r.gate_decision,
        "decision_reason": r.decision_reason,
        "wilcoxon_p_value": float(r.wilcoxon_p_value) if r.wilcoxon_p_value else None,
        "effect_size": float(r.effect_size) if r.effect_size else None,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None
    } for r in regressions]

    # 4. Drift Incidents
    drift_events = db.query(DriftEvent).filter(
        DriftEvent.project_id == project_id
    ).order_by(desc(DriftEvent.window_start)).limit(20).all()

    drift_summary = [{
        "event_id": str(e.id),
        "metric_name": e.metric_name,
        "test_type": e.test_type,
        "severity": e.severity,
        "statistic_value": float(e.statistic_value),
        "threshold": float(e.threshold),
        "p_value": float(e.p_value) if e.p_value else None,
        "triage_status": e.triage_status,
        "acknowledged_by": e.acknowledged_by,
        "notes": e.resolution_notes
    } for e in drift_events]

    # 5. Judge Calibration Status
    cal_runs = db.query(CalibrationRun).filter(
        CalibrationRun.project_id == project_id
    ).order_by(desc(CalibrationRun.created_at)).limit(5).all()

    cal_summary = [{
        "run_id": str(c.id),
        "status": c.status,
        "sample_size": c.sample_size,
        "overall_kappa": float(c.overall_kappa),
        "passed": c.passed
    } for c in cal_runs]

    return {
        "metadata": {
            "platform": "VERITAS AI",
            "report_type": "Model Risk Governance Evidence Dossier (SR 11-7 / OCC 2011-12)",
            "project_name": project_name,
            "project_id": str(project_id),
            "generated_at": now.isoformat(),
            "regulatory_pillars": [
                "Sound Model Development & Implementation",
                "Rigorous Objective Validation & Ongoing Monitoring",
                "Robust Governance, Policies & Controls"
            ]
        },
        "audit_chain_verification": audit_verification,
        "prompt_inventory": prompt_inventory,
        "dataset_inventory": dataset_inventory,
        "regression_testing_evidence": reg_summary,
        "continuous_drift_evidence": drift_summary,
        "evaluator_calibration_evidence": cal_summary
    }


def export_regression_csv(db: Session, project_id: uuid.UUID) -> str:
    """Exports regression runs as a structured CSV."""
    runs = db.query(RegressionRun).filter(RegressionRun.project_id == project_id).order_by(desc(RegressionRun.created_at)).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["run_id", "created_at", "trigger", "gate_decision", "decision_reason", "wilcoxon_p_value", "effect_size"])

    for r in runs:
        writer.writerow([
            str(r.id),
            r.created_at.isoformat() if r.created_at else "",
            r.trigger,
            r.gate_decision,
            r.decision_reason,
            float(r.wilcoxon_p_value) if r.wilcoxon_p_value else "",
            float(r.effect_size) if r.effect_size else ""
        ])

    return output.getvalue()

