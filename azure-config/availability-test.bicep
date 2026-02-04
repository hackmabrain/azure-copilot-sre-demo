// Availability Test (Ping Test) Configuration
// Deploy with: az deployment group create --resource-group rg-sre-agent-demo --template-file availability-test.bicep

param webAppName string = 'azure-copilot-sre-demo'
param appInsightsName string = 'appinsights-azure-copilot-sre-demo'
param webAppUrl string = 'https://azure-copilot-sre-demo.azurewebsites.net'

// Get reference to existing Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

// Availability Test - Home Page
resource availabilityTestHome 'Microsoft.Insights/webtests@2022-06-15' = {
  name: '${webAppName}-home-availability'
  location: appInsights.location
  tags: {
    'hidden-link:${appInsights.id}': 'Resource'
  }
  kind: 'ping'
  properties: {
    Name: 'Home Page Availability Test'
    Description: 'Ping test for home page endpoint'
    Enabled: true
    Frequency: 300 // Test every 5 minutes
    Timeout: 30
    Kind: 'ping'
    RetryEnabled: true
    Locations: [
      {
        Id: 'emea-nl-ams-azr' // Netherlands
      }
      {
        Id: 'emea-gb-db3-azr' // UK South
      }
      {
        Id: 'us-fl-mia-edge' // US East
      }
      {
        Id: 'apac-sg-sin-azr' // Southeast Asia
      }
      {
        Id: 'emea-se-sto-edge' // Sweden (closest)
      }
    ]
    Configuration: {
      WebTest: '<WebTest Name="${webAppName}-home" Id="${guid(webAppName, 'home')}" Enabled="True" CssProjectStructure="" CssIteration="" Timeout="30" WorkItemIds="" xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010" Description="" CredentialUserName="" CredentialPassword="" PreAuthenticate="True" Proxy="default" StopOnError="False" RecordedResultFile="" ResultsLocale=""><Items><Request Method="GET" Guid="${guid(webAppName, 'home', 'request')}" Version="1.1" Url="${webAppUrl}" ThinkTime="0" Timeout="30" ParseDependentRequests="False" FollowRedirects="True" RecordResult="True" Cache="False" ResponseTimeGoal="0" Encoding="utf-8" ExpectedHttpStatusCode="200" ExpectedResponseUrl="" ReportingName="" IgnoreHttpStatusCode="False" /></Items></WebTest>'
    }
    SyntheticMonitorId: '${webAppName}-home-availability'
  }
}

// Availability Test - Health Endpoint
resource availabilityTestHealth 'Microsoft.Insights/webtests@2022-06-15' = {
  name: '${webAppName}-health-availability'
  location: appInsights.location
  tags: {
    'hidden-link:${appInsights.id}': 'Resource'
  }
  kind: 'ping'
  properties: {
    Name: 'Health Endpoint Availability Test'
    Description: 'Ping test for health check endpoint'
    Enabled: true
    Frequency: 300 // Test every 5 minutes
    Timeout: 30
    Kind: 'ping'
    RetryEnabled: true
    Locations: [
      {
        Id: 'emea-nl-ams-azr' // Netherlands
      }
      {
        Id: 'emea-gb-db3-azr' // UK South
      }
      {
        Id: 'us-fl-mia-edge' // US East
      }
      {
        Id: 'apac-sg-sin-azr' // Southeast Asia
      }
      {
        Id: 'emea-se-sto-edge' // Sweden (closest)
      }
    ]
    Configuration: {
      WebTest: '<WebTest Name="${webAppName}-health" Id="${guid(webAppName, 'health')}" Enabled="True" CssProjectStructure="" CssIteration="" Timeout="30" WorkItemIds="" xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010" Description="" CredentialUserName="" CredentialPassword="" PreAuthenticate="True" Proxy="default" StopOnError="False" RecordedResultFile="" ResultsLocale=""><Items><Request Method="GET" Guid="${guid(webAppName, 'health', 'request')}" Version="1.1" Url="${webAppUrl}/healthz" ThinkTime="0" Timeout="30" ParseDependentRequests="False" FollowRedirects="True" RecordResult="True" Cache="False" ResponseTimeGoal="0" Encoding="utf-8" ExpectedHttpStatusCode="200" ExpectedResponseUrl="" ReportingName="" IgnoreHttpStatusCode="False" /></Items></WebTest>'
    }
    SyntheticMonitorId: '${webAppName}-health-availability'
  }
}

// Alert for availability test failures
resource availabilityAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${webAppName}-availability-alert'
  location: 'global'
  properties: {
    description: 'Alert when availability test fails from multiple locations'
    severity: 1
    enabled: true
    scopes: [
      appInsights.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.WebtestLocationAvailabilityCriteria'
      webTestId: availabilityTestHome.id
      componentId: appInsights.id
      failedLocationCount: 2
    }
    actions: []
  }
}

output availabilityTestHomeId string = availabilityTestHome.id
output availabilityTestHealthId string = availabilityTestHealth.id
output availabilityAlertId string = availabilityAlert.id
