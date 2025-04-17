param name string 
param location string
param tags object = {}
param serviceName string = 'apim'
param publisherEmail string = 'noreply@microsoft.com'
param publisherName string = 'Microsoft'
param apimSku string = 'Basicv2'
param apimManagedIdentityType string = 'SystemAssigned'

resource apimService 'Microsoft.ApiManagement/service@2024-06-01-preview' = {
  name: name
  location: location
  sku: {
    name: apimSku
    capacity: 1
  }
  tags: union(tags, { 'azd-service-name': serviceName })
  properties: {
    publisherEmail: publisherEmail
    publisherName: publisherName
  }
  identity: {
    type: apimManagedIdentityType
  }
}


output apimId string = apimService.id
output apimName string = apimService.name
output apimPrincipalId string = apimService.identity.principalId
output apimGatewayUrl string = apimService.properties.gatewayUrl
