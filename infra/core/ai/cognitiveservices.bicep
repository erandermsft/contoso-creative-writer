metadata description = 'Creates an Azure Cognitive Services instance.'
param name string
param location string = resourceGroup().location
param tags object = {}
@description('The custom subdomain name used to access the API. Defaults to the value of the name parameter.')
param customSubDomainName string = name
param deployments array = []
param kind string = 'AIServices'
param apimPrincipalId string
param cognitiveServicesOpenAIUser string = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'

@allowed([ 'Enabled', 'Disabled' ])
param publicNetworkAccess string = 'Enabled'
param sku object = {
  name: 'S0'
}

param allowedIpRules array = []
param networkAcls object = empty(allowedIpRules) ? {
  defaultAction: 'Allow'
} : {
  ipRules: allowedIpRules
  defaultAction: 'Deny'
}

resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  properties: {
    customSubDomainName: customSubDomainName
    publicNetworkAccess: publicNetworkAccess
    networkAcls: networkAcls
  }
  sku: sku
}

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  parent: account
  name: deployment.name
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
  }
  sku: contains(deployment, 'sku') ? deployment.sku : {
    name: 'Standard'
    capacity: 8
  }
}]

resource csRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(apimPrincipalId)) {
  name: guid(account.id, cognitiveServicesOpenAIUser, apimPrincipalId)
  scope: account
  properties: {
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAIUser)
    principalId: apimPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output endpoint string = account.properties.endpoint
output endpoints object = account.properties.endpoints
output id string = account.id
output name string = account.name
output skuName string = account.sku.name
