from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import current_user, db_session
from app.database.models import CustomModule, ModuleExecutionLog, Scan, Target, User
from app.jobs.manager import job_manager
from app.modules.custom_interceptor import custom_id_from_module_id
from app.plugins.registry import module_registry
from app.schemas.scans import ScanCreate, ScanLogRead, ScanRead

router = APIRouter(prefix="/scans", tags=["scans"])
DbSession = Annotated[Session, Depends(db_session)]
CurrentUser = Annotated[User, Depends(current_user)]


@router.get("", response_model=list[ScanRead])
def list_scans(db: DbSession, user: CurrentUser) -> list[Scan]:
    return (
        db.query(Scan)
        .options(selectinload(Scan.findings))
        .filter(Scan.user_id == user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )


@router.post("", response_model=ScanRead, status_code=status.HTTP_201_CREATED)
async def create_scan(payload: ScanCreate, db: DbSession, user: CurrentUser) -> Scan:
    if not payload.authorization_confirmed:
        raise HTTPException(status_code=400, detail="Authorization confirmation is required before starting a scan")
    target = db.query(Target).filter(Target.id == payload.target_id, Target.user_id == user.id).one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    if not target.active:
        raise HTTPException(status_code=400, detail="Target is inactive")

    unknown = [
        module_id
        for module_id in payload.modules
        if module_id not in module_registry.ids() and not _custom_module_exists(db, user.id, module_id)
    ]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown modules: {', '.join(unknown)}")

    scan = Scan(
        user_id=user.id,
        target_id=payload.target_id,
        modules=payload.modules,
        status="pending",
        authorization_confirmed=True,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    job_manager.start_scan(scan.id, payload.options)
    return scan


def _custom_module_exists(db: Session, user_id: str, module_id: str) -> bool:
    custom_id = custom_id_from_module_id(module_id)
    if custom_id is None:
        return False
    return (
        db.query(CustomModule)
        .filter(CustomModule.id == custom_id, CustomModule.user_id == user_id, CustomModule.active.is_(True))
        .one_or_none()
        is not None
    )


@router.get("/{scan_id}", response_model=ScanRead)
def get_scan(scan_id: str, db: DbSession, user: CurrentUser) -> Scan:
    scan = (
        db.query(Scan)
        .options(selectinload(Scan.findings))
        .filter(Scan.id == scan_id, Scan.user_id == user.id)
        .one_or_none()
    )
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/logs", response_model=list[ScanLogRead])
def get_scan_logs(scan_id: str, db: DbSession, user: CurrentUser) -> list[ModuleExecutionLog]:
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).one_or_none()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan.logs


@router.post("/{scan_id}/cancel")
async def cancel_scan(scan_id: str, db: DbSession, user: CurrentUser) -> dict[str, bool]:
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).one_or_none()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    canceled = await job_manager.cancel_scan(scan_id)
    return {"canceled": canceled}
