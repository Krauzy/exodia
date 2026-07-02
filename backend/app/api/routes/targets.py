from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import db_session
from app.database.models import Target
from app.schemas.targets import TargetCreate, TargetRead, TargetUpdate

router = APIRouter(prefix="/targets", tags=["targets"])
DbSession = Annotated[Session, Depends(db_session)]


@router.get("", response_model=list[TargetRead])
def list_targets(db: DbSession) -> list[Target]:
    return db.query(Target).order_by(Target.created_at.desc()).all()


@router.post("", response_model=TargetRead, status_code=status.HTTP_201_CREATED)
def create_target(payload: TargetCreate, db: DbSession) -> Target:
    target = Target(**payload.model_dump())
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


@router.get("/{target_id}", response_model=TargetRead)
def get_target(target_id: str, db: DbSession) -> Target:
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@router.put("/{target_id}", response_model=TargetRead)
def update_target(target_id: str, payload: TargetUpdate, db: DbSession) -> Target:
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    data = payload.model_dump(exclude_unset=True)
    if ("target_type" in data) ^ ("value" in data):
        target_type = data.get("target_type", target.target_type)
        value = data.get("value", target.value)
        from app.core.security import validate_target_value

        data["value"] = validate_target_value(target_type, value)
    for key, value in data.items():
        setattr(target, key, value)
    db.commit()
    db.refresh(target)
    return target


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_target(target_id: str, db: DbSession) -> None:
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    db.delete(target)
    db.commit()
