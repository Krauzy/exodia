from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import SEVERITY_SCORES


class Severity(StrEnum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


def normalize_severity(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in SEVERITY_SCORES:
        return "info"
    return normalized


def risk_score_for_severities(values: list[str]) -> int:
    return sum(SEVERITY_SCORES.get(normalize_severity(value), 0) for value in values)


class FindingBase(BaseModel):
    title: str = Field(min_length=3, max_length=240)
    description: str = Field(min_length=3)
    severity: Severity
    evidence: dict[str, Any] = Field(default_factory=dict)
    recommendation: str = Field(min_length=3)

    @field_validator("severity", mode="before")
    @classmethod
    def normalize(cls, value: str) -> str:
        return normalize_severity(str(value))


class FindingRead(FindingBase):
    id: str
    scan_id: str
    module_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    detail: str
