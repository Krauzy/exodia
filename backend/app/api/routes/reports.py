from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import current_user, db_session
from app.database.models import Report, Scan, User
from app.reports.generator import generate_report
from app.schemas.reports import ReportGenerateRequest, ReportRead

router = APIRouter(prefix="/reports", tags=["reports"])
DbSession = Annotated[Session, Depends(db_session)]
CurrentUser = Annotated[User, Depends(current_user)]


@router.get("", response_model=list[ReportRead])
def list_reports(db: DbSession, user: CurrentUser) -> list[Report]:
    return db.query(Report).filter(Report.user_id == user.id).order_by(Report.created_at.desc()).all()


@router.get("/{report_id}", response_model=ReportRead)
def get_report(report_id: str, db: DbSession, user: CurrentUser) -> Report:
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == user.id).one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/{scan_id}/generate", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
def generate_scan_report(scan_id: str, payload: ReportGenerateRequest, db: DbSession, user: CurrentUser) -> Report:
    scan = (
        db.query(Scan)
        .options(selectinload(Scan.target), selectinload(Scan.findings))
        .filter(Scan.id == scan_id, Scan.user_id == user.id)
        .one_or_none()
    )
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    content = generate_report(scan, payload.format)
    report = Report(user_id=user.id, scan_id=scan.id, format=payload.format, content=content)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
