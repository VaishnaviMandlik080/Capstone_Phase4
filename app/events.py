from app.models import Alert


alerts: list[Alert] = []


def record_offline_alert(device_id: int) -> Alert:
    alert = Alert(
        device_id=device_id,
        message=f"Device {device_id} changed from online to offline",
    )
    alerts.append(alert)
    return alert
