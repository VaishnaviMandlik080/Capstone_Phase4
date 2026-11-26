from typing import Literal

from pydantic import BaseModel, Field


DeviceType = Literal["router", "switch", "server"]
DeviceStatus = Literal["online", "offline"]


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1)
    device_type: DeviceType


class DeviceStatusUpdate(BaseModel):
    status: DeviceStatus


class Device(BaseModel):
    id: int
    name: str
    device_type: DeviceType
    status: DeviceStatus = "online"


class Alert(BaseModel):
    device_id: int
    message: str
    event_type: Literal["device_offline"] = "device_offline"
