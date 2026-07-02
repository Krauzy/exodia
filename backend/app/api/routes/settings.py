from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import db_session
from app.core.config import get_settings
from app.database.models import AppSettings
from app.schemas.settings import SettingsRead, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])
DbSession = Annotated[Session, Depends(db_session)]


SETTINGS_KEY = "app"


def _defaults() -> SettingsRead:
    settings = get_settings()
    return SettingsRead(
        safe_mode=settings.safe_mode,
        plugins_dir=str(settings.plugins_dir),
        http_timeout_seconds=settings.http_timeout_seconds,
        max_concurrent_modules=settings.max_concurrent_modules,
    )


@router.get("", response_model=SettingsRead)
def get_app_settings(db: DbSession) -> SettingsRead:
    row = db.get(AppSettings, SETTINGS_KEY)
    defaults = _defaults().model_dump()
    if row is None:
        return SettingsRead(**defaults)
    defaults.update(row.value)
    return SettingsRead(**defaults)


@router.put("", response_model=SettingsRead)
def update_app_settings(payload: SettingsUpdate, db: DbSession) -> SettingsRead:
    current = get_app_settings(db).model_dump()
    current.update(payload.model_dump(exclude_unset=True, exclude_none=True))
    row = db.get(AppSettings, SETTINGS_KEY)
    if row is None:
        row = AppSettings(key=SETTINGS_KEY, value=current)
        db.add(row)
    else:
        row.value = current
    db.commit()
    return SettingsRead(**current)
