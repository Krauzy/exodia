from __future__ import annotations

from typing import Any

from app.core.constants import REPORT_FORMATS
from app.reports.exporters import build_report_payload, export_html, export_json, export_markdown


def generate_report(scan: Any, report_format: str) -> str:
    normalized = report_format.lower()
    if normalized not in REPORT_FORMATS:
        raise ValueError("Unsupported report format")
    payload = build_report_payload(scan)
    if normalized == "json":
        return export_json(payload)
    if normalized == "markdown":
        return export_markdown(payload)
    return export_html(payload)
