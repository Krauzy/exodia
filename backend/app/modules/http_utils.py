from __future__ import annotations

from urllib.parse import urljoin

import httpx

from app.core.constants import DEFAULT_HTTP_TIMEOUT_SECONDS


def absolute_url(target: str, path: str = "") -> str:
    if path:
        return urljoin(target.rstrip("/") + "/", path.lstrip("/"))
    return target


async def fetch_public_resource(
    url: str,
    timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    timeout = httpx.Timeout(timeout_seconds)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=headers or {"User-Agent": "Exodia Defensive Auditor/0.1"},
    ) as client:
        return await client.get(url)

