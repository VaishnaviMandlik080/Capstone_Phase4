import ipaddress
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


DeviceType = Literal["router", "switch", "server"]
DeviceStatus = Literal["online", "offline"]


class DeviceFields(BaseModel):
    device_id: str = Field(
        min_length=1,
        examples=["RTR-101"],
        description="Unique device identifier, for example RTR-101.",
    )
    name: str = Field(min_length=1, examples=["Branch Router"])
    device_type: DeviceType = Field(examples=["router"])
    ip_address: str = Field(examples=["192.168.10.1"])
    status: DeviceStatus = Field(default="online", examples=["online"])

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
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "device_id": "RTR-101",
                    "name": "Branch Router",
                    "device_type": "router",
                    "ip_address": "192.168.10.1",
                    "status": "online",
                }
            ]
        }
    )


class DeviceResponse(DeviceFields):
    pass


class StatusUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "offline"}]}
    )

    status: DeviceStatus = Field(examples=["offline"])


class AlertResponse(BaseModel):
    device_id: str
    message: str
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def require_utc_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value.astimezone(timezone.utc)
