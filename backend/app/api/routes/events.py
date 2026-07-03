from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import current_user, db_session
from app.database.models import Scan, User
from app.jobs.manager import job_manager

router = APIRouter(prefix="/events", tags=["events"])
DbSession = Annotated[Session, Depends(db_session)]
CurrentUser = Annotated[User, Depends(current_user)]


@router.get("/scans/{scan_id}")
async def stream_scan_events(scan_id: str, db: DbSession, user: CurrentUser) -> StreamingResponse:
    if db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).one_or_none() is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return StreamingResponse(
        job_manager.event_bus.stream(scan_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
