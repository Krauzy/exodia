from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import events, health, modules, reports, scans, settings, sre, targets
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.database.session import init_db
from app.plugins.loader import load_local_plugins
from app.plugins.registry import module_registry


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
        allow_origins=settings_obj.allowed_origins + ["http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(modules.router)
    app.include_router(targets.router)
    app.include_router(scans.router)
    app.include_router(events.router)
    app.include_router(reports.router)
    app.include_router(sre.router)
    app.include_router(settings.router)
    return app


app = create_app()
