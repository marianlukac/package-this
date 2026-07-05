# OpenAPI Usage

## Interactive docs

With the backend running, browse to:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Raw JSON: http://localhost:8000/openapi.json

## Exporting a stable file

```bash
./scripts/export-openapi.sh docs/openapi.yaml
```

This calls `GET /openapi.json` and writes it to `docs/openapi.yaml` (requires `yq` for YAML conversion).

## MCP server usage

The API is designed for MCP consumption. Key agent-friendly endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /operational-summary` | Current state snapshot |
| `GET /packages?status=in_transit` | Filter packages by lifecycle status |
| `GET /packages/at-risk` | Packages needing attention |
| `GET /packages/delayed` | All delayed packages |
| `GET /packages/{id}/history` | Full audit trail for a package |
| `GET /trucks/{id}/current-location` | Real-time truck position |
| `GET /trucks/{id}/current-route` | Active stops and route |
| `GET /deliveries/active` | All in-flight deliveries |
| `GET /customers/{id}/complaints` | Complaints per customer |
| `POST /manager-actions` | Execute manager decisions |
| `POST /demo/reset` | Restore seed state |
| `POST /demo/scenarios/{name}` | Run a scripted scenario |

## Authentication

All endpoints require `X-Persona-Id: <employee-id>`. For MCP tools, pass this as a configured header using the employee ID appropriate for the tool's role.
