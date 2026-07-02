from __future__ import annotations

from typing import Any

import httpx

from app.modules.base import Finding, SecurityModule
from app.modules.http_utils import absolute_url
from app.schemas.common import Severity
from app.schemas.modules import ModuleResult


class SecurityTxtChecker(SecurityModule):
    id = "security_txt_checker"
    name = "Security.txt Checker"
    description = "Checks /.well-known/security.txt for disclosure contacts and policy metadata."
    category = "web"
    default_severity = Severity.info

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        url = absolute_url(target, "/.well-known/security.txt")
        timeout = float(options.get("timeout", 8.0))
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout), follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "Exodia Defensive Auditor/0.1"})

        if response.status_code >= 400:
            finding = Finding(
                title="Security.txt not found",
                description="The target did not publish a readable /.well-known/security.txt file.",
                severity=Severity.info,
                evidence={"url": url, "status_code": response.status_code},
                recommendation="Publish security.txt to document vulnerability disclosure contacts and policy.",
            )
            return ModuleResult(
                module_id=self.id,
                target=target,
                findings=[finding],
                raw_data={"status_code": response.status_code},
            )

        fields: dict[str, list[str]] = {}
        for line in response.text.splitlines():
            if ":" not in line or line.strip().startswith("#"):
                continue
            key, value = line.split(":", 1)
            fields.setdefault(key.strip().lower(), []).append(value.strip())

        findings = [
            Finding(
                title="Security.txt is available",
                description="The target publishes vulnerability disclosure metadata.",
                severity=Severity.info,
                evidence={"url": str(response.url), "fields": fields},
                recommendation="Keep security.txt current and align contacts with the disclosure policy.",
            )
        ]
        if "contact" not in fields:
            findings.append(
                Finding(
                    title="Security.txt has no Contact field",
                    description="The security.txt file is present but does not include a Contact field.",
                    severity=Severity.low,
                    evidence={"fields": fields},
                    recommendation="Add at least one Contact field as described by RFC 9116.",
                )
            )

        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data={"status_code": response.status_code, "fields": fields},
        )
