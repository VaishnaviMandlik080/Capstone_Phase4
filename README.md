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
