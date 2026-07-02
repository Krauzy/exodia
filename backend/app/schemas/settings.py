from __future__ import annotations

from pydantic import BaseModel, Field


class SettingsRead(BaseModel):
    safe_mode: bool = True
    plugins_dir: str = "./plugins"
    http_timeout_seconds: float = 8.0
    max_concurrent_modules: int = 3


class SettingsUpdate(BaseModel):
    safe_mode: bool | None = None
    plugins_dir: str | None = Field(default=None, max_length=500)
    http_timeout_seconds: float | None = Field(default=None, ge=1, le=30)
    max_concurrent_modules: int | None = Field(default=None, ge=1, le=6)

