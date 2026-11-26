from app.events import record_offline_alert
from app.models import Device, DeviceCreate, DeviceStatus
from app.repositories.device_repository import device_repository


class DeviceNotFoundError(Exception):
    pass


def create_device(device_data: DeviceCreate) -> Device:
    return device_repository.create(device_data)


def list_devices() -> list[Device]:
    return device_repository.list_all()


def get_device(device_id: int) -> Device:
    device = device_repository.get(device_id)
    if device is None:
        raise DeviceNotFoundError(f"Device {device_id} not found")
    return device


def update_device_status(device_id: int, status: DeviceStatus) -> Device:
    device = get_device(device_id)
    if device.status == "online" and status == "offline":
        record_offline_alert(device_id)
    updated_device = device.model_copy(update={"status": status})
    device_repository.save(updated_device)
    return updated_device
