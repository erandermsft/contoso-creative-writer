param apiManagementName string
param openAiName string
param openAiEndpoint string
param openAIAPIName string = 'openai'
param openAIAPIDescription string = 'Azure OpenAI API inferencing API'
param openAIAPIDisplayName string = 'OpenAI'
param openAIAPIPath string = 'openai'
param openAIAPIVersion string = '2024-02-01'
param openAIAPISpecURL string = 'https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/cognitiveservices/data-plane/AzureOpenAI/inference/stable/${openAIAPIVersion}/inference.json'
param openAISubscriptionName string = 'openai-subscription'
param openAISubscriptionDescription string = 'OpenAI Subscription'

var policyXml = loadTextContent('policy.xml')
var updatedPolicyXml = replace(policyXml, '{backend-id}', openAiName)

resource apimService 'Microsoft.ApiManagement/service@2024-06-01-preview' existing = {
  name: apiManagementName
}

resource api 'Microsoft.ApiManagement/service/apis@2024-06-01-preview' = {
  name: openAIAPIName
  parent: apimService
  properties: {
    apiType: 'http'
    description: openAIAPIDescription
    displayName: openAIAPIDisplayName
    format: 'openapi-link'
    path: openAIAPIPath
    protocols: [
      'https'
    ]
    subscriptionKeyParameterNames: {
      header: 'api-key'
      query: 'api-key'
    }
    subscriptionRequired: true
    type: 'http'
    value: openAIAPISpecURL
  }
}

resource apimPolicy 'Microsoft.ApiManagement/service/apis/policies@2024-06-01-preview' = {
  name: 'policy'
  parent: api
  properties: {
    format: 'rawxml'
    value: updatedPolicyXml
  }
}

resource openAiBackend 'Microsoft.ApiManagement/service/backends@2024-06-01-preview' = {
  name: openAiName
  parent: apimService
  properties: {
    description: 'backend description'
    url: '${openAiEndpoint}openai'
    protocol: 'http'
    circuitBreaker: {
      rules: [
        {
          failureCondition: {
            count: 1
            errorReasons: [
              'Server errors'
            ]
            interval: 'PT5M'
            statusCodeRanges: [
              {
                min: 429
                max: 429
              }
            ]
          }
          name: 'openAIBreakerRule'
          tripDuration: 'PT1M'
          acceptRetryAfter: true
        }
      ]
    }
  }
}

resource apimSubscription 'Microsoft.ApiManagement/service/subscriptions@2024-06-01-preview' = {
  name: openAISubscriptionName
  parent: apimService
  properties: {
    allowTracing: true
    displayName: openAISubscriptionDescription
    scope: '/apis/${api.id}'
    state: 'active'
  }
}

#disable-next-line outputs-should-not-contain-secrets
output subscriptionPrimaryKey string = apimSubscription.listSecrets().primaryKey
