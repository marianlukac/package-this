using '../main.bicep'

param environmentName = 'trainer'
param location = 'eastus'

// SQL Admin credentials — values supplied via az deployment command or CI secret
param sqlAdminLogin = 'dmadmin'
@secure()
param sqlAdminPassword = ''  // Provided at deploy time: --parameters sqlAdminPassword=$SQL_ADMIN_PASSWORD
