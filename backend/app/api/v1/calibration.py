"""
VERITAS AI — Judge Calibration & Human Annotation Router
"""
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.database import get_db
from backend.app.models.tenant import Project, User
from backend.app.models.calibration import HumanAnnotation, CalibrationRun
from backend.app.schemas.drift import HumanAnnotationCreate, CalibrationRunOut
from backend.app.services.calibration_service import record_human_annotation, execute_calibration_run
from backend.app.api.deps import get_current_project, get_current_user

router = APIRouter(prefix="/calibration", tags=["Judge Calibration & Agreement"])


@router.post("/annotations")
def add_human_annotation(
    anno_in: HumanAnnotationCreate,
    project: Project = Depends(get_current_project),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = current_user.email if current_user else "expert_underwriter@bank.com"
    anno = record_human_annotation(
        db=db,
        project_id=project.id,
        annotator_email=email,
        dimension=anno_in.dimension,
        human_score=anno_in.human_score,
        trace_id=anno_in.trace_id,
        dataset_case_id=anno_in.dataset_case_id,
        notes=anno_in.notes
    )
    return {"id": str(anno.id), "status": "recorded"}


@router.post("/run", response_model=CalibrationRunOut)
def run_calibration(
    evaluator_version_id: uuid.UUID,
    dimension_pairs: Dict[str, Dict[str, List[float]]],
    project: Project = Depends(get_current_project),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = current_user.email if current_user else "model_risk_officer@bank.com"
    try:
        cal = execute_calibration_run(
            db=db,
            project_id=project.id,
            evaluator_version_id=evaluator_version_id,
            dimension_pairs=dimension_pairs,
            author_email=email
        )
        return cal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=List[CalibrationRunOut])
def get_calibration_history(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return db.query(CalibrationRun).filter(
        CalibrationRun.project_id == project.id
    ).order_by(desc(CalibrationRun.created_at)).all()
