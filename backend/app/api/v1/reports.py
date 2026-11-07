"""
VERITAS AI — Governance Reports & Evidence Package Router
"""
import uuid
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.tenant import Project
from backend.app.services.report_service import generate_governance_package, export_regression_csv
from backend.app.api.deps import get_current_project

router = APIRouter(prefix="/reports", tags=["Governance Reports (SR 11-7)"])


@router.get("/governance-package")
def get_governance_dossier(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return generate_governance_package(db=db, project_id=project.id, project_name=project.name)


@router.get("/regressions-csv")
def get_regressions_csv(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    csv_data = export_regression_csv(db=db, project_id=project.id)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=veritas_regressions_{project.slug}.csv"}
    )

