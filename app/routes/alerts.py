from fastapi import APIRouter

from app.models import AlertResponse
from app.services.device_service import device_service

router = APIRouter()


@router.get("/alerts", response_model=list[AlertResponse])
def get_alerts() -> list[AlertResponse]:
    return device_service.list_alerts()
