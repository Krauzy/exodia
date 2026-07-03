from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import current_user, db_session
from app.core.auth import create_access_token, hash_password, verify_password
from app.database.models import User
from app.schemas.auth import AuthToken, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])
DbSession = Annotated[Session, Depends(db_session)]
CurrentUser = Annotated[User, Depends(current_user)]


@router.post("/register", response_model=AuthToken, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: DbSession) -> AuthToken:
    existing = db.query(User).filter(User.username == payload.username).one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthToken(access_token=create_access_token(user.id), user=UserRead.model_validate(user))


@router.post("/login", response_model=AuthToken)
def login_user(payload: UserLogin, db: DbSession) -> AuthToken:
    user = db.query(User).filter(User.username == payload.username).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return AuthToken(access_token=create_access_token(user.id), user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
def read_current_user(user: CurrentUser) -> User:
    return user
