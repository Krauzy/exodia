from __future__ import annotations

from typing import Any, TypedDict

import httpx

from app.core.constants import DEFAULT_HTTP_TIMEOUT_SECONDS
from app.modules.base import Finding, SecurityModule
from app.schemas.common import Severity
from app.schemas.modules import ModuleResult


class HeaderRule(TypedDict):
    title: str
    severity: Severity
    recommendation: str


REQUIRED_HEADERS: dict[str, HeaderRule] = {
    "content-security-policy": {
        "title": "Missing Content-Security-Policy",
        "severity": Severity.medium,
        "recommendation": "Define a restrictive Content-Security-Policy suited to the application.",
    },
    "strict-transport-security": {
        "title": "Missing Strict-Transport-Security",
        "severity": Severity.medium,
        "recommendation": "Enable HSTS for HTTPS targets after validating subdomain readiness.",
    },
    "x-frame-options": {
        "title": "Missing X-Frame-Options",
        "severity": Severity.low,
        "recommendation": "Set X-Frame-Options or use CSP frame-ancestors to control framing.",
    },
    "x-content-type-options": {
        "title": "Missing X-Content-Type-Options",
        "severity": Severity.low,
        "recommendation": "Set X-Content-Type-Options to nosniff.",
    },
    "referrer-policy": {
        "title": "Missing Referrer-Policy",
        "severity": Severity.low,
        "recommendation": "Set a Referrer-Policy that limits sensitive URL disclosure.",
    },
    "permissions-policy": {
        "title": "Missing Permissions-Policy",
        "severity": Severity.info,
        "recommendation": "Define a Permissions-Policy to disable unused browser features.",
    },
}


class WebSecurityHeadersAnalyzer(SecurityModule):
    id = "web_headers"
    name = "Web Security Headers Analyzer"
    description = "Passively checks public HTTP response headers for common defensive controls."
    category = "web"
    default_severity = Severity.low

    def __init__(self, client_factory: Any | None = None) -> None:
        self.client_factory = client_factory

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        timeout = float(options.get("timeout", DEFAULT_HTTP_TIMEOUT_SECONDS))
        headers = {"User-Agent": "Exodia Defensive Auditor/0.1"}
        if self.client_factory:
            client = self.client_factory()
            close_client = False
        else:
            client = httpx.AsyncClient(timeout=httpx.Timeout(timeout), follow_redirects=True, headers=headers)
            close_client = True
        try:
            response = await client.get(target)
        finally:
            if close_client:
                await client.aclose()

        normalized_headers = {key.lower(): value for key, value in response.headers.items()}
        findings: list[Finding] = []
        for header, metadata in REQUIRED_HEADERS.items():
            if header not in normalized_headers:
                findings.append(
                    Finding(
                        title=metadata["title"],
                        description=f"The response did not include {header}.",
                        severity=metadata["severity"],
                        evidence={"url": str(response.url), "status_code": response.status_code},
                        recommendation=metadata["recommendation"],
                    )
                )

        csp = normalized_headers.get("content-security-policy", "")
        if csp and "unsafe-inline" in csp:
            findings.append(
                Finding(
                    title="Content-Security-Policy allows unsafe-inline",
                    description=(
                        "The Content-Security-Policy contains unsafe-inline, "
                        "which weakens script/style controls."
                    ),
                    severity=Severity.low,
                    evidence={"content-security-policy": csp},
                    recommendation="Remove unsafe-inline where possible and migrate to nonces or hashes.",
                )
            )

        hsts = normalized_headers.get("strict-transport-security", "")
        if hsts and "max-age=0" in hsts.replace(" ", "").lower():
            findings.append(
                Finding(
                    title="Strict-Transport-Security is disabled",
                    description="The HSTS header advertises max-age=0.",
                    severity=Severity.medium,
                    evidence={"strict-transport-security": hsts},
                    recommendation="Use a positive HSTS max-age only after validating HTTPS readiness.",
                )
            )

        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data={
                "status_code": response.status_code,
                "url": str(response.url),
                "headers": dict(response.headers),
            },
        )
