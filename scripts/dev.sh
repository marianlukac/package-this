#!/bin/bash
# Start backend and frontend locally (no Docker required)
# Usage: ./scripts/dev.sh
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Backend: create venv if needed
if [ ! -d "$ROOT/backend/.venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$ROOT/backend/.venv"
fi

# Backend: install dependencies
echo "Installing backend dependencies..."
"$ROOT/backend/.venv/bin/pip" install -r "$ROOT/backend/requirements.txt" --quiet

# Backend: run migrations
echo "Running database migrations..."
(cd "$ROOT/backend" && .venv/bin/alembic upgrade head)

# Frontend: install dependencies if needed
if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (cd "$ROOT/frontend" && npm install)
fi

# Start backend in background
echo "Starting backend..."
(cd "$ROOT/backend" && .venv/bin/uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!

# Start frontend in background
echo "Starting frontend..."
(cd "$ROOT/frontend" && npm start) &
FRONTEND_PID=$!

echo ""
echo "Services running (Ctrl+C to stop both):"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:4200"
echo "  Swagger:  http://localhost:8000/docs"

# Wait and clean up on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
