from __future__ import annotations

from typing import Any

from app.modules.base import Finding, SecurityModule
from app.schemas.common import Severity
from app.schemas.modules import ModuleParameter, ModuleResult
from app.schemas.sre import SreCheckRequest, SreProbe
from app.services.sre import run_sre_check


class SreSecurityModule(SecurityModule):
    probe_name: str
    category = "sre"
    tags = ["SRE"]
    default_severity = Severity.low
    parameters = [
        ModuleParameter(name="timeout_seconds", label="Timeout seconds", type="number", default=8.0),
        ModuleParameter(name="latency_warning_ms", label="Latency warning ms", type="number", default=1000),
    ]

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        payload = SreCheckRequest(
            url=target,
            timeout_seconds=float(options.get("timeout_seconds", 8.0)),
            latency_warning_ms=int(options.get("latency_warning_ms", 1000)),
            authorization_confirmed=True,
        )
        result = await run_sre_check(payload)
        probe = next((item for item in result.probes if item.name == self.probe_name), None)
        findings = [self._finding_for_probe(probe)] if probe and probe.status != "pass" else []
        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data=result.model_dump(mode="json"),
        )

    def _finding_for_probe(self, probe: SreProbe) -> Finding:
        severity = Severity.low if probe.status == "warn" else Severity.medium
        if probe.status == "fail" and probe.name in {"DNS resolution", "HTTP availability"}:
            severity = Severity.high
        return Finding(
            title=f"SRE probe warning: {probe.name}",
            description=probe.detail,
            severity=severity,
            evidence={"probe": probe.name, "status": probe.status},
            recommendation=probe.recommendation,
        )


class SreDnsModule(SreSecurityModule):
    id = "sre_dns"
    name = "SRE DNS Resolution"
    description = "Checks whether the site hostname resolves and records DNS latency."
    probe_name = "DNS resolution"
    default_severity = Severity.high


class SreHttpModule(SreSecurityModule):
    id = "sre_http"
    name = "SRE HTTP Availability"
    description = "Checks bounded HTTP reachability, response code, and server availability."
    probe_name = "HTTP availability"
    default_severity = Severity.high


class SreLatencyModule(SreSecurityModule):
    id = "sre_latency"
    name = "SRE Latency Budget"
    description = "Checks observed HTTP latency against an operational warning threshold."
    probe_name = "Latency budget"


class SreRedirectModule(SreSecurityModule):
    id = "sre_redirects"
    name = "SRE Redirect Behavior"
    description = "Checks redirect chain length for operational reliability issues."
    probe_name = "Redirect behavior"


class SreTlsModule(SreSecurityModule):
    id = "sre_tls"
    name = "SRE TLS Health"
    description = "Checks certificate validity, issuer, protocol, and expiration health for HTTPS targets."
    probe_name = "TLS health"
    default_severity = Severity.medium
