import httpx
import pytest

from app.modules.web_headers.module import WebSecurityHeadersAnalyzer


@pytest.mark.asyncio
async def test_web_headers_module_reports_missing_headers() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"server": "test"}, text="ok")

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, base_url="https://example.test")
    module = WebSecurityHeadersAnalyzer(client_factory=lambda: client)

    result = await module.run("https://example.test", {})
    await client.aclose()

    assert result.module_id == "web_headers"
    assert any(finding.title == "Missing Content-Security-Policy" for finding in result.findings)

