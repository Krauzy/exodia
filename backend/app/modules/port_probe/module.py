from __future__ import annotations

import asyncio
from typing import Any

from app.core.constants import DEFAULT_SAFE_PORTS
from app.core.security import hostname_from_target
from app.modules.base import Finding, SecurityModule
from app.schemas.common import Severity
from app.schemas.modules import ModuleParameter, ModuleResult


class SafePortProbe(SecurityModule):
    id = "port_probe"
    name = "Safe Port Probe"
    description = "Performs a low-rate connection check against a small allowlisted port set."
    category = "network"
    default_severity = Severity.info
    parameters = [
        ModuleParameter(
            name="ports",
            label="Ports",
            type="list",
            required=False,
            default=DEFAULT_SAFE_PORTS,
            description="Small allowlisted port list for authorized environments.",
        ),
        ModuleParameter(
            name="timeout",
            label="Timeout",
            type="number",
            required=False,
            default=1.5,
            description="Connection timeout in seconds.",
        ),
    ]

    async def _probe_port(self, hostname: str, port: int, timeout: float) -> bool:
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(hostname, port), timeout=timeout)
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        hostname = hostname_from_target(target)
        requested_ports = options.get("ports") or DEFAULT_SAFE_PORTS
        ports = [int(port) for port in requested_ports if int(port) in DEFAULT_SAFE_PORTS][: len(DEFAULT_SAFE_PORTS)]
        timeout = float(options.get("timeout", 1.5))
        open_ports: list[int] = []

        for port in ports:
            is_open = await self._probe_port(hostname, port, timeout)
            if is_open:
                open_ports.append(port)
            await asyncio.sleep(0.2)

        findings = [
            Finding(
                title="Open services detected",
                description="The safe port probe observed open TCP ports from the configured small port list.",
                severity=Severity.info,
                evidence={"host": hostname, "open_ports": open_ports},
                recommendation="Confirm that each exposed service is expected, patched, and access-controlled.",
            )
        ] if open_ports else []

        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data={"host": hostname, "ports_checked": ports, "open_ports": open_ports},
        )

