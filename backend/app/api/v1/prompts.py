"""
VERITAS AI — Prompts & Version Registry Router
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.tenant import Project, User
from backend.app.models.prompt import Prompt, PromptVersion
from backend.app.schemas.prompt import (
    PromptCreate,
    PromptOut,
    PromptVersionCreate,
    PromptVersionOut,
    DiffRequest,
    DiffOut
)
from backend.app.services.prompt_service import (
    create_or_get_prompt,
    create_prompt_version,
    diff_prompt_versions
)
from backend.app.api.deps import get_current_project, get_current_user

router = APIRouter(prefix="/prompts", tags=["Prompt Registry"])


@router.get("", response_model=List[PromptOut])
def list_prompts(
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return db.query(Prompt).filter(Prompt.project_id == project.id).all()


@router.post("", response_model=PromptOut)
def create_prompt(
    prompt_in: PromptCreate,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    return create_or_get_prompt(
        db=db,
        project_id=project.id,
        name=prompt_in.name,
        slug=prompt_in.slug,
        description=prompt_in.description
    )


@router.get("/{prompt_id}", response_model=PromptOut)
def get_prompt_detail(
    prompt_id: uuid.UUID,
    project: Project = Depends(get_current_project),
    db: Session = Depends(get_db)
):
    prompt = db.query(Prompt).filter(
        Prompt.project_id == project.id,
        Prompt.id == prompt_id
    ).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found.")
    return prompt


@router.post("/{prompt_id}/versions", response_model=PromptVersionOut)
def create_version(
    prompt_id: uuid.UUID,
    ver_in: PromptVersionCreate,
    project: Project = Depends(get_current_project),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    author_email = current_user.email if current_user else "engineer@bank.com"
    return create_prompt_version(
        db=db,
        project_id=project.id,
        prompt_id=prompt_id,
        prompt_template=ver_in.prompt_template,
        author_email=author_email,
        template_variables=ver_in.template_variables,
        system_instruction=ver_in.system_instruction,
        change_summary=ver_in.change_summary,
        version_label=ver_in.version_label,
        publish=ver_in.publish
    )


@router.post("/diff", response_model=DiffOut)
def diff_versions(diff_req: DiffRequest, db: Session = Depends(get_db)):
    try:
        return diff_prompt_versions(
            db=db,
            version_a_id=diff_req.version_a_id,
            version_b_id=diff_req.version_b_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
