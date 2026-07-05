#!/bin/bash
# Reset all data tables and re-run seed script
set -e

echo "Resetting Dunder Mifflin Package Manager seed data..."
curl -s -X POST http://localhost:8000/demo/reset \
  -H "X-Persona-Id: michael-scott" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo ""
echo "Seed data reset complete."
