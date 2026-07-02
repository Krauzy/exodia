from __future__ import annotations

from typing import Any

import httpx

from app.modules.base import Finding, SecurityModule
from app.modules.http_utils import absolute_url
from app.schemas.common import Severity
from app.schemas.modules import ModuleResult


class RobotsTxtChecker(SecurityModule):
    id = "robots_checker"
    name = "Robots.txt Checker"
    description = "Fetches robots.txt and reports declared paths without treating them as access controls."
    category = "web"
    default_severity = Severity.info

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        url = absolute_url(target, "/robots.txt")
        timeout = float(options.get("timeout", 8.0))
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout), follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "Exodia Defensive Auditor/0.1"})

        if response.status_code == 404:
            return ModuleResult(module_id=self.id, target=target, findings=[], raw_data={"status_code": 404})

        directives = []
        for line in response.text.splitlines():
            clean = line.strip()
            if clean.lower().startswith(("allow:", "disallow:", "sitemap:")):
                directives.append(clean)

        findings = [
            Finding(
                title="Robots.txt is publicly available",
                description="Robots.txt exposes crawler directives. These entries are not security controls.",
                severity=Severity.info,
                evidence={"url": str(response.url), "directives": directives[:100]},
                recommendation="Do not rely on robots.txt to hide sensitive routes. Enforce authorization server-side.",
            )
        ] if directives else []

        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data={"status_code": response.status_code, "directives": directives},
        )

