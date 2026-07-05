# Dunder Mifflin Package Manager

The official trainer baseline for the **Agentic AI Workshop** — a full-stack business application for managing paper-product and office-supply packages from sale creation through delivery.

Workshop attendees build agents, MCP servers, memory systems, and agent-to-agent scenarios on top of this application.

---

## Quick Start

```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start everything (SQL Server + Backend + Frontend)
docker compose up
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:4200 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| OpenAPI JSON | http://localhost:8000/openapi.json |

The backend automatically runs migrations and seeds the database on first startup.

---

## Personas

Use the persona switcher in the top-right corner of the UI, or pass the `X-Persona-Id` header directly:

```bash
curl -H "X-Persona-Id: jim-halpert" http://localhost:8000/packages
```

| Name | Slug | Persona |
|------|------|---------|
| Michael Scott | michael-scott | manager |
| Dwight Schrute | dwight-schrute | sales |
| Jim Halpert | jim-halpert | sales |
| Pam Beesly | pam-beesly | accounting |
| Darryl Philbin | darryl-philbin | warehouse |
| Roy Anderson | roy-anderson | warehouse |

See [docs/persona-guide.md](docs/persona-guide.md) for the full list.

---

## Resetting Data

```bash
# Via API (requires manager persona)
curl -X POST http://localhost:8000/demo/reset -H "X-Persona-Id: michael-scott"

# Via script
./scripts/reset-seed.sh      # Linux/Mac
.\scripts\reset-seed.ps1    # Windows
```

---

## Demo Scenarios

```bash
curl -X POST http://localhost:8000/demo/scenarios/delayed-delivery \
  -H "X-Persona-Id: michael-scott"
```

Available: `delayed-delivery`, `damaged-in-transit`, `happy-customer`, `manager-reroute`, `complaint-and-return`

---

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/architecture.md](docs/architecture.md) | System overview and data flow |
| [docs/local-setup.md](docs/local-setup.md) | Full local development guide |
| [docs/azure-setup.md](docs/azure-setup.md) | Azure provisioning and deployment |
| [docs/persona-guide.md](docs/persona-guide.md) | All personas and permissions |
| [docs/seed-data.md](docs/seed-data.md) | What's seeded on startup |
| [docs/demo-scenarios.md](docs/demo-scenarios.md) | Trainer scripts for each scenario |
| [docs/event-topics.md](docs/event-topics.md) | Service Bus topics and event shapes |
| [docs/mcp-integration.md](docs/mcp-integration.md) | How to build MCP servers on this API |

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLModel, Alembic |
| Frontend | Angular 18, Tailwind CSS |
| Database | Azure SQL (prod) / SQL Server 2022 in Docker (local) |
| Messaging | Azure Service Bus (8 topics) |
| Real-time | Azure Web PubSub / WebSocket fallback |
| Maps | Azure Maps |
| Infrastructure | Azure Bicep, Azure Container Apps |
