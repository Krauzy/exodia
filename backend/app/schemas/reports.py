from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import REPORT_FORMATS


class ReportGenerateRequest(BaseModel):
    format: str = Field(default="html")

    @field_validator("format")
    @classmethod
    def validate_format(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in REPORT_FORMATS:
            raise ValueError("Unsupported report format")
        return normalized


class ReportRead(BaseModel):
    id: str
    user_id: str | None
    scan_id: str
    format: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
