"""
VERITAS AI — Benchmark Datasets Router
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.tenant import Project, User
from backend.app.models.dataset import Dataset, DatasetVersion
from backend.app.schemas.dataset import DatasetCreate, DatasetOut, DatasetVersionOut
from backend.app.services.dataset_service import create_or_get_dataset, import_dataset_version_from_jsonl
from backend.app.api.deps import get_current_project, get_current_user

router = APIRouter(prefix="/datasets", tags=["Benchmark Datasets"])


@router.get("", response_model=List[DatasetOut])
def list_datasets(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return db.query(Dataset).filter(Dataset.project_id == project.id).all()


@router.post("", response_model=DatasetOut)
def create_dataset(
    dataset_in: DatasetCreate,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return create_or_get_dataset(
        db=db,
        project_id=project.id,
        name=dataset_in.name,
        slug=dataset_in.slug,
        description=dataset_in.description
    )


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset_detail(
    dataset_id: uuid.UUID,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    ds = db.query(Dataset).filter(
        Dataset.project_id == project.id,
        Dataset.id == dataset_id
    ).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return ds


@router.post("/{dataset_id}/import-jsonl", response_model=DatasetVersionOut)
def import_jsonl_endpoint(
    dataset_id: uuid.UUID,
    jsonl_content: str = Body(..., media_type="text/plain"),
    change_summary: str = Body("Imported test cases"),
    project: Project = Depends(get_current_project),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    author_email = current_user.email if current_user else "risk_engineer@bank.com"
    return import_dataset_version_from_jsonl(
        db=db,
        project_id=project.id,
        dataset_id=dataset_id,
        jsonl_content=jsonl_content,
        author_email=author_email,
        change_summary=change_summary
    )
