from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_modules_endpoint(client: TestClient) -> None:
    response = client.get("/modules")

    assert response.status_code == 200
    assert any(module["id"] == "web_headers" for module in response.json())


def test_create_target_and_reject_scan_without_authorization(client: TestClient) -> None:
    target_response = client.post(
        "/targets",
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
        json={
            "target_id": target_response.json()["id"],
            "modules": ["web_headers"],
            "authorization_confirmed": False,
        },
    )

    assert scan_response.status_code == 400


def test_sre_check_rejects_missing_authorization(client: TestClient) -> None:
    response = client.post(
        "/sre/check",
        json={
            "url": "https://example.test",
            "authorization_confirmed": False,
        },
    )

    assert response.status_code == 422
