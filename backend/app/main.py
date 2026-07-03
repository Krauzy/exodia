from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, events, health, modules, pentest, reports, scans, settings, sre, targets
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.database.session import init_db
from app.plugins.loader import load_local_plugins
from app.plugins.registry import module_registry

API_ROUTERS: tuple[APIRouter, ...] = (
    health.router,
    auth.router,
    modules.router,
    targets.router,
    scans.router,
    events.router,
    reports.router,
    sre.router,
    pentest.router,
    settings.router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings_obj = get_settings()
    init_db()
    load_local_plugins(settings_obj.plugins_dir, module_registry)
    yield


def create_app() -> FastAPI:
    configure_logging()
    settings_obj = get_settings()
    app = FastAPI(
        title=settings_obj.app_name,
        version=settings_obj.app_version,
        description="Local defensive audit platform for authorized environments.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings_obj.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings_obj.api_prefix.rstrip("/")
    for router in API_ROUTERS:
        app.include_router(router, prefix=api_prefix)

    if not api_prefix:
        for router in API_ROUTERS:
            app.include_router(router, prefix="/api", include_in_schema=False)

    return app


app = create_app()
