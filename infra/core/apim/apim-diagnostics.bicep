param apimName string
param applicationInsightsResourceId string
@secure()
param applicationInsightsConnectionString string

var logSettings = {
  headers: [ 
    'Content-type', 'User-agent', 'x-ms-region', 'x-ratelimit-remaining-tokens' , 'x-ratelimit-remaining-requests', 'Ocp-Apim-Subscription-Name', 'Ocp-Apim-Subscription-Id', 'Ocp-Apim-Trace']
  body: { bytes: 8192 }
}

resource logger 'Microsoft.ApiManagement/service/loggers@2022-08-01' = {
  name: '${apimName}/applicationinsights'
  properties: {
    loggerType: 'applicationInsights'
    resourceId: applicationInsightsResourceId
    credentials: {
      connectionString: applicationInsightsConnectionString 
    }
  }
}

resource diagnostic 'Microsoft.ApiManagement/service/diagnostics@2022-08-01' = {
  name: '${apimName}/applicationinsights'
  properties: {
    loggerId: logger.id
    alwaysLog: 'allErrors'
    httpCorrelationProtocol: 'W3C'
    logClientIp: true
    metrics: true
    verbosity: 'verbose'
    sampling: {
      samplingType: 'fixed'
      percentage: 100
    }
    frontend: {
      request: logSettings
      response: logSettings
    }
    backend: {
      request: logSettings
      response: logSettings
    }
  }
}
