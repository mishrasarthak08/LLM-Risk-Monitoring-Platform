"""
VERITAS AI — Evaluator Calibration & Agreement Service
"""
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.calibration import HumanAnnotation, CalibrationRun, CalibrationDimensionScore
from backend.app.models.evaluator import EvaluatorVersion
from backend.app.statistics.agreement import compute_evaluator_agreement
from backend.app.services.audit_service import record_audit_event


def record_human_annotation(
    db: Session,
    project_id: uuid.UUID,
    annotator_email: str,
    dimension: str,
    human_score: float,
    trace_id: Optional[uuid.UUID] = None,
    dataset_case_id: Optional[uuid.UUID] = None,
    notes: Optional[str] = None
) -> HumanAnnotation:
    anno = HumanAnnotation(
        id=uuid.uuid4(),
        project_id=project_id,
        trace_id=trace_id,
        dataset_case_id=dataset_case_id,
        annotator_email=annotator_email,
        dimension=dimension,
        human_score=human_score,
        notes=notes
    )
    db.add(anno)
    db.commit()
    db.refresh(anno)
    return anno


def execute_calibration_run(
    db: Session,
    project_id: uuid.UUID,
    evaluator_version_id: uuid.UUID,
    dimension_pairs: Dict[str, Dict[str, List[float]]],
    # e.g. {"factual_accuracy": {"human": [...], "judge": [...]}}
    thresholds: Optional[Dict[str, float]] = None,
    author_email: str = "risk_officer@bank.com"
) -> CalibrationRun:
    """
    Executes a mathematical calibration run for an LLM Judge version.
    """
    eval_v = db.query(EvaluatorVersion).filter(EvaluatorVersion.id == evaluator_version_id).first()
    if not eval_v:
        raise ValueError("Evaluator version not found.")

    cal_thresholds = thresholds or {
        "factual_accuracy": 0.70,
        "policy_compliance": 0.80,
        "completeness": 0.70,
        "reasoning_quality": 0.60,
        "tone_clarity": 0.55
    }

    all_passed = True
    total_samples = 0
    kappa_scores = []

    cal_run = CalibrationRun(
        id=uuid.uuid4(),
        project_id=project_id,
        evaluator_version_id=evaluator_version_id,
        status="RUNNING",
        sample_size=0,
        overall_kappa=0.0,
        passed=False
    )
    db.add(cal_run)

    for dim_name, pair in dimension_pairs.items():
        h_scores = pair.get("human", [])
        j_scores = pair.get("judge", [])
        scale_type = "ordinal" if dim_name in ("reasoning_quality", "tone_clarity") else "binary"
        target_thresh = cal_thresholds.get(dim_name, 0.65)

        res = compute_evaluator_agreement(h_scores, j_scores, scale_type=scale_type, min_kappa_threshold=target_thresh)
        passed = res["passed"]
        if not passed and dim_name in ("factual_accuracy", "policy_compliance"):
            all_passed = False

        dim_score = CalibrationDimensionScore(
            id=uuid.uuid4(),
            calibration_run_id=cal_run.id,
            dimension=dim_name,
            kappa_score=res["kappa"],
            threshold=target_thresh,
            passed=passed,
            sample_size=len(h_scores),
            confusion_matrix=res.get("confusion_matrix")
        )
        db.add(dim_score)
        total_samples = max(total_samples, len(h_scores))
        kappa_scores.append(res["kappa"])

    overall_kappa = float(sum(kappa_scores) / len(kappa_scores)) if kappa_scores else 0.0

    cal_run.sample_size = total_samples
    cal_run.overall_kappa = round(overall_kappa, 3)
    cal_run.passed = all_passed
    cal_run.status = "CALIBRATED" if all_passed else "FAILED"

    eval_v.calibration_status = "CALIBRATED" if all_passed else "FAILED"
    eval_v.last_kappa_score = cal_run.overall_kappa

    db.commit()
    db.refresh(cal_run)

    record_audit_event(
        db=db,
        project_id=project_id,
        actor_email=author_email,
        event_type="CALIBRATION_CERTIFIED",
        payload={
            "calibration_run_id": str(cal_run.id),
            "evaluator_version_id": str(evaluator_version_id),
            "overall_kappa": cal_run.overall_kappa,
            "passed": all_passed,
            "status": cal_run.status
        }
    )

    return cal_run

