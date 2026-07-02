from __future__ import annotations

import html
import json
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from app.core.constants import AUTHORIZED_USE_DISCLAIMER


def _finding_to_dict(finding: Any) -> dict[str, Any]:
    return {
        "title": finding.title,
        "description": finding.description,
        "severity": finding.severity,
        "module_id": finding.module_id,
        "evidence": finding.evidence,
        "recommendation": finding.recommendation,
        "timestamp": finding.created_at.isoformat(),
    }


def build_report_payload(scan: Any) -> dict[str, Any]:
    findings = [_finding_to_dict(finding) for finding in scan.findings]
    counts = Counter(finding["severity"] for finding in findings)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "disclaimer": AUTHORIZED_USE_DISCLAIMER,
        "target": {
            "id": scan.target.id,
            "name": scan.target.name,
            "type": scan.target.target_type,
            "value": scan.target.value,
            "authorization_scope": scan.target.authorization_scope,
            "tags": scan.target.tags,
        },
        "scan": {
            "id": scan.id,
            "status": scan.status,
            "modules": scan.modules,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
            "risk_score": scan.risk_score,
        },
        "summary": {
            "total_findings": len(findings),
            "by_severity": {
                severity: counts.get(severity, 0)
                for severity in ["critical", "high", "medium", "low", "info"]
            },
        },
        "findings": findings,
    }


def export_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def export_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Exodia Security Report - {payload['target']['name']}",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        "## Authorized Use Disclaimer",
        "",
        payload["disclaimer"],
        "",
        "## Target",
        "",
        f"- Type: `{payload['target']['type']}`",
        f"- Value: `{payload['target']['value']}`",
        f"- Authorized scope: {payload['target']['authorization_scope']}",
        "",
        "## Executive Summary",
        "",
        f"- Scan status: `{payload['scan']['status']}`",
        f"- Risk score: `{payload['scan']['risk_score']}`",
        f"- Findings: `{payload['summary']['total_findings']}`",
        "",
        "## Findings By Severity",
        "",
    ]
    for severity, count in payload["summary"]["by_severity"].items():
        lines.append(f"- {severity}: {count}")
    lines.extend(["", "## Findings", ""])
    if not payload["findings"]:
        lines.append("No findings were detected by the selected defensive modules.")
    for finding in payload["findings"]:
        lines.extend(
            [
                f"### [{finding['severity']}] {finding['title']}",
                "",
                finding["description"],
                "",
                f"- Module: `{finding['module_id']}`",
                f"- Evidence: `{json.dumps(finding['evidence'], sort_keys=True)}`",
                f"- Recommendation: {finding['recommendation']}",
                "",
            ]
        )
    return "\n".join(lines)


def export_html(payload: dict[str, Any]) -> str:
    findings_html = ""
    if not payload["findings"]:
        findings_html = "<p>No findings were detected by the selected defensive modules.</p>"
    for finding in payload["findings"]:
        evidence = html.escape(json.dumps(finding["evidence"], indent=2, sort_keys=True))
        findings_html += f"""
        <section class="finding severity-{html.escape(finding['severity'])}">
          <h3>{html.escape(finding['title'])}</h3>
          <p><strong>Severity:</strong> {html.escape(finding['severity'])}</p>
          <p>{html.escape(finding['description'])}</p>
          <pre>{evidence}</pre>
          <p><strong>Recommendation:</strong> {html.escape(finding['recommendation'])}</p>
        </section>
        """

    severity_items = "".join(
        f"<li>{html.escape(severity)}: {count}</li>"
        for severity, count in payload["summary"]["by_severity"].items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Exodia Report - {html.escape(payload['target']['name'])}</title>
  <style>
    body {{ background: #0b1120; color: #dbeafe; font-family: Inter, Arial, sans-serif; margin: 40px; }}
    h1, h2, h3 {{ color: #f8fafc; }}
    code, pre {{ background: #111827; color: #bfdbfe; border: 1px solid #243244; border-radius: 6px; padding: 10px; }}
    .finding {{
      border: 1px solid #243244;
      border-left: 5px solid #38bdf8;
      border-radius: 8px;
      padding: 16px;
      margin: 16px 0;
    }}
    .severity-critical {{ border-left-color: #ef4444; }}
    .severity-high {{ border-left-color: #f97316; }}
    .severity-medium {{ border-left-color: #f59e0b; }}
    .severity-low {{ border-left-color: #22c55e; }}
    .severity-info {{ border-left-color: #38bdf8; }}
  </style>
</head>
<body>
  <h1>Exodia Security Report</h1>
  <p><strong>Generated at:</strong> {html.escape(payload['generated_at'])}</p>
  <h2>Authorized Use Disclaimer</h2>
  <p>{html.escape(payload['disclaimer'])}</p>
  <h2>Target</h2>
  <p><strong>Name:</strong> {html.escape(payload['target']['name'])}</p>
  <p><strong>Type:</strong> {html.escape(payload['target']['type'])}</p>
  <p><strong>Value:</strong> {html.escape(payload['target']['value'])}</p>
  <p><strong>Authorized scope:</strong> {html.escape(payload['target']['authorization_scope'])}</p>
  <h2>Executive Summary</h2>
  <p><strong>Status:</strong> {html.escape(payload['scan']['status'])}</p>
  <p><strong>Risk score:</strong> {payload['scan']['risk_score']}</p>
  <p><strong>Total findings:</strong> {payload['summary']['total_findings']}</p>
  <ul>{severity_items}</ul>
  <h2>Findings</h2>
  {findings_html}
</body>
</html>"""
