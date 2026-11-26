import pytest

from app.models import DeviceCreate, DeviceStatus
from app.repositories.device_repository import InMemoryDeviceRepository
from app.services.device_service import DeviceAlreadyExistsError, DeviceNotFoundError, DeviceService


@pytest.fixture
def repository() -> InMemoryDeviceRepository:
    return InMemoryDeviceRepository()


@pytest.fixture
def service(repository: InMemoryDeviceRepository) -> DeviceService:
    return DeviceService(repository)


def create_device(status: DeviceStatus = "online") -> DeviceCreate:
    return DeviceCreate(
        device_id="RTR-101",
        name="Branch Router",
        device_type="router",
        ip_address="192.168.10.1",
        status=status,
    )


def test_register_device(service: DeviceService) -> None:
    device = service.register(create_device())
    assert device.device_id == "RTR-101"
    assert device.name == "Branch Router"
    assert device.status == "online"
    assert service.get("RTR-101") == device


def test_register_duplicate_device_raises_error(service: DeviceService) -> None:
    service.register(create_device())
    with pytest.raises(DeviceAlreadyExistsError, match="RTR-101"):
        service.register(create_device())


def test_get_and_update_missing_device_raise_error(service: DeviceService) -> None:
    with pytest.raises(DeviceNotFoundError, match="MISSING"):
        service.get("MISSING")
    with pytest.raises(DeviceNotFoundError, match="MISSING"):
        service.update_status("MISSING", "offline")


def test_initial_offline_registration_does_not_create_alert(service: DeviceService) -> None:
    device = service.register(create_device(status="offline"))
    assert device.status == "offline"
    assert service.list_alerts() == []


def test_online_to_offline_transition_creates_one_alert(service: DeviceService) -> None:
    service.register(create_device())
    updated = service.update_status("RTR-101", "offline")
    assert updated.status == "offline"
    alerts = service.list_alerts()
    assert len(alerts) == 1
    assert alerts[0].device_id == "RTR-101"
    assert alerts[0].message == "Device RTR-101 changed from online to offline"
    assert alerts[0].timestamp.utcoffset().total_seconds() == 0


def test_repeated_offline_update_does_not_create_another_alert(service: DeviceService) -> None:
    service.register(create_device())
    service.update_status("RTR-101", "offline")
    service.update_status("RTR-101", "offline")
    assert len(service.list_alerts()) == 1
