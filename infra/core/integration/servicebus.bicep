param location string = resourceGroup().location
param name string

resource sb_ns 'Microsoft.ServiceBus/namespaces@2024-01-01' = {
  name: name
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }

  resource articles 'topics' = {
    name: 'published-articles'

    resource subscription 'subscriptions' = {
      name: 'email-subscription'
      properties: {
        deadLetteringOnFilterEvaluationExceptions: true
        deadLetteringOnMessageExpiration: true
        maxDeliveryCount: 10
      }
    }
  }
  
  resource socialMediaPosts 'topics' = {
    name: 'social-media-posts'

    resource subscription 'subscriptions' = {
      name: 'twitter-subscription'
      properties: {
        deadLetteringOnFilterEvaluationExceptions: true
        deadLetteringOnMessageExpiration: true
        maxDeliveryCount: 10
      }
    }
  }
}

output name string = sb_ns.name



