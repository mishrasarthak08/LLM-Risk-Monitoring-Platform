import contextvars
from typing import Optional
from uuid import UUID

_parent_span_id: contextvars.ContextVar[Optional[UUID]] = contextvars.ContextVar(
    "parent_span_id", default=None
)


def get_parent_span_id() -> Optional[UUID]:
    return _parent_span_id.get()


def set_parent_span_id(span_id: UUID) -> contextvars.Token:
    return _parent_span_id.set(span_id)


def reset_parent_span_id(token: contextvars.Token) -> None:
    _parent_span_id.reset(token)
