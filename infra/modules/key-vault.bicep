@description('The name of the Key Vault')
param keyVaultName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('The object ID of the managed identity that needs access')
param managedIdentityObjectId string

@description('SQL connection string to store as a secret')
@secure()
param sqlConnectionString string

@description('Service Bus connection string to store as a secret')
@secure()
param serviceBusConnectionString string

@description('Web PubSub connection string to store as a secret')
@secure()
param webPubSubConnectionString string

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

// Managed identity gets Key Vault Secrets User role
resource secretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, managedIdentityObjectId, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '4633458b-17de-408a-b874-0445c86b69e6' // Key Vault Secrets User
    )
    principalId: managedIdentityObjectId
    principalType: 'ServicePrincipal'
  }
}

resource sqlSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'database-url'
  properties: {
    value: sqlConnectionString
  }
}

resource serviceBusSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'service-bus-connection-string'
  properties: {
    value: serviceBusConnectionString
  }
}

resource webPubSubSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'web-pubsub-connection-string'
  properties: {
    value: webPubSubConnectionString
  }
}

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output sqlSecretUri string = sqlSecret.properties.secretUri
output serviceBusSecretUri string = serviceBusSecret.properties.secretUri
output webPubSubSecretUri string = webPubSubSecret.properties.secretUri
