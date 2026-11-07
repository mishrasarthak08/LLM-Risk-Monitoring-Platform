"""
VERITAS AI — Cryptographic Audit Trail Router
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.core.database import get_db
from backend.app.models.tenant import Project
from backend.app.models.audit import AuditEvent
from backend.app.schemas.drift import AuditEventOut, AuditVerifyOut
from backend.app.services.audit_service import verify_audit_chain
from backend.app.api.deps import get_current_project

router = APIRouter(prefix="/audit", tags=["Cryptographic Audit Ledger"])


@router.get("/events", response_model=List[AuditEventOut])
def list_audit_events(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return db.query(AuditEvent).filter(
        AuditEvent.project_id == project.id
    ).order_by(desc(AuditEvent.sequence_number)).limit(100).all()


@router.get("/verify", response_model=AuditVerifyOut)
def verify_audit_integrity(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return verify_audit_chain(db=db, project_id=project.id)

