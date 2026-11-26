import ipaddress
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


DeviceType = Literal["router", "switch", "server"]
DeviceStatus = Literal["online", "offline"]


class DeviceFields(BaseModel):
    device_id: int = Field(gt=0)
    name: str = Field(min_length=1)
    device_type: DeviceType
    ip_address: str
    status: DeviceStatus = "online"

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, value: str) -> str:
        try:
            address = ipaddress.ip_address(value)
        except ValueError as error:
            raise ValueError("ip_address must be a valid IPv4 address") from error
        if not isinstance(address, ipaddress.IPv4Address):
            raise ValueError("ip_address must be a valid IPv4 address")
        return str(address)


class DeviceCreate(DeviceFields):
    pass


class DeviceResponse(DeviceFields):
    pass


class StatusUpdate(BaseModel):
    status: DeviceStatus


class AlertResponse(BaseModel):
    device_id: int
    message: str
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def require_utc_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value.astimezone(timezone.utc)
