from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.security import normalize_url


class SreCheckRequest(BaseModel):
    url: str = Field(min_length=8, max_length=512)
    timeout_seconds: float = Field(default=8.0, ge=1.0, le=30.0)
    latency_warning_ms: int = Field(default=1000, ge=100, le=10000)
    authorization_confirmed: bool

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return normalize_url(value)

    @model_validator(mode="after")
    def require_authorization(self) -> SreCheckRequest:
        if not self.authorization_confirmed:
            raise ValueError("Authorization confirmation is required before running an SRE check")
        return self


class DnsCheckResult(BaseModel):
    hostname: str
    resolved: bool
    addresses: list[str] = Field(default_factory=list)
    latency_ms: float
    error: str | None = None


class HttpCheckResult(BaseModel):
    reachable: bool
    status_code: int | None = None
    final_url: str | None = None
    latency_ms: float
    redirect_count: int = 0
    content_type: str | None = None
    server: str | None = None
    error: str | None = None


class TlsCheckResult(BaseModel):
    enabled: bool
    valid: bool
    protocol: str | None = None
    issuer: str | None = None
    expires_at: datetime | None = None
    days_remaining: int | None = None
    error: str | None = None


class SreProbe(BaseModel):
    name: str
    status: str = Field(pattern="^(pass|warn|fail)$")
    detail: str
    recommendation: str


class SreCheckResponse(BaseModel):
    url: str
    checked_at: datetime
    overall_status: str = Field(pattern="^(healthy|degraded|down)$")
    score: int = Field(ge=0, le=100)
    dns: DnsCheckResult
    http: HttpCheckResult
    tls: TlsCheckResult | None
    probes: list[SreProbe]

