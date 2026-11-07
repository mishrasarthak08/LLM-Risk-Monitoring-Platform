"""
VERITAS AI — Regression Suite & CI Gatekeeper Router
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.database import get_db
from backend.app.models.tenant import Project, User
from backend.app.models.regression import RegressionRun
from backend.app.schemas.regression import RegressionRunRequest, RegressionRunOut
from backend.app.services.regression_service import execute_regression_run
from backend.app.providers.factory import get_llm_provider
from backend.app.api.deps import get_current_project, get_current_user

router = APIRouter(prefix="/regressions", tags=["Regression Testing & CI Gatekeeper"])


@router.get("", response_model=List[RegressionRunOut])
def list_regression_runs(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return db.query(RegressionRun).filter(
        RegressionRun.project_id == project.id
    ).order_by(desc(RegressionRun.created_at)).all()


@router.post("/run", response_model=RegressionRunOut)
async def trigger_regression_run(
    req: RegressionRunRequest,
    project: Project = Depends(get_current_project),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = get_llm_provider()
    actor_email = current_user.email if current_user else "ci_pipeline@bank.com"
    try:
        run = await execute_regression_run(
            db=db,
            project_id=project.id,
            baseline_prompt_version_id=req.baseline_prompt_version_id,
            candidate_prompt_version_id=req.candidate_prompt_version_id,
            dataset_version_id=req.dataset_version_id,
            evaluator_version_id=req.evaluator_version_id,
            provider=provider,
            trigger=req.trigger,
            ci_run_url=req.ci_run_url,
            actor_email=actor_email
        )
        return run
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{run_id}", response_model=RegressionRunOut)
def get_regression_run_detail(
    run_id: uuid.UUID,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    run = db.query(RegressionRun).filter(
        RegressionRun.project_id == project.id,
        RegressionRun.id == run_id
    ).first()
    if not run:
        raise HTTPException(status_code=404, detail="Regression run not found.")
    return run
