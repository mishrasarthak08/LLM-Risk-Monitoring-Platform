"""
VERITAS AI — Statistical Drift Detection Router
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.database import get_db
from backend.app.models.tenant import Project, User
from backend.app.models.drift import DriftEvent
from backend.app.schemas.drift import DriftEventOut, DriftTriageUpdateRequest
from backend.app.services.drift_service import evaluate_production_drift, update_drift_triage
from backend.app.api.deps import get_current_project, get_current_user

router = APIRouter(prefix="/drift", tags=["Production Drift Monitoring"])


@router.get("/events", response_model=List[DriftEventOut])
def list_drift_events(
    status: Optional[str] = None,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    query = db.query(DriftEvent).filter(DriftEvent.project_id == project.id)
    if status:
        query = query.filter(DriftEvent.triage_status == status)
    return query.order_by(desc(DriftEvent.window_start)).all()


@router.post("/evaluate", response_model=List[DriftEventOut])
def trigger_drift_evaluation(
    feature_name: str = "credit_memo_v1",
    rolling_hours: int = 24,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return evaluate_production_drift(
        db=db,
        project_id=project.id,
        feature_name=feature_name,
        rolling_hours=rolling_hours
    )


@router.patch("/events/{event_id}/triage", response_model=DriftEventOut)
def triage_drift_event(
    event_id: uuid.UUID,
    triage_req: DriftTriageUpdateRequest,
    project: Project = Depends(get_current_project),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    author_email = current_user.email if current_user else "oncall_engineer@bank.com"
    try:
        return update_drift_triage(
            db=db,
            project_id=project.id,
            event_id=event_id,
            new_status=triage_req.new_status,
            notes=triage_req.notes,
            author_email=author_email
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

