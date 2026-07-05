# Azure Setup (Trainer Baseline)

## Prerequisites

- Azure CLI authenticated (`az login`)
- Bicep CLI (`az bicep install`)
- An Azure subscription with sufficient quota

## Deploy infrastructure

```bash
cd infra

# Create a resource group
az group create --name rg-dm-packages-dev --location eastus

# Deploy all resources
az deployment group create \
  --resource-group rg-dm-packages-dev \
  --template-file main.bicep \
  --parameters environmentName=dev \
               sqlAdminLogin=dmadmin \
               sqlAdminPassword='<strong-password>'
```

The deployment outputs `backendUrl` and `frontendUrl`.

## Configure backend environment

After deployment, update the backend container app's environment:

| Variable | Value source |
|---|---|
| `DATABASE_URL` | Azure SQL connection string from Bicep output |
| `EVENT_PUBLISHER` | `servicebus` |
| `AZURE_SERVICE_BUS_CONNECTION_STRING` | From Bicep output |
| `REALTIME_PUBLISHER` | `webpubsub` |
| `AZURE_WEB_PUBSUB_CONNECTION_STRING` | From Bicep output |
| `AZURE_MAPS_KEY` | From Bicep output |

## Run database migrations

After deploying the backend container:

```bash
# Exec into the container
az containerapp exec \
  --name dm-packages-dev-backend \
  --resource-group rg-dm-packages-dev \
  --command "alembic upgrade head"
```

## Seed data

```bash
curl -X POST https://<backend-url>/demo/reset \
  -H "X-Persona-Id: michael-scott"
```

## Shared trainer resources

For workshop sessions, one trainer deploys the infrastructure and shares:
1. The backend URL with attendees
2. The Azure Maps subscription key
3. Instructions to use `X-Persona-Id` headers

Attendees can use the shared backend or run locally against the shared Azure SQL.
