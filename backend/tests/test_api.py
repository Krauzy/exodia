from fastapi.testclient import TestClient


def auth_headers(client: TestClient, username: str = "analyst") -> dict[str, str]:
    response = client.post("/auth/register", json={"username": username, "password": "strong-password"})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_prefixed_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_modules_endpoint(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.get("/modules", headers=headers)

    assert response.status_code == 200
    assert any(module["id"] == "web_headers" for module in response.json())
    assert any("PENTEST" in module["tags"] for module in response.json())
    assert any("SRE" in module["tags"] for module in response.json())


def test_create_custom_module(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/modules",
        headers=headers,
        json={
            "name": "status-check",
            "title": "Status Check",
            "description": "Checks intercepted HTTP status codes.",
            "severity": "low",
            "tags": ["api"],
            "code": (
                "def analyze(request, response):\n"
                "    if response.status_code >= 400:\n"
                "        return {\"title\": \"HTTP error\", \"description\": \"Error status\", "
                "\"severity\": \"low\", \"recommendation\": \"Review endpoint\", "
                "\"evidence\": {\"status\": response.status_code}}\n"
                "    return []\n"
            ),
        },
    )

    assert response.status_code == 201
    assert response.json()["module_id"].startswith("custom:")

    modules = client.get("/modules", headers=headers)
    assert any(module["id"] == response.json()["module_id"] for module in modules.json())


def test_custom_module_rejects_imports(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/modules",
        headers=headers,
        json={
            "name": "bad-module",
            "title": "Bad Module",
            "description": "Attempts to import an unsafe module.",
            "severity": "low",
            "tags": ["bad"],
            "code": "import os\ndef analyze(request, response):\n    return []\n",
        },
    )

    assert response.status_code == 400


def test_create_target_and_reject_scan_without_authorization(client: TestClient) -> None:
    headers = auth_headers(client)
    target_response = client.post(
        "/targets",
        headers=headers,
        json={
            "name": "Lab App",
            "target_type": "web",
            "value": "https://lab.example",
            "description": "test",
            "authorization_scope": "owned lab application",
            "tags": ["lab"],
            "active": True,
        },
    )
    assert target_response.status_code == 201

    scan_response = client.post(
        "/scans",
        headers=headers,
        json={
            "target_id": target_response.json()["id"],
            "modules": ["web_headers"],
            "authorization_confirmed": False,
        },
    )

    assert scan_response.status_code == 400


def test_sre_check_rejects_missing_authorization(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/sre/check",
        headers=headers,
        json={
            "url": "https://example.test",
            "authorization_confirmed": False,
        },
    )

    assert response.status_code == 422


def test_pentest_check_rejects_missing_authorization(client: TestClient) -> None:
    headers = auth_headers(client)
    response = client.post(
        "/pentest/check",
        headers=headers,
        json={
            "url": "https://example.test",
            "authorization_confirmed": False,
        },
    )

    assert response.status_code == 422


def test_targets_are_scoped_to_authenticated_user(client: TestClient) -> None:
    first_headers = auth_headers(client, "first")
    second_headers = auth_headers(client, "second")
    response = client.post(
        "/targets",
        headers=first_headers,
        json={
            "name": "Private App",
            "target_type": "web",
            "value": "https://private.example",
            "description": "test",
            "authorization_scope": "owned lab application",
            "tags": ["lab"],
            "active": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["user_id"] is not None

    first_targets = client.get("/targets", headers=first_headers)
    second_targets = client.get("/targets", headers=second_headers)

    assert len(first_targets.json()) == 1
    assert second_targets.json() == []
