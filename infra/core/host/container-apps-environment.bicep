metadata description = 'Creates an Azure Container Apps environment.'
param name string
param location string = resourceGroup().location
param tags object = {}

@description('Name of the Application Insights resource')
param applicationInsightsName string

@description('Name of the Log Analytics workspace')
param logAnalyticsWorkspaceName string

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-10-02-preview' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    appInsightsConfiguration: {
      connectionString: applicationInsights.properties.ConnectionString
    }
    openTelemetryConfiguration: {
      logsConfiguration: {
        destinations: ['appInsights']
      }
      metricsConfiguration: {
        destinations: [] // appInsights not supported yet
      }
      tracesConfiguration: {
        destinations: ['appInsights']
      }
    }
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: logAnalyticsWorkspaceName
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

output defaultDomain string = containerAppsEnvironment.properties.defaultDomain
output id string = containerAppsEnvironment.id
output name string = containerAppsEnvironment.name
