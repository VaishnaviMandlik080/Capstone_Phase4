# NetPulse

A small, in-memory FastAPI device-monitoring API. It validates IPv4 addresses,
tracks routers, switches, and servers, and records an alert when a device
changes from online to offline.

## Run

From the project root, create and activate a virtual environment, then install
the requirements:

`@bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
`@

Open `/docs` for the interactive API documentation. The API exposes:

- `POST /devices`
- `GET /devices`
- `GET /devices/{device_id}`
- `PATCH /devices/{device_id}/status`
- `GET /alerts`
- `GET /health`

Device registration requires a string `device_id`, `name`, `device_type`
(`router`, `switch`, or `server`), and a valid IPv4 `ip_address`. Status
defaults to `online`.

Run the automated tests with:

`@bash
python -m pytest -q
`@

## Verify the offline alert in Swagger

Device and alert data are held in memory and reset when the application process
restarts. Restart the server for a clean walkthrough, then open `/docs` and run
these requests in order:

1. In `POST /devices`, select **Try it out**, paste the JSON below, and select
   **Execute**. Expect HTTP 201.

   `@json
   {
     "device_id": "RTR-101",
     "name": "Branch Router",
     "device_type": "router",
     "ip_address": "192.168.10.1",
     "status": "online"
   }
   `@

2. In `PATCH /devices/{device_id}/status`, enter `RTR-101` as the device ID.
   Paste the body below and select **Execute**. Expect HTTP 200 and `offline`
   in the response.

   `@json
   {
     "status": "offline"
   }
   `@

3. Run `GET /alerts`. It should contain exactly one alert for `RTR-101`.
   Repeat the same PATCH, then run `GET /alerts` again; there is still only one
   alert. Registering `RTR-101` again returns HTTP 409. If it already exists,
   restart the server or use a new ID such as `RTR-102`.

## Architecture

- **Routes** define the REST endpoints and translate service errors into HTTP
  responses.
- **Service** enforces the device rules and detects online-to-offline
  transitions without depending on HTTP.
- **Repository** owns the in-memory device dictionary and alert list, returning
  copies to callers.
- **Events** creates a timestamped offline alert and asks the repository to
  save it.

The route, service, repository, and event modules form one deployable modular
monolith. A future database-backed repository can implement the `DeviceRepository`
protocol and be injected into `DeviceService`; the service's business rules and
route contracts can stay unchanged.

FastAPI generates `/openapi.json` from route declarations and Pydantic request
and response models. Swagger UI at `/docs` renders that schema, including the
model examples and documented HTTP responses.
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
