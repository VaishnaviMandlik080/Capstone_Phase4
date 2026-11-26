from datetime import datetime

import pytest
from fastapi.testclient import TestClient

import app.routes.alerts as alerts_routes
import app.routes.devices as devices_routes
from app.main import app
from app.repositories.device_repository import InMemoryDeviceRepository
from app.services.device_service import DeviceService


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    service = DeviceService(InMemoryDeviceRepository())
    monkeypatch.setattr(devices_routes, "device_service", service)
    monkeypatch.setattr(alerts_routes, "device_service", service)
    return TestClient(app)


def device_payload(**overrides: object) -> dict[str, object]:
    return {
        "device_id": "RTR-101",
        "name": "Branch Router",
        "device_type": "router",
        "ip_address": "192.168.10.1",
        **overrides,
    }


def test_health_and_all_six_endpoints(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    endpoints = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
    }
    assert {
        ("POST", "/devices"),
        ("GET", "/devices"),
        ("GET", "/devices/{device_id}"),
        ("PATCH", "/devices/{device_id}/status"),
        ("GET", "/alerts"),
        ("GET", "/health"),
    } <= endpoints


def test_openapi_documents_examples_and_error_responses(
    client: TestClient,
) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert paths["/devices"]["post"]["responses"]["201"]
    assert paths["/devices"]["post"]["responses"]["409"]["description"]
    assert paths["/devices/{device_id}"]["get"]["responses"]["404"]["description"]
    assert paths["/devices/{device_id}/status"]["patch"]["responses"]["404"]["description"]
    assert schema["components"]["schemas"]["DeviceCreate"]["examples"][0]["device_id"] == "RTR-101"
    assert schema["components"]["schemas"]["StatusUpdate"]["examples"][0]["status"] == "offline"


def test_register_list_and_get_device(client: TestClient) -> None:
    response = client.post("/devices", json=device_payload())
    assert response.status_code == 201
    assert response.json() == {
        "device_id": "RTR-101",
        "name": "Branch Router",
        "device_type": "router",
        "ip_address": "192.168.10.1",
        "status": "online",
    }
    assert client.get("/devices").json() == [response.json()]
    assert client.get("/devices/RTR-101").json() == response.json()


@pytest.mark.parametrize(
    "payload",
    [
        {"device_type": "firewall"},
        {"status": "unknown"},
        {"ip_address": "not-an-ip"},
        {"ip_address": "2001:db8::1"},
        {"device_id": ""},
    ],
)
def test_invalid_device_data_returns_422(
    client: TestClient, payload: dict[str, object]
) -> None:
    assert client.post("/devices", json=device_payload(**payload)).status_code == 422


def test_duplicate_device_id_returns_409(client: TestClient) -> None:
    assert client.post("/devices", json=device_payload()).status_code == 201
    assert client.post("/devices", json=device_payload(name="duplicate")).status_code == 409


def test_missing_device_returns_404_for_get_and_status_update(client: TestClient) -> None:
    assert client.get("/devices/RTR-404").status_code == 404
    assert client.patch("/devices/RTR-404/status", json={"status": "offline"}).status_code == 404


def test_only_first_online_to_offline_transition_creates_alert(client: TestClient) -> None:
    client.post("/devices", json=device_payload())
    first = client.patch("/devices/RTR-101/status", json={"status": "offline"})
    repeated = client.patch("/devices/RTR-101/status", json={"status": "offline"})
    assert first.status_code == repeated.status_code == 200
    alerts = client.get("/alerts").json()
    assert len(alerts) == 1
    assert alerts[0]["device_id"] == "RTR-101"
    assert alerts[0]["message"] == "Device RTR-101 changed from online to offline"
    assert datetime.fromisoformat(alerts[0]["timestamp"]).utcoffset().total_seconds() == 0


def test_swagger_walkthrough_inputs(client: TestClient) -> None:
    registration = client.post("/devices", json={
        "device_id": "RTR-101", "name": "Branch Router", "device_type": "router",
        "ip_address": "192.168.10.1", "status": "online",
    })
    assert registration.status_code == 201
    first = client.patch("/devices/RTR-101/status", json={"status": "offline"})
    assert first.status_code == 200
    assert first.json()["status"] == "offline"
    assert client.patch("/devices/RTR-101/status", json={"status": "offline"}).status_code == 200
    alerts = client.get("/alerts").json()
    assert len(alerts) == 1 and alerts[0]["device_id"] == "RTR-101"
    duplicate = client.post("/devices", json={
        "device_id": "RTR-101", "name": "Branch Router", "device_type": "router",
        "ip_address": "192.168.10.1", "status": "online",
    })
    assert duplicate.status_code == 409


def test_initial_offline_registration_does_not_create_alert(client: TestClient) -> None:
    assert client.post("/devices", json=device_payload(status="offline")).status_code == 201
    assert client.get("/alerts").json() == []


def test_offline_transition_after_recovery_creates_a_new_alert(client: TestClient) -> None:
    client.post("/devices", json=device_payload())
    client.patch("/devices/RTR-101/status", json={"status": "offline"})
    client.patch("/devices/RTR-101/status", json={"status": "online"})
    client.patch("/devices/RTR-101/status", json={"status": "offline"})
    assert len(client.get("/alerts").json()) == 2
