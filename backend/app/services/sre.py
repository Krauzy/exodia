from __future__ import annotations

import asyncio
import socket
import ssl
import time
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.security import hostname_from_target
from app.schemas.sre import (
    DnsCheckResult,
    HttpCheckResult,
    SreCheckRequest,
    SreCheckResponse,
    SreProbe,
    TlsCheckResult,
)


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 2)


async def _resolve_dns(hostname: str) -> DnsCheckResult:
    started = time.perf_counter()
    try:
        results = await asyncio.to_thread(socket.getaddrinfo, hostname, None, type=socket.SOCK_STREAM)
        addresses = sorted({str(item[4][0]) for item in results})
        return DnsCheckResult(
            hostname=hostname,
            resolved=bool(addresses),
            addresses=addresses,
            latency_ms=_elapsed_ms(started),
        )
    except Exception as exc:
        return DnsCheckResult(
            hostname=hostname,
            resolved=False,
            latency_ms=_elapsed_ms(started),
            error=type(exc).__name__,
        )


async def _check_http(payload: SreCheckRequest) -> HttpCheckResult:
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(payload.timeout_seconds),
            follow_redirects=True,
            headers={"User-Agent": "Exodia SRE Checker/0.1"},
        ) as client:
            response = await client.get(payload.url)
        return HttpCheckResult(
            reachable=True,
            status_code=response.status_code,
            final_url=str(response.url),
            latency_ms=_elapsed_ms(started),
            redirect_count=len(response.history),
            content_type=response.headers.get("content-type"),
            server=response.headers.get("server"),
        )
    except Exception as exc:
        return HttpCheckResult(
            reachable=False,
            latency_ms=_elapsed_ms(started),
            error=type(exc).__name__,
        )


def _read_tls(hostname: str, port: int, timeout_seconds: float) -> dict[str, Any]:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=timeout_seconds) as tcp:
        with context.wrap_socket(tcp, server_hostname=hostname) as tls:
            cert = tls.getpeercert()
            protocol = tls.version()
    return {"certificate": cert, "protocol": protocol}


async def _check_tls(url: str, timeout_seconds: float) -> TlsCheckResult | None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return None
    hostname = hostname_from_target(url)
    port = parsed.port or 443
    try:
        data = await asyncio.to_thread(_read_tls, hostname, port, timeout_seconds)
    except Exception as exc:
        return TlsCheckResult(enabled=True, valid=False, error=type(exc).__name__)

    cert = data["certificate"]
    issuer = dict(item[0] for item in cert.get("issuer", [])) if cert.get("issuer") else {}
    expires_at = None
    days_remaining = None
    not_after = cert.get("notAfter")
    if not_after:
        expires_at = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
        days_remaining = (expires_at - datetime.now(UTC)).days
    return TlsCheckResult(
        enabled=True,
        valid=days_remaining is None or days_remaining >= 0,
        protocol=data["protocol"],
        issuer=issuer.get("organizationName") or issuer.get("commonName"),
        expires_at=expires_at,
        days_remaining=days_remaining,
    )


def _build_probes(
    dns: DnsCheckResult,
    http: HttpCheckResult,
    tls: TlsCheckResult | None,
    latency_warning_ms: int,
) -> list[SreProbe]:
    probes = [
        SreProbe(
            name="DNS resolution",
            status="pass" if dns.resolved else "fail",
            detail=f"{len(dns.addresses)} address(es) resolved" if dns.resolved else f"DNS failed: {dns.error}",
            recommendation="Confirm authoritative DNS records and resolver reachability.",
        ),
        SreProbe(
            name="HTTP availability",
            status="pass" if http.reachable and http.status_code and http.status_code < 500 else "fail",
            detail=(
                f"HTTP {http.status_code} in {http.latency_ms} ms"
                if http.reachable
                else f"HTTP request failed: {http.error}"
            ),
            recommendation="Investigate upstream service health, routing, and application error budgets.",
        ),
        SreProbe(
            name="Latency budget",
            status="pass" if http.reachable and http.latency_ms <= latency_warning_ms else "warn",
            detail=f"Observed {http.latency_ms} ms, warning threshold {latency_warning_ms} ms",
            recommendation="Check CDN, origin saturation, dependency latency, and regional routing.",
        ),
        SreProbe(
            name="Redirect behavior",
            status="pass" if http.redirect_count <= 2 else "warn",
            detail=f"{http.redirect_count} redirect(s) followed",
            recommendation="Keep redirect chains short to reduce user-visible latency and failure modes.",
        ),
    ]
    if tls is not None:
        if not tls.valid:
            tls_status = "fail"
            tls_detail = f"TLS validation failed: {tls.error}"
        elif tls.days_remaining is not None and tls.days_remaining <= 14:
            tls_status = "warn"
            tls_detail = f"Certificate expires in {tls.days_remaining} day(s)"
        else:
            tls_status = "pass"
            tls_detail = f"{tls.protocol or 'TLS'} certificate is valid"
        probes.append(
            SreProbe(
                name="TLS health",
                status=tls_status,
                detail=tls_detail,
                recommendation="Keep certificates renewed, trusted, and monitored before expiration.",
            )
        )
    return probes


def _score(probes: list[SreProbe]) -> int:
    score = 100
    for probe in probes:
        if probe.status == "warn":
            score -= 15
        elif probe.status == "fail":
            score -= 35
    return max(0, score)


def _overall_status(score: int, probes: list[SreProbe]) -> str:
    if any(probe.status == "fail" and probe.name in {"DNS resolution", "HTTP availability"} for probe in probes):
        return "down"
    if score < 90 or any(probe.status == "warn" for probe in probes):
        return "degraded"
    return "healthy"


async def run_sre_check(payload: SreCheckRequest) -> SreCheckResponse:
    hostname = hostname_from_target(payload.url)
    dns, http, tls = await asyncio.gather(
        _resolve_dns(hostname),
        _check_http(payload),
        _check_tls(payload.url, payload.timeout_seconds),
    )
    probes = _build_probes(dns, http, tls, payload.latency_warning_ms)
    score = _score(probes)
    return SreCheckResponse(
        url=payload.url,
        checked_at=datetime.now(UTC),
        overall_status=_overall_status(score, probes),
        score=score,
        dns=dns,
        http=http,
        tls=tls,
        probes=probes,
    )
