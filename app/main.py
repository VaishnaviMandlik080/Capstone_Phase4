from fastapi import FastAPI

from app.routes.devices import router as devices_router

app = FastAPI(title="NetPulse")
app.include_router(devices_router, prefix="/devices", tags=["devices"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
