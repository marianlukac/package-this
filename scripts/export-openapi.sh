#!/usr/bin/env bash
# Export the OpenAPI spec from the running backend to a file.
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
OUTPUT="${1:-docs/openapi.yaml}"

echo "Exporting OpenAPI spec from $BACKEND_URL..."

# Try JSON first, convert to YAML if yq is available
if command -v yq &>/dev/null; then
  curl -sf "$BACKEND_URL/openapi.json" | yq -P > "$OUTPUT"
  echo "Written to $OUTPUT (YAML)"
else
  OUTPUT="${OUTPUT%.yaml}.json"
  curl -sf "$BACKEND_URL/openapi.json" > "$OUTPUT"
  echo "Written to $OUTPUT (JSON — install yq for YAML output)"
fi
