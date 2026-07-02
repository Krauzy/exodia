from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.database.models import Scan
from app.database.session import SessionLocal
from app.jobs.manager import job_manager

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/scans/{scan_id}")
async def stream_scan_events(scan_id: str) -> StreamingResponse:
    with SessionLocal() as db:
        if db.get(Scan, scan_id) is None:
            raise HTTPException(status_code=404, detail="Scan not found")
    return StreamingResponse(
        job_manager.event_bus.stream(scan_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

