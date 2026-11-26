from fastapi import APIRouter, HTTPException, status

from app.models import DeviceCreate, DeviceResponse, StatusUpdate
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    device_service,
)

router = APIRouter()


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_device(device: DeviceCreate) -> DeviceResponse:
    try:
        return device_service.register(device)
    except DeviceAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error


@router.get("", response_model=list[DeviceResponse])
def get_devices() -> list[DeviceResponse]:
    return device_service.list()


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device_by_id(device_id: int) -> DeviceResponse:
    try:
        return device_service.get(device_id)
    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error


@router.patch("/{device_id}/status", response_model=DeviceResponse)
def change_device_status(
    device_id: int, update: StatusUpdate
) -> DeviceResponse:
    try:
        return device_service.update_status(device_id, update.status)
    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
