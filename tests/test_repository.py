from app.models import AlertResponse, DeviceResponse
from app.repositories.device_repository import InMemoryDeviceRepository


def device() -> DeviceResponse:
    return DeviceResponse(
        device_id="RTR-101",
        name="Branch Router",
        device_type="router",
        ip_address="192.168.10.1",
    )


def test_repository_returns_device_copies() -> None:
    repository = InMemoryDeviceRepository()
    repository.add_device(device())

    retrieved = repository.get_device("RTR-101")
    assert retrieved is not None
    retrieved.name = "mutated"
    repository.list_devices()[0].name = "also-mutated"

    stored = repository.get_device("RTR-101")
    assert stored is not None
    assert stored.name == "Branch Router"


def test_repository_returns_alert_copies() -> None:
    repository = InMemoryDeviceRepository()
    repository.save_alert(
        AlertResponse(
            device_id="RTR-101",
            message="Device RTR-101 changed from online to offline",
            timestamp="2026-11-26T09:00:00+00:00",
        )
    )

    alerts = repository.list_alerts()
    alerts.clear()

    assert len(repository.list_alerts()) == 1
