from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import MAX_TAGS, TARGET_TYPES
from app.core.security import sanitize_text, validate_target_value


class TargetBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    target_type: str = Field(pattern="^(web|api|host)$")
    value: str = Field(min_length=2, max_length=512)
    description: str = Field(default="", max_length=1000)
    authorization_scope: str = Field(min_length=8, max_length=2000)
    tags: list[str] = Field(default_factory=list, max_length=MAX_TAGS)
    active: bool = True

    @field_validator("name", "description", "authorization_scope", mode="before")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return sanitize_text(str(value), max_length=2000)

    @field_validator("tags", mode="before")
    @classmethod
    def clean_tags(cls, value: list[str] | None) -> list[str]:
        if not value:
            return []
        cleaned = []
        for tag in value[:MAX_TAGS]:
            safe = sanitize_text(str(tag), max_length=32).lower()
            if safe and safe not in cleaned:
                cleaned.append(safe)
        return cleaned

    @model_validator(mode="after")
    def validate_target(self) -> TargetBase:
        if self.target_type not in TARGET_TYPES:
            raise ValueError("Unsupported target type")
        self.value = validate_target_value(self.target_type, self.value)
        return self


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    target_type: str | None = Field(default=None, pattern="^(web|api|host)$")
    value: str | None = Field(default=None, min_length=2, max_length=512)
    description: str | None = Field(default=None, max_length=1000)
    authorization_scope: str | None = Field(default=None, min_length=8, max_length=2000)
    tags: list[str] | None = Field(default=None, max_length=MAX_TAGS)
    active: bool | None = None

    @model_validator(mode="after")
    def validate_partial_target(self) -> TargetUpdate:
        if self.target_type and self.value:
            self.value = validate_target_value(self.target_type, self.value)
        return self


class TargetRead(TargetBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

