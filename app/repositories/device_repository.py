from app.models import Device, DeviceCreate


class InMemoryDeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[int, Device] = {}
        self._next_id = 1

    def create(self, device_data: DeviceCreate) -> Device:
        device = Device(
            id=self._next_id,
            name=device_data.name,
            device_type=device_data.device_type,
        )
        self._devices[device.id] = device
        self._next_id += 1
        return device

    def list_all(self) -> list[Device]:
        return list(self._devices.values())

    def get(self, device_id: int) -> Device | None:
        return self._devices.get(device_id)

    def save(self, device: Device) -> None:
        self._devices[device.id] = device


device_repository = InMemoryDeviceRepository()
