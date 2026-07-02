from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import db_session
from app.database.models import ModuleExecutionLog, Scan, Target
from app.jobs.manager import job_manager
from app.plugins.registry import module_registry
from app.schemas.scans import ScanCreate, ScanLogRead, ScanRead

router = APIRouter(prefix="/scans", tags=["scans"])
DbSession = Annotated[Session, Depends(db_session)]


@router.get("", response_model=list[ScanRead])
def list_scans(db: DbSession) -> list[Scan]:
    return (
        db.query(Scan)
        .options(selectinload(Scan.findings))
        .order_by(Scan.created_at.desc())
        .all()
    )


@router.post("", response_model=ScanRead, status_code=status.HTTP_201_CREATED)
async def create_scan(payload: ScanCreate, db: DbSession) -> Scan:
    if not payload.authorization_confirmed:
        raise HTTPException(status_code=400, detail="Authorization confirmation is required before starting a scan")
    target = db.get(Target, payload.target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    if not target.active:
        raise HTTPException(status_code=400, detail="Target is inactive")

    unknown = [module_id for module_id in payload.modules if module_id not in module_registry.ids()]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown modules: {', '.join(unknown)}")

    scan = Scan(
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


@router.get("/{scan_id}", response_model=ScanRead)
def get_scan(scan_id: str, db: DbSession) -> Scan:
    scan = db.query(Scan).options(selectinload(Scan.findings)).filter(Scan.id == scan_id).one_or_none()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/logs", response_model=list[ScanLogRead])
def get_scan_logs(scan_id: str, db: DbSession) -> list[ModuleExecutionLog]:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan.logs


@router.post("/{scan_id}/cancel")
async def cancel_scan(scan_id: str, db: DbSession) -> dict[str, bool]:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    canceled = await job_manager.cancel_scan(scan_id)
    return {"canceled": canceled}
