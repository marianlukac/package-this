# Local Setup

## Prerequisites

- Docker Desktop (with Docker Compose v2)
- Git

That's it. The devcontainer handles everything else.

## Quickstart (Docker Compose)

```bash
git clone <repo-url>
cd package-this
docker compose up
```

Services:
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- SQL Server: localhost:1433 (sa / DunderMifflin2024!)

## First-time seed

The backend seeds the database automatically on startup via `create_db_and_tables()`. To re-seed:

```bash
curl -X POST http://localhost:8000/demo/reset -H "X-Persona-Id: michael-scott"
# or
./scripts/reset-seed.sh
```

## Local development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # Edit DATABASE_URL for local SQL Server
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start                   # Starts on port 4200 with proxy to :8000
```

## Devcontainer (VS Code / Codespaces)

Open the repo in VS Code and click "Reopen in Container". The devcontainer installs:
- Python 3.12 + pip
- Node 20 + Angular CLI 18
- Azure CLI + Bicep CLI
- ODBC Driver 18 for SQL Server

## Running tests

```bash
cd backend
pytest
```

## Linting

```bash
cd backend
ruff check .
```
