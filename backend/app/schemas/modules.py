from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import FindingBase, Severity


class ModuleParameter(BaseModel):
    name: str
    label: str
    type: str = Field(pattern="^(string|number|boolean|list)$")
    required: bool = False
    default: Any = None
    description: str = ""


class ModuleInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    tags: list[str] = Field(default_factory=list)
    default_severity: Severity
    parameters: list[ModuleParameter] = Field(default_factory=list)


class CustomModuleCreate(BaseModel):
    name: str = Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=8, max_length=2000)
    severity: Severity = Severity.info
    tags: list[str] = Field(default_factory=list, max_length=12)
    code: str = Field(min_length=40, max_length=8000)


class CustomModuleRead(BaseModel):
    id: str
    module_id: str
    name: str
    title: str
    description: str
    severity: Severity
    tags: list[str]
    code: str
    active: bool


class ModuleResult(BaseModel):
    module_id: str
    target: str
    findings: Sequence[FindingBase] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)
