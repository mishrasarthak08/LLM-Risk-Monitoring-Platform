"""
VERITAS AI — Prompt Schemas
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class PromptCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class PromptVersionCreate(BaseModel):
    prompt_template: str
    template_variables: Optional[Dict[str, Any]] = None
    system_instruction: Optional[str] = None
    change_summary: str = "Updated prompt"
    version_label: Optional[str] = None
    publish: bool = False


class PromptVersionOut(BaseModel):
    id: uuid.UUID
    prompt_id: uuid.UUID
    version_number: int
    version_label: str
    content_hash: str
    prompt_template: str
    template_variables: Optional[Dict[str, Any]]
    system_instruction: Optional[str]
    change_summary: Optional[str]
    author_email: str
    is_published: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class PromptOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    slug: str
    description: Optional[str]
    active_version_id: Optional[uuid.UUID]
    created_at: datetime.datetime
    versions: Optional[List[PromptVersionOut]] = None

    model_config = ConfigDict(from_attributes=True)


class DiffRequest(BaseModel):
    version_a_id: uuid.UUID
    version_b_id: uuid.UUID


class DiffOut(BaseModel):
    version_a: Dict[str, Any]
    version_b: Dict[str, Any]
    diff_text: str

