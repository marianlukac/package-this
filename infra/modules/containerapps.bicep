param prefix string
param location string
param sqlConnectionString string
param serviceBusConnectionString string
param webPubSubConnectionString string
param azureMapsKey string

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${prefix}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource environment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${prefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

resource backend 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${prefix}-backend'
  location: location
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: 'ghcr.io/globalai-community/dm-package-manager/backend:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'DATABASE_URL', value: sqlConnectionString }
            { name: 'EVENT_PUBLISHER', value: 'servicebus' }
            { name: 'AZURE_SERVICE_BUS_CONNECTION_STRING', value: serviceBusConnectionString }
            { name: 'REALTIME_PUBLISHER', value: 'webpubsub' }
            { name: 'AZURE_WEB_PUBSUB_CONNECTION_STRING', value: webPubSubConnectionString }
            { name: 'AZURE_MAPS_KEY', value: azureMapsKey }
            { name: 'APP_ENV', value: 'azure' }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

resource frontend 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${prefix}-frontend'
  location: location
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 4200
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: 'ghcr.io/globalai-community/dm-package-manager/frontend:latest'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 2
      }
    }
  }
}

output backendUrl string = 'https://${backend.properties.configuration.ingress!.fqdn}'
output frontendUrl string = 'https://${frontend.properties.configuration.ingress!.fqdn}'
