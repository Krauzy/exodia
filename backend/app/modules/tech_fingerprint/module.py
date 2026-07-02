from __future__ import annotations

import re
from typing import Any

import httpx

from app.modules.base import Finding, SecurityModule
from app.schemas.common import Severity
from app.schemas.modules import ModuleResult

META_GENERATOR_RE = re.compile(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']', re.I)


class TechnologyFingerprint(SecurityModule):
    id = "tech_fingerprint"
    name = "Technology Fingerprint"
    description = "Passively identifies public technology hints from headers and HTML."
    category = "web"
    default_severity = Severity.info

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        timeout = float(options.get("timeout", 8.0))
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout), follow_redirects=True) as client:
            response = await client.get(target, headers={"User-Agent": "Exodia Defensive Auditor/0.1"})

        headers = {key.lower(): value for key, value in response.headers.items()}
        body = response.text[:200_000]
        technologies: dict[str, str] = {}
        for header in ("server", "x-powered-by", "x-generator"):
            if header in headers:
                technologies[header] = headers[header]

        generator = META_GENERATOR_RE.search(body)
        if generator:
            technologies["meta-generator"] = generator.group(1)
        if "__NEXT_DATA__" in body:
            technologies["framework-nextjs"] = "Next.js public marker"
        if "wp-content" in body:
            technologies["cms-wordpress"] = "WordPress public asset path"
        if "data-reactroot" in body or "react-dom" in body:
            technologies["framework-react"] = "React public marker"

        findings = [
            Finding(
                title="Public technology hints detected",
                description="The response exposes passive technology indicators.",
                severity=Severity.info,
                evidence={"technologies": technologies, "url": str(response.url)},
                recommendation="Review exposed version banners and remove unnecessary framework/version disclosure.",
            )
        ] if technologies else []

        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data={"status_code": response.status_code, "technologies": technologies},
        )

