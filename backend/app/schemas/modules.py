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
    default_severity: Severity
    parameters: list[ModuleParameter] = Field(default_factory=list)


class ModuleResult(BaseModel):
    module_id: str
    target: str
    findings: Sequence[FindingBase] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)
