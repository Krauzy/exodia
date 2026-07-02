from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import FindingBase, Severity
from app.schemas.modules import ModuleInfo, ModuleParameter, ModuleResult


class Finding(FindingBase):
    pass


class SecurityModule(ABC):
    id: str
    name: str
    description: str
    category: str
    default_severity: Severity = Severity.info
    parameters: list[ModuleParameter] = []

    def info(self) -> ModuleInfo:
        return ModuleInfo(
            id=self.id,
            name=self.name,
            description=self.description,
            category=self.category,
            default_severity=self.default_severity,
            parameters=self.parameters,
        )

    @abstractmethod
    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        raise NotImplementedError


class HttpObservation(BaseModel):
    url: str
    status_code: int | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    body_preview: str = ""

