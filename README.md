# FlowDesk MVP (CareOps Hackathon)

A unified operations platform prototype for service businesses.

## What this MVP includes

- Business onboarding APIs (workspace, channels, booking setup, activation)
- Contact intake flow creating contacts + conversations + automated welcome
- Booking flow with automated confirmation
- Unified inbox data model with automation pause on staff reply
- Inventory management with low-stock alerts
- Owner dashboard for real-time KPIs + alert links

---

## Run locally

### 1) Prerequisites

- Python **3.11+**
- pip
- (Optional) PostgreSQL if you do not want SQLite

Check Python version:

```bash
python --version
```

### 2) Clone and enter the project

```bash
git clone <your-repo-url>
cd flowdesk
```

### 3) Create a virtual environment

#### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4) Install dependencies

```bash
pip install --upgrade pip
pip install -e .
```

### 5) Run the server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Now open:

- Dashboard: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

---

## Database configuration

By default, the app uses SQLite:

- `sqlite:///./flowdesk.db`

To use PostgreSQL, set `DATABASE_URL` before starting the server.

### macOS / Linux

```bash
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@localhost:5432/flowdesk"
```

### Windows (PowerShell)

```powershell
$env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@localhost:5432/flowdesk"
```

If you use PostgreSQL, install a driver too:

```bash
pip install psycopg[binary]
```

---

## Quick smoke test (API)

Create a workspace:

```bash
curl -X POST http://localhost:8000/onboarding/workspace \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Care",
    "address": "123 Main St",
    "timezone": "UTC",
    "contact_email": "owner@acme.test"
  }'
```

Connect at least one channel (required before activation):

```bash
curl -X POST http://localhost:8000/onboarding/channels/1 \
  -H "Content-Type: application/json" \
  -d '{"email_connected": true, "sms_connected": false}'
```

---

## Key endpoints

- `POST /onboarding/workspace`
- `POST /onboarding/channels/{workspace_id}`
- `POST /contact-form/submit`
- `POST /booking-types`
- `POST /bookings`
- `POST /inventory`
- `POST /inbox/{conversation_id}/reply`
- `POST /onboarding/activate/{workspace_id}`
- `GET /` dashboard

## Troubleshooting

- **`No module named uvicorn`**: run `pip install -e .` inside the activated virtual environment.
- **Port 8000 already in use**: run with a different port, e.g. `--port 8001`.
- **Install failed behind company proxy**: set your pip proxy/index settings or use your standard internal Python package mirror.
