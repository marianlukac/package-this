# Quickstart: Local Development

**Date**: 2026-06-19

This guide gets the Dunder Mifflin Package Manager running locally in under 10 minutes.

---

## Prerequisites

- Docker Desktop (running)
- Git

That's it for Docker Compose startup. For development (editing code with live reload),
you also need Python 3.12 and Node 20 installed locally, or use the devcontainer.

---

## Start the Full Stack

```bash
git clone <repo-url>
cd package-this

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start everything
docker compose up
```

Services started:
- SQL Server 2022 on port 1433
- FastAPI backend on port 8000 (`http://localhost:8000`)
- Angular frontend on port 4200 (`http://localhost:4200`)
- API docs at `http://localhost:8000/docs`

The backend automatically runs migrations and seeds the database on first startup.

---

## Switching Personas

Open the application at `http://localhost:4200`. Use the persona switcher in the top-right
corner to switch between any of the 12 predefined employees.

To switch personas via API directly (for agent testing):

```bash
# As Darryl (warehouse)
curl -H "X-Persona-Id: darryl-philbin" http://localhost:8000/packages

# As Michael (manager)
curl -X POST http://localhost:8000/manager-actions \
  -H "X-Persona-Id: michael-scott" \
  -H "Content-Type: application/json" \
  -d '{"action": "override_priority", "entity_type": "package", "entity_id": "PKG-2024-001", "payload": {"priority": "urgent"}, "reason": "Demo", "source": "api"}'
```

---

## Resetting Seed Data

```bash
# Via script (recommended)
./scripts/reset-seed.sh          # Linux/Mac
.\scripts\reset-seed.ps1         # Windows PowerShell

# Via API (Michael persona required)
curl -X POST http://localhost:8000/demo/reset \
  -H "X-Persona-Id: michael-scott"
```

Both methods truncate all data tables and re-run the seed script, restoring the 12 employees,
10 customers, 3 trucks, and 13 seed packages.

---

## Running a Demo Scenario

```bash
curl -X POST http://localhost:8000/demo/scenarios/delayed-delivery \
  -H "X-Persona-Id: michael-scott"
```

Available scenarios: `delayed-delivery`, `damaged-in-transit`, `happy-customer`,
`manager-reroute`, `complaint-and-return`

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

Tests use an in-memory SQLite database (tests only — not the application baseline).
All lifecycle, permission, and event tests run without a running server.

---

## Local Event Stream (without Azure Service Bus)

By default locally, the `InMemoryEventPublisher` logs events to the backend console.
You will see JSON event envelopes printed to stdout as you interact with the application.

To enable the Azure Service Bus emulator or connect to a shared trainer Service Bus,
update `backend/.env`:

```env
EVENT_PUBLISHER=service_bus
AZURE_SERVICE_BUS_CONNECTION_STRING=<your-connection-string>
```

---

## Devcontainer (GitHub Codespaces or VS Code)

Open the repository in VS Code and select "Reopen in Container" when prompted, or open
a GitHub Codespace directly from the repository.

The devcontainer includes:
- Python 3.12 with pip
- Node 20 with npm and Angular CLI
- Azure CLI
- Bicep CLI
- Azure SQL ODBC driver (for local connection testing)
- Docker-in-Docker

---

## Environment Variables Reference

### backend/.env.example

```env
# Database
DATABASE_URL=mssql+pyodbc://sa:YourPassword@sqlserver:1433/dm_packages?driver=ODBC+Driver+18+for+SQL+Server

# Event publisher: "inmemory" (default) or "service_bus"
EVENT_PUBLISHER=inmemory
AZURE_SERVICE_BUS_CONNECTION_STRING=

# Real-time updates: "websocket" (default) or "web_pubsub"
REALTIME_PUBLISHER=websocket
AZURE_WEB_PUBSUB_CONNECTION_STRING=

# Azure Maps
AZURE_MAPS_KEY=

# Simulation
SIMULATION_TICK_INTERVAL_SECONDS=5
SIMULATION_LOCATION_EVENT_EVERY_N_TICKS=3

# App
APP_ENV=local
APP_PORT=8000
```

### frontend/.env.example

```env
API_BASE_URL=http://localhost:8000
WS_URL=ws://localhost:8000/ws
AZURE_MAPS_CLIENT_ID=
```

---

## Connecting to Shared Trainer Azure Resources

See `docs/azure-setup.md` for:
- How to provision the shared Azure resources with Bicep
- How to configure the backend to use Azure SQL, Service Bus, and Web PubSub
- How to deploy using Azure Container Apps
