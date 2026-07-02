from __future__ import annotations

import asyncio
import socket
import ssl
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from app.core.security import hostname_from_target
from app.modules.base import Finding, SecurityModule
from app.schemas.common import Severity
from app.schemas.modules import ModuleResult


def _read_certificate(hostname: str, port: int, timeout: float) -> dict[str, Any]:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout) as tcp:
        with context.wrap_socket(tcp, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
            protocol = tls.version()
    return {"certificate": cert, "protocol": protocol}


class TlsAnalyzer(SecurityModule):
    id = "tls_analyzer"
    name = "TLS Analyzer"
    description = "Checks basic TLS certificate validity and protocol information."
    category = "transport"
    default_severity = Severity.low

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        timeout = float(options.get("timeout", 6.0))
        parsed = urlparse(target)
        hostname = hostname_from_target(target)
        port = parsed.port or 443
        findings: list[Finding] = []

        try:
            data = await asyncio.to_thread(_read_certificate, hostname, port, timeout)
        except Exception as exc:
            findings.append(
                Finding(
                    title="TLS connection failed",
                    description="The target did not complete a basic TLS handshake.",
                    severity=Severity.medium,
                    evidence={"host": hostname, "port": port, "error": type(exc).__name__},
                    recommendation=(
                        "Verify that TLS is enabled, publicly reachable from this environment, "
                        "and configured correctly."
                    ),
                )
            )
            return ModuleResult(
                module_id=self.id,
                target=target,
                findings=findings,
                raw_data={"host": hostname, "port": port},
            )

        cert = data["certificate"]
        not_after = cert.get("notAfter")
        issuer = dict(x[0] for x in cert.get("issuer", [])) if cert.get("issuer") else {}
        subject = dict(x[0] for x in cert.get("subject", [])) if cert.get("subject") else {}
        expires_at = None
        if not_after:
            expires_at = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
            days_left = (expires_at - datetime.now(UTC)).days
            if days_left < 0:
                findings.append(
                    Finding(
                        title="TLS certificate is expired",
                        description="The certificate expiration date is in the past.",
                        severity=Severity.high,
                        evidence={"expires_at": expires_at.isoformat()},
                        recommendation="Renew the certificate and validate the full chain.",
                    )
                )
            elif days_left <= 30:
                findings.append(
                    Finding(
                        title="TLS certificate expires soon",
                        description="The certificate expires within 30 days.",
                        severity=Severity.medium,
                        evidence={"expires_at": expires_at.isoformat(), "days_left": days_left},
                        recommendation="Schedule certificate renewal before expiration.",
                    )
                )

        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data={
                "host": hostname,
                "port": port,
                "protocol": data["protocol"],
                "issuer": issuer,
                "subject": subject,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )
