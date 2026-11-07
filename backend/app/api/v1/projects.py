"""
VERITAS AI — Projects & API Keys Router
"""
import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import generate_api_key
from backend.app.models.tenant import Project, APIKey, Organization, User, Membership
from backend.app.schemas.tenant import ProjectCreate, ProjectOut, APIKeyCreate, APIKeyOut
from backend.app.schemas.trace import TraceOut
from backend.app.services.trace_service import ingest_trace
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectOut])
def list_projects(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user and current_user.memberships:
        org_ids = [m.organization_id for m in current_user.memberships]
        return db.query(Project).filter(Project.organization_id.in_(org_ids)).all()
    return db.query(Project).all()


@router.post("", response_model=ProjectOut)
def create_project(
    project_in: ProjectCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    org_id = None
    if current_user and current_user.memberships:
        org_id = current_user.memberships[0].organization_id
    else:
        org = db.query(Organization).first()
        if not org:
            org = Organization(id=uuid.uuid4(), name="Default Org", slug="default-org")
            db.add(org)
            db.commit()
        org_id = org.id

    slug = project_in.slug
    if db.query(Project).filter(Project.organization_id == org_id, Project.slug == slug).first():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    proj = Project(
        id=uuid.uuid4(),
        organization_id=org_id,
        name=project_in.name,
        slug=slug,
        description=project_in.description
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
    return proj


@router.get("/{project_id}/api-keys", response_model=List[APIKeyOut])
def list_project_api_keys(project_id: uuid.UUID, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")
    return db.query(APIKey).filter(APIKey.project_id == project_id).order_by(APIKey.created_at.desc()).all()


@router.post("/{project_id}/api-keys", response_model=APIKeyOut)
def create_project_api_key(project_id: uuid.UUID, key_in: APIKeyCreate, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")

    raw_key, prefix, hashed = generate_api_key()
    api_key = APIKey(
        id=uuid.uuid4(),
        project_id=project_id,
        name=key_in.name,
        key_prefix=prefix,
        hashed_key=hashed,
        is_active=True
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    out = APIKeyOut.model_validate(api_key)
    out.raw_key = raw_key
    return out


@router.delete("/{project_id}/api-keys/{key_id}")
def revoke_project_api_key(project_id: uuid.UUID, key_id: uuid.UUID, db: Session = Depends(get_db)):
    key_record = db.query(APIKey).filter(APIKey.id == key_id, APIKey.project_id == project_id).first()
    if not key_record:
        raise HTTPException(status_code=404, detail="API Key not found.")
    key_record.is_active = False
    db.commit()
    return {"status": "REVOKED", "key_id": str(key_id)}


@router.post("/{project_id}/test-event", response_model=TraceOut)
def send_test_event(project_id: uuid.UUID, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")

    trace = ingest_trace(
        db=db,
        project_id=proj.id,
        feature_name="onboarding_verification",
        input_payload={"message": "VERITAS AI connectivity handshake test event.", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()},
        output_text="Handshake confirmed. Your application is successfully integrated with VERITAS AI.",
        trace_type="test",
        model_name="veritas-handshake-v1",
        input_tokens=42,
        output_tokens=18,
        latency_ms=115,
        status="SUCCESS",
        spans_data=[
            {
                "name": "connectivity_handshake",
                "span_type": "handshake",
                "latency_ms": 115,
                "tokens": 60
            }
        ]
    )
    return trace


