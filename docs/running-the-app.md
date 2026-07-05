# Running the App

There are two ways to run the Dunder Mifflin Package Manager: with Docker (recommended, fewest prerequisites) or directly on your machine using the dev scripts (no Docker required).

---

## Option 1: Docker

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Compose v2
- Git

### Steps

::: code-group

```bash [Mac / Linux]
git clone <repo-url>
cd package-this
./scripts/dev.sh
```

```powershell [Windows]
git clone <repo-url>
cd package-this
docker compose up
```

:::

That's it. Docker pulls the SQL Server image, builds the backend and frontend, runs migrations, and seeds the database on first start.

---

## Option 2: Dev Script (no Docker)

The dev scripts handle virtual environment creation, dependency installation, database migrations, and starting both services. The database defaults to SQLite so no database server is needed.

### Prerequisites

- Python 3.12 ([python.org](https://www.python.org/downloads/))
- Node.js 20+ ([nodejs.org](https://nodejs.org/))
- Git

### First run

::: code-group

```bash [Mac / Linux]
git clone <repo-url>
cd package-this
chmod +x scripts/dev.sh
./scripts/dev.sh
```

```powershell [Windows]
git clone <repo-url>
cd package-this
.\scripts\dev.ps1
```

:::

On first run the script will:

1. Create a Python 3.12 virtual environment in `backend/.venv`
2. Install Python dependencies from `backend/requirements.txt`
3. Run database migrations (creates a local `backend/dm_packages_dev.db` SQLite file)
4. Install Node dependencies in `frontend/node_modules`
5. Start the backend and frontend

On subsequent runs it skips steps 1, 2, and 4 if those outputs already exist.

### Stopping the services

::: code-group

```bash [Mac / Linux]
# Press Ctrl+C in the terminal where dev.sh is running.
# Both backend and frontend are stopped automatically.
```

```powershell [Windows]
# Close the two terminal windows that were opened by dev.ps1,
# or press Ctrl+C in each one.
```

:::

---

## Service URLs

Once running, all services are available on localhost:

| Service | URL |
|---------|-----|
| Frontend | <http://localhost:4200> |
| Backend API | <http://localhost:8000> |
| Swagger UI | <http://localhost:8000/docs> |
| OpenAPI JSON | <http://localhost:8000/openapi.json> |

---

## Verify it's working

::: code-group

```bash [Mac / Linux]
curl http://localhost:8000/packages -H "X-Persona-Id: jim-halpert"
```

```powershell [Windows]
Invoke-RestMethod http://localhost:8000/packages `
  -Headers @{ "X-Persona-Id" = "jim-halpert" }
```

:::

You should get a JSON list of packages. If the response is empty, the seed data may not have run yet; see [Resetting Data](#resetting-data) below.

---

## Resetting Data

To wipe all records and re-seed the database to the workshop starting state:

::: code-group

```bash [Mac / Linux]
curl -X POST http://localhost:8000/demo/reset \
  -H "X-Persona-Id: michael-scott"
```

```powershell [Windows]
.\scripts\reset-seed.ps1
```

:::

---

## Troubleshooting

### `ImportError: cannot import name 'StrEnum'`

The virtual environment was created with Python 3.10 or earlier. Delete it and let the script recreate it:

::: code-group

```bash [Mac / Linux]
rm -rf backend/.venv
./scripts/dev.sh
```

```powershell [Windows]
Remove-Item -Recurse -Force backend\.venv
.\scripts\dev.ps1
```

:::

### Alembic error: `table X already exists`

A partial database file exists from a previous failed run. Delete it and re-run migrations:

::: code-group

```bash [Mac / Linux]
rm -f backend/dm_packages_dev.db
./scripts/dev.sh
```

```powershell [Windows]
Remove-Item -Force backend\dm_packages_dev.db
.\scripts\dev.ps1
```

:::
