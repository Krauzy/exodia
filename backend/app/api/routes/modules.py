from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import current_user, db_session, get_module_registry
from app.core.security import sanitize_text
from app.database.models import CustomModule, User
from app.modules.custom_interceptor import (
    CustomModuleValidationError,
    module_id_for_custom,
    validate_interceptor_code,
)
from app.plugins.registry import ModuleRegistry
from app.schemas.common import Severity, normalize_severity
from app.schemas.modules import CustomModuleCreate, CustomModuleRead, ModuleInfo

router = APIRouter(prefix="/modules", tags=["modules"])
RegistryDep = Annotated[ModuleRegistry, Depends(get_module_registry)]
DbSession = Annotated[Session, Depends(db_session)]
CurrentUser = Annotated[User, Depends(current_user)]


@router.get("", response_model=list[ModuleInfo])
def list_modules(registry: RegistryDep, db: DbSession, user: CurrentUser) -> list[ModuleInfo]:
    builtins = registry.list()
    custom = [
        _custom_module_info(module)
        for module in db.query(CustomModule)
        .filter(CustomModule.user_id == user.id, CustomModule.active.is_(True))
        .order_by(CustomModule.created_at.desc())
        .all()
    ]
    return builtins + custom


@router.post("", response_model=CustomModuleRead, status_code=status.HTTP_201_CREATED)
def create_custom_module(payload: CustomModuleCreate, db: DbSession, user: CurrentUser) -> CustomModuleRead:
    try:
        validate_interceptor_code(payload.code)
    except CustomModuleValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    tags = _normalize_tags(payload.tags)
    module = CustomModule(
        user_id=user.id,
        name=payload.name.strip().lower(),
        title=sanitize_text(payload.title, max_length=160),
        description=sanitize_text(payload.description, max_length=2000),
        severity=payload.severity.value,
        tags=tags,
        code=payload.code,
    )
    db.add(module)
    db.commit()
    db.refresh(module)
    return _custom_module_read(module)


def _custom_module_info(module: CustomModule) -> ModuleInfo:
    tags = list(dict.fromkeys(["CUSTOM", *module.tags]))
    return ModuleInfo(
        id=module_id_for_custom(module.id),
        name=module.title,
        description=module.description,
        category="custom",
        tags=tags,
        default_severity=Severity(normalize_severity(module.severity)),
        parameters=[],
    )


def _custom_module_read(module: CustomModule) -> CustomModuleRead:
    return CustomModuleRead(
        id=module.id,
        module_id=module_id_for_custom(module.id),
        name=module.name,
        title=module.title,
        description=module.description,
        severity=Severity(normalize_severity(module.severity)),
        tags=module.tags,
        code=module.code,
        active=module.active,
    )


def _normalize_tags(values: list[str]) -> list[str]:
    tags = ["CUSTOM"]
    for value in values[:12]:
        tag = sanitize_text(value, max_length=32).upper()
        if tag and tag not in tags:
            tags.append(tag)
    return tags
