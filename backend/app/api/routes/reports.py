from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import db_session
from app.database.models import Report, Scan
from app.reports.generator import generate_report
from app.schemas.reports import ReportGenerateRequest, ReportRead

router = APIRouter(prefix="/reports", tags=["reports"])
DbSession = Annotated[Session, Depends(db_session)]


@router.get("", response_model=list[ReportRead])
def list_reports(db: DbSession) -> list[Report]:
    return db.query(Report).order_by(Report.created_at.desc()).all()


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: str, db: DbSession) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{scan_id}/generate", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
def generate_scan_report(scan_id: str, payload: ReportGenerateRequest, db: DbSession) -> Report:
    scan = (
        db.query(Scan)
        .options(selectinload(Scan.target), selectinload(Scan.findings))
        .filter(Scan.id == scan_id)
        .one_or_none()
    )
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    content = generate_report(scan, payload.format)
    report = Report(scan_id=scan.id, format=payload.format, content=content)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
