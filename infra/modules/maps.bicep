param prefix string
param location string

resource mapsAccount 'Microsoft.Maps/accounts@2023-06-01' = {
  name: '${prefix}-maps'
  location: location
  sku: {
    name: 'G2'
  }
  kind: 'Gen2'
  properties: {
    disableLocalAuth: false
  }
}

output primaryKey string = mapsAccount.listKeys().primaryKey
