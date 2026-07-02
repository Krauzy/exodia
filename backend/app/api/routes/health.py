from fastapi import APIRouter

from app.core.constants import APP_NAME, APP_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}

