@minLength(1)
@description('Primary location for all resources')
param location string

@description('The AI Hub resource name.')
param hubName string
@description('The AI Project resource name.')
param projectName string
@description('The Key Vault resource name.')
param keyVaultName string
@description('The Storage Account resource name.')
param storageAccountName string
@description('The Open AI resource name.')
param openAiName string
@description('The Open AI connection name.')
param openAiConnectionName string
@description('The Open AI model deployments.')
param openAiModelDeployments array = []
@description('The Log Analytics resource name.')
param logAnalyticsName string = ''
@description('The Application Insights resource name.')
param applicationInsightsName string = ''
@description('The Grafana name')
param grafanaName string
@description('The Container Registry resource name.')
param containerRegistryName string = ''
@description('The Azure Search resource name.')
param searchServiceName string = ''
@description('The Azure Search connection name.')
param searchConnectionName string = ''
@description('The Bing resource name.')
param bingName string
@description('The Bing connection name.')
param bingConnectionName string
param tags object = {}
param apimPrincipalId string

module hubDependencies '../ai/hub-dependencies.bicep' = {
  name: 'hubDependencies'
  params: {
    location: location
    tags: tags
    keyVaultName: keyVaultName
    storageAccountName: storageAccountName
    containerRegistryName: containerRegistryName
    applicationInsightsName: applicationInsightsName
    grafanaName: grafanaName
    logAnalyticsName: logAnalyticsName
    openAiName: openAiName
    openAiModelDeployments: openAiModelDeployments
    searchServiceName: searchServiceName
    bingName: bingName
    apimPrincipalId: apimPrincipalId
  }
}

module hub '../ai/hub.bicep' = {
  name: 'hub'
  params: {
    location: location
    tags: tags
    name: hubName
    displayName: hubName
    keyVaultId: hubDependencies.outputs.keyVaultId
    storageAccountId: hubDependencies.outputs.storageAccountId
    containerRegistryId: hubDependencies.outputs.containerRegistryId
    applicationInsightsId: hubDependencies.outputs.applicationInsightsId
    openAiName: hubDependencies.outputs.openAiName
    openAiConnectionName: openAiConnectionName
    aiSearchName: hubDependencies.outputs.searchServiceName
    aiSearchConnectionName: searchConnectionName
    bingName: hubDependencies.outputs.bingName
    bingConnectionName: bingConnectionName
  }
}

module project '../ai/project.bicep' = {
  name: 'project'
  params: {
    location: location
    tags: tags
    name: projectName
    displayName: projectName
    hubName: hub.outputs.name
    keyVaultName: hubDependencies.outputs.keyVaultName
  }
}

// Outputs
// Resource Group
output resourceGroupName string = resourceGroup().name

// Hub
output hubName string = hub.outputs.name
output hubPrincipalId string = hub.outputs.principalId

// Project
output projectName string = project.outputs.name
output projectPrincipalId string = project.outputs.principalId

// Key Vault
output keyVaultName string = hubDependencies.outputs.keyVaultName
output keyVaultEndpoint string = hubDependencies.outputs.keyVaultEndpoint

// Application Insights
output applicationInsightsName string = hubDependencies.outputs.applicationInsightsName
output applicationInsightsId string = hubDependencies.outputs.applicationInsightsId
output applicationInsightsConnectionString string = hubDependencies.outputs.applicationInsightsConnectionString
output logAnalyticsWorkspaceName string = hubDependencies.outputs.logAnalyticsWorkspaceName

// Container Registry
output containerRegistryName string = hubDependencies.outputs.containerRegistryName
output containerRegistryEndpoint string = hubDependencies.outputs.containerRegistryEndpoint

// Storage Account
output storageAccountName string = hubDependencies.outputs.storageAccountName

// Open AI
output openAiName string = hubDependencies.outputs.openAiName
output openAiEndpoint string = hubDependencies.outputs.openAiEndpoint

// Search
output searchServiceName string = hubDependencies.outputs.searchServiceName
output searchServiceEndpoint string = hubDependencies.outputs.searchServiceEndpoint

// Bing Search
output bingName string = hubDependencies.outputs.bingName
output bingEndpoint string = hubDependencies.outputs.bingEndpoint
output bingApiKey string = hubDependencies.outputs.bingApiKey

