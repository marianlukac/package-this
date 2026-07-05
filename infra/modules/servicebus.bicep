param prefix string
param location string

var topics = [
  'packages'
  'package-status'
  'package-location'
  'truck-location'
  'truck-reroute'
  'manager-actions'
  'complaints'
  'audit-log'
]

resource namespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${prefix}-sb'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
}

resource sbTopics 'Microsoft.ServiceBus/namespaces/topics@2022-10-01-preview' = [for topic in topics: {
  parent: namespace
  name: topic
  properties: {
    defaultMessageTimeToLive: 'P14D'
  }
}]

resource authRule 'Microsoft.ServiceBus/namespaces/authorizationRules@2022-10-01-preview' = {
  parent: namespace
  name: 'dm-packages-app'
  properties: {
    rights: ['Send', 'Listen', 'Manage']
  }
}

output connectionString string = authRule.listKeys().primaryConnectionString
