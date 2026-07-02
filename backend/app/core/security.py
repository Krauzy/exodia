from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from app.core.constants import ALLOWED_TARGET_PROTOCOLS

HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?$"
)


def sanitize_text(value: str, max_length: int = 500) -> str:
    normalized = " ".join(value.strip().split())
    return normalized[:max_length]


def normalize_url(value: str) -> str:
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme.lower() not in ALLOWED_TARGET_PROTOCOLS:
        raise ValueError("Only http and https targets are allowed")
    if not parsed.netloc:
        raise ValueError("Target URL must include a host")
    return value.rstrip("/")


def is_valid_host(value: str) -> bool:
    candidate = value.strip()
    if not candidate:
        return False
    try:
        ipaddress.ip_address(candidate)
        return True
    except ValueError:
        return bool(HOSTNAME_RE.match(candidate))


def hostname_from_target(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme and parsed.hostname:
        return parsed.hostname
    if is_valid_host(value):
        return value.strip().rstrip(".")
    raise ValueError("Could not resolve hostname from target")


def validate_target_value(target_type: str, value: str) -> str:
    if target_type in {"web", "api"}:
        return normalize_url(value)
    if target_type == "host":
        if not is_valid_host(value):
            raise ValueError("Host targets must be a valid IP address or hostname")
        return value.strip().rstrip(".")
    raise ValueError("Invalid target type")

