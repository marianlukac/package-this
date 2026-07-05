param prefix string
param location string
param adminLogin string
@secure()
param adminPassword string

resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: '${prefix}-sql'
  location: location
  properties: {
    administratorLogin: adminLogin
    administratorLoginPassword: adminPassword
    minimalTlsVersion: '1.2'
  }
}

resource sqlFirewallAzure 'Microsoft.Sql/servers/firewallRules@2023-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: 'dm-packages'
  location: location
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
}

output connectionString string = 'mssql+pyodbc://${adminLogin}:${adminPassword}@${sqlServer.properties.fullyQualifiedDomainName}/dm-packages?driver=ODBC+Driver+18+for+SQL+Server'
