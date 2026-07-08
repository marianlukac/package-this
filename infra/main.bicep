targetScope = 'resourceGroup'

@description('Environment name: dev, staging, prod')
param environmentName string = 'dev'

@description('Azure region')
param location string = resourceGroup().location

@description('SQL admin login')
param sqlAdminLogin string

@secure()
@description('SQL admin password')
param sqlAdminPassword string

@description('Fully-qualified backend container image, e.g. ghcr.io/org/repo/backend:sha')
param backendImage string = 'ghcr.io/globalai-community/dm-package-manager/backend:latest'

@description('Fully-qualified frontend container image, e.g. ghcr.io/org/repo/frontend:sha')
param frontendImage string = 'ghcr.io/globalai-community/dm-package-manager/frontend:latest'

@description('Container registry server (e.g. ghcr.io)')
param registryServer string = 'ghcr.io'

@description('Container registry username (leave empty for anonymous pull of public images)')
param registryUsername string = ''

@secure()
@description('Container registry password / token')
param registryPassword string = ''

var prefix = 'dm-packages-${environmentName}'

// ----- Azure SQL -----
module sql './modules/sql.bicep' = {
  name: 'sql'
  params: {
    prefix: prefix
    location: location
    adminLogin: sqlAdminLogin
    adminPassword: sqlAdminPassword
  }
}

// ----- Service Bus -----
module serviceBus './modules/servicebus.bicep' = {
  name: 'servicebus'
  params: {
    prefix: prefix
    location: location
  }
}

// ----- Web PubSub -----
module webPubSub './modules/webpubsub.bicep' = {
  name: 'webpubsub'
  params: {
    prefix: prefix
    location: location
  }
}

// ----- Azure Maps -----
module maps './modules/maps.bicep' = {
  name: 'maps'
  params: {
    prefix: prefix
    location: location
  }
}

// ----- Container Apps -----
module containerApps './modules/containerapps.bicep' = {
  name: 'containerapps'
  params: {
    prefix: prefix
    location: location
    sqlConnectionString: sql.outputs.connectionString
    serviceBusConnectionString: serviceBus.outputs.connectionString
    webPubSubConnectionString: webPubSub.outputs.connectionString
    azureMapsKey: maps.outputs.primaryKey
    backendImage: backendImage
    frontendImage: frontendImage
    registryServer: registryServer
    registryUsername: registryUsername
    registryPassword: registryPassword
  }
}

output backendUrl string = containerApps.outputs.backendUrl
output frontendUrl string = containerApps.outputs.frontendUrl
