from datetime import UTC, datetime
from types import SimpleNamespace

from app.reports.generator import generate_report
from app.schemas.common import risk_score_for_severities


def test_risk_score_mapping() -> None:
    assert risk_score_for_severities(["info", "low", "medium", "high", "critical"]) == 20


def test_markdown_report_contains_disclaimer() -> None:
    target = SimpleNamespace(
        id="target-1",
        name="Lab",
        target_type="web",
        value="https://lab.example",
        authorization_scope="owned lab scope",
        tags=["lab"],
    )
    finding = SimpleNamespace(
        title="Missing header",
        description="A defensive header is missing.",
        severity="low",
        module_id="web_headers",
        evidence={"header": "x-content-type-options"},
        recommendation="Set the header.",
        created_at=datetime.now(UTC),
    )
    scan = SimpleNamespace(
        id="scan-1",
        status="completed",
        modules=["web_headers"],
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        risk_score=1,
        target=target,
        findings=[finding],
    )

    report = generate_report(scan, "markdown")

    assert "Authorized Use Disclaimer" in report
    assert "Missing header" in report

