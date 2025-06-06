param name string
param location string = resourceGroup().location
param resourceGroupName string
param tags object = {}

param identityName string
param identityId string
param containerAppsEnvironmentName string
param containerRegistryName string
param serviceName string = 'api'
param openAi_4_DeploymentName string
param openAi_4_eval_DeploymentName string
param openAi_o3_mini_DeploymentName string
param openAiEndpoint string
param openAiName string
param bingName string
param openAiApiVersion string
param openAiEmbeddingDeploymentName string
param openAiType string
param aiSearchEndpoint string
param aiSearchIndexName string
param appinsights_Connectionstring string
param aiProjectName string
param subscriptionId string
param apimGatewayUrl string
param bingApiEndpoint string

@secure()
param bingApiKey string
@secure()
param apimSubscriptionKey string


module app '../core/host/container-app-upsert.bicep' = {
  name: '${serviceName}-container-app-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    identityName: identityName
    identityType: 'UserAssigned'
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    secrets: {
      'bing-search-key': bingApiKey
      'apim-subscription-key': apimSubscriptionKey
    }
    env: [
      {
        name: 'AZURE_LOCATION'
        value: location
      }
      {
        name: 'AZURE_RESOURCE_GROUP'
        value: resourceGroupName
      }
      {
        name: 'AZURE_SUBSCRIPTION_ID'
        value: subscriptionId
      }
      {
        name: 'AZURE_CLIENT_ID'
        value: identityId
      }
      {
        name: 'AZURE_SEARCH_ENDPOINT'
        value: aiSearchEndpoint
      }
      {
        name: 'AZUREAISEARCH__INDEX_NAME'
        value: aiSearchIndexName
      }
      {
        name: 'OPENAI_TYPE'
        value: openAiType
      }
      {
        name: 'AZURE_OPENAI_API_VERSION'
        value: openAiApiVersion
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: openAiEndpoint
      }
      {
        name: 'AZURE_OPENAI_NAME'
        value: openAiName
      }
      {
        name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
        value: openAi_4_DeploymentName
      }
      {
        name: 'AZURE_OPENAI_4_EVAL_DEPLOYMENT_NAME'
        value: openAi_4_eval_DeploymentName
      }
      {
        name: 'AZURE_OPENAI_O3_MINI_DEPLOYMENT_NAME'
        value: openAi_o3_mini_DeploymentName
      }
      {
        name: 'AZURE_AI_PROJECT_NAME'
        value: aiProjectName
      }
      {
        name: 'AZURE_EMBEDDING_NAME'
        value: openAiEmbeddingDeploymentName
      }
      {
        name: 'APPINSIGHTS_CONNECTIONSTRING'
        value: appinsights_Connectionstring
      }
      {
        name: 'BING_SEARCH_ENDPOINT'
        value: bingApiEndpoint
      }
      {
        name: 'BING_SEARCH_KEY'
        secretRef: 'bing-search-key'
      }
      {
        name: 'BING_SEARCH_NAME'
        value: bingName
      }
      {
        name: 'APIM_ENDPOINT'
        value: apimGatewayUrl
      }
      {
        name: 'APIM_SUBSCRIPTION_KEY'
        secretRef: 'apim-subscription-key'
      }
      {
        name: 'MCP_SERVER_URL'
        value: 'http://mcp-server'
      }
    ]
    targetPort: 80
  }
}

output SERVICE_ACA_NAME string = app.outputs.name
output SERVICE_ACA_URI string = app.outputs.uri
output SERVICE_ACA_IMAGE_NAME string = app.outputs.imageName
