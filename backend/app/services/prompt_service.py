"""
VERITAS AI — Prompt Registry & Versioning Service
Enforces content-addressed immutability and version history.
"""
import uuid
import difflib
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.prompt import Prompt, PromptVersion
from backend.app.core.security import compute_sha256
from backend.app.services.audit_service import record_audit_event


def create_or_get_prompt(
    db: Session,
    project_id: uuid.UUID,
    name: str,
    slug: str,
    description: Optional[str] = None
) -> Prompt:
    prompt = db.query(Prompt).filter(
        Prompt.project_id == project_id,
        Prompt.slug == slug
    ).first()
    if not prompt:
        prompt = Prompt(
            id=uuid.uuid4(),
            project_id=project_id,
            name=name,
            slug=slug,
            description=description
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
    return prompt


def create_prompt_version(
    db: Session,
    project_id: uuid.UUID,
    prompt_id: uuid.UUID,
    prompt_template: str,
    author_email: str,
    template_variables: Optional[Dict[str, Any]] = None,
    system_instruction: Optional[str] = None,
    change_summary: str = "Initial version",
    version_label: Optional[str] = None,
    publish: bool = False
) -> PromptVersion:
    """
    Creates an immutable version of a prompt. Never overwrites existing versions.
    """
    latest = db.query(PromptVersion).filter(
        PromptVersion.prompt_id == prompt_id
    ).order_by(desc(PromptVersion.version_number)).first()

    next_version = (latest.version_number + 1) if latest else 1
    label = version_label or f"v{next_version}.0.0"

    content_dict = {
        "template": prompt_template,
        "variables": template_variables or {},
        "system": system_instruction or ""
    }
    content_hash = compute_sha256(content_dict)

    version = PromptVersion(
        id=uuid.uuid4(),
        prompt_id=prompt_id,
        version_number=next_version,
        version_label=label,
        content_hash=content_hash,
        prompt_template=prompt_template,
        template_variables=template_variables,
        system_instruction=system_instruction,
        change_summary=change_summary,
        author_email=author_email,
        is_published=publish
    )
    db.add(version)

    if publish:
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if prompt:
            prompt.active_version_id = version.id

    db.commit()
    db.refresh(version)

    # Record in cryptographic audit trail
    record_audit_event(
        db=db,
        project_id=project_id,
        actor_email=author_email,
        event_type="PROMPT_VERSION_CREATED",
        payload={
            "prompt_id": str(prompt_id),
            "version_id": str(version.id),
            "version_number": next_version,
            "content_hash": content_hash,
            "is_published": publish
        }
    )

    return version


def diff_prompt_versions(
    db: Session,
    version_a_id: uuid.UUID,
    version_b_id: uuid.UUID
) -> Dict[str, Any]:
    v_a = db.query(PromptVersion).filter(PromptVersion.id == version_a_id).first()
    v_b = db.query(PromptVersion).filter(PromptVersion.id == version_b_id).first()

    if not v_a or not v_b:
        raise ValueError("One or both prompt versions not found.")

    diff = list(difflib.unified_diff(
        v_a.prompt_template.splitlines(keepends=True),
        v_b.prompt_template.splitlines(keepends=True),
        fromfile=f"version_{v_a.version_label}",
        tofile=f"version_{v_b.version_label}"
    ))

    return {
        "version_a": {"id": str(v_a.id), "label": v_a.version_label, "hash": v_a.content_hash},
        "version_b": {"id": str(v_b.id), "label": v_b.version_label, "hash": v_b.content_hash},
        "diff_text": "".join(diff)
    }

