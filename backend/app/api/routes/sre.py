from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import current_user
from app.database.models import User
from app.schemas.sre import SreCheckRequest, SreCheckResponse
from app.services.sre import run_sre_check

router = APIRouter(prefix="/sre", tags=["sre"])
CurrentUser = Annotated[User, Depends(current_user)]


@router.post("/check", response_model=SreCheckResponse)
async def check_site(payload: SreCheckRequest, user: CurrentUser) -> SreCheckResponse:
    return await run_sre_check(payload)
