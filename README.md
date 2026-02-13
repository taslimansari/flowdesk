# FlowDesk MVP (CareOps Hackathon)

A unified operations platform prototype for service businesses. This MVP includes:

- Business onboarding APIs (workspace, channels, booking setup, activation)
- Contact intake flow creating contacts + conversations + automated welcome
- Booking flow with automated confirmation
- Unified inbox data model with automation pause on staff reply
- Inventory management with low-stock alerts
- Owner dashboard for real-time KPIs + alert links

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

Open http://localhost:8000

## Key Endpoints

- `POST /onboarding/workspace`
- `POST /onboarding/channels/{workspace_id}`
- `POST /contact-form/submit`
- `POST /booking-types`
- `POST /bookings`
- `POST /inventory`
- `POST /inbox/{conversation_id}/reply`
- `POST /onboarding/activate/{workspace_id}`
- `GET /` dashboard

## Notes

- Uses SQLAlchemy with a configurable `DATABASE_URL` (defaults to SQLite).
- Designed so integrations (email/SMS) can be swapped for real providers.
