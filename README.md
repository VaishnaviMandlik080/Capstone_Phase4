# NetPulse

A small, in-memory FastAPI device-monitoring API. It validates IPv4 addresses,
tracks routers, switches, and servers, and records an alert when a device
changes from online to offline.

## Run

From the project root, create and activate a virtual environment, then install
the requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `/docs` for the interactive API documentation. The API exposes:

- `POST /devices`
- `GET /devices`
- `GET /devices/{device_id}`
- `PATCH /devices/{device_id}/status`
- `GET /alerts`
- `GET /health`

Device registration requires `device_id`, `name`, `device_type` (`router`,
`switch`, or `server`), and a valid IPv4 `ip_address`. Status defaults to
`online`.

Run the automated tests with:

```bash
pytest
```

## Verify the offline alert in Swagger

Open `/docs` and run these requests in order:

1. Register an online device with `POST /devices`:

   ```json
   {
     "device_id": 1,
     "name": "edge-router",
     "device_type": "router",
     "ip_address": "192.168.1.1"
   }
   ```

2. Run `PATCH /devices/1/status` twice with this body:

   ```json
   {
     "status": "offline"
   }
   ```

3. Run `GET /alerts`. It should return one alert for device 1. Repeating the
   offline update does not create another alert.
