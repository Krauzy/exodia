from fastapi import APIRouter

from app.schemas.sre import SreCheckRequest, SreCheckResponse
from app.services.sre import run_sre_check

router = APIRouter(prefix="/sre", tags=["sre"])


@router.post("/check", response_model=SreCheckResponse)
async def check_site(payload: SreCheckRequest) -> SreCheckResponse:
    return await run_sre_check(payload)

