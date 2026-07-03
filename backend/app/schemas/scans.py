from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import MAX_SCAN_MODULES, SCAN_STATUSES
from app.schemas.common import FindingRead


class ScanCreate(BaseModel):
    target_id: str
    modules: list[str] = Field(min_length=1, max_length=MAX_SCAN_MODULES)
    authorization_confirmed: bool
    options: dict[str, dict[str, Any]] = Field(default_factory=dict)

    @field_validator("modules")
    @classmethod
    def unique_modules(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))


class ScanRead(BaseModel):
    id: str
    user_id: str | None
    target_id: str
    modules: list[str]
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    current_module: str | None
    risk_score: float
    authorization_confirmed: bool
    created_at: datetime
    findings: list[FindingRead] = Field(default_factory=list)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in SCAN_STATUSES:
            return "failed"
        return value

    model_config = ConfigDict(from_attributes=True)


class ScanLogRead(BaseModel):
    id: int
    scan_id: str
    module_id: str | None
    event_type: str
    message: str
    payload: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
