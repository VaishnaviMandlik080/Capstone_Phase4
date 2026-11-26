from fastapi import APIRouter, HTTPException

from app.models import Device, DeviceCreate, DeviceStatusUpdate
from app.services.device_service import (
    DeviceNotFoundError,
    create_device,
    get_device,
    list_devices,
    update_device_status,
)

router = APIRouter()


@router.post("", response_model=Device, status_code=201)
def register_device(device: DeviceCreate) -> Device:
    return create_device(device)


@router.get("", response_model=list[Device])
def get_devices() -> list[Device]:
    return list_devices()


@router.get("/{device_id}", response_model=Device)
def get_device_by_id(device_id: int) -> Device:
    try:
        return get_device(device_id)
    except DeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/{device_id}/status", response_model=Device)
def change_device_status(
    device_id: int, update: DeviceStatusUpdate
) -> Device:
    try:
        return update_device_status(device_id, update.status)
    except DeviceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
