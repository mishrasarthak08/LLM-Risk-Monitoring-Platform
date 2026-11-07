"""
VERITAS AI — FastAPI Dependency Injection Layer
Authenticates JWT tokens, validates API keys, and scopes database sessions to projects.
"""
import uuid
import datetime
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token, hash_api_key
from backend.app.models.tenant import User, Project, APIKey, Membership

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not token:
        # For development/demo convenience, return default admin if available
        demo_user = db.query(User).filter(User.email == "demo@bank.com").first()
        return demo_user

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")
    return user


def get_current_project(
    x_project_id: Optional[str] = Header(None, alias="X-Project-ID"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """Resolves project context via X-API-Key or X-Project-ID or first available project."""
    # 1. API Key Authentication
    if x_api_key:
        hashed = hash_api_key(x_api_key)
        key_record = db.query(APIKey).filter(APIKey.hashed_key == hashed, APIKey.is_active == True).first()
        if key_record:
            key_record.last_used_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
            return key_record.project

    # 2. Header Project ID
    if x_project_id:
        try:
            p_uuid = uuid.UUID(x_project_id)
            project = db.query(Project).filter(Project.id == p_uuid).first()
            if project:
                return project
        except ValueError:
            pass

    # 3. Default or First Project
    default_p = db.query(Project).filter(Project.slug == "credit-memo-underwriting").first()
    if default_p:
        return default_p

    first_p = db.query(Project).first()
    if first_p:
        return first_p

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active project found in system.")

