# Start backend and frontend locally (no Docker required)
# Usage: .\scripts\dev.ps1

$root = Split-Path $PSScriptRoot -Parent

# Backend: create venv if needed
if (-not (Test-Path "$root\backend\.venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv "$root\backend\.venv"
}

# Backend: install dependencies
Write-Host "Installing backend dependencies..."
& "$root\backend\.venv\Scripts\pip" install -r "$root\backend\requirements.txt" --quiet

# Backend: run migrations
Write-Host "Running database migrations..."
Push-Location "$root\backend"
& ".venv\Scripts\alembic" upgrade head
Pop-Location

# Frontend: install dependencies if needed
if (-not (Test-Path "$root\frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..."
    Push-Location "$root\frontend"
    npm install
    Pop-Location
}

# Start backend in a new terminal window
Write-Host "Starting backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; .venv\Scripts\uvicorn app.main:app --reload --port 8000"

# Start frontend in a new terminal window
Write-Host "Starting frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; npm start"

Write-Host ""
Write-Host "Services starting in separate windows:"
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  Frontend: http://localhost:4200"
Write-Host "  Swagger:  http://localhost:8000/docs"
