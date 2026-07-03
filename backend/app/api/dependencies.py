from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import decode_access_token
from app.database.models import User
from app.database.session import get_db
from app.jobs.manager import JobManager, job_manager
from app.plugins.registry import ModuleRegistry, module_registry


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_module_registry() -> ModuleRegistry:
    return module_registry


def get_job_manager() -> JobManager:
    return job_manager


def current_user(request: Request, db: Annotated[Session, Depends(db_session)]) -> User:
    token = _bearer_token(request)
    if token is None:
        token = request.query_params.get("token")
    payload = decode_access_token(token) if token else None
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, payload["sub"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def _bearer_token(request: Request) -> str | None:
    header = request.headers.get("authorization")
    if not header:
        return None
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token
