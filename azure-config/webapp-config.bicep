// Web App Configuration for Monitoring Features
// Deploy with: az deployment group create --resource-group rg-sre-agent-demo --template-file webapp-config.bicep

param webAppName string = 'azure-copilot-sre-demo'
param appInsightsName string = 'appinsights-azure-copilot-sre-demo'

// Get reference to existing web app
resource webApp 'Microsoft.Web/sites@2022-09-01' existing = {
  name: webAppName
}

// Get reference to existing Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

// Update Web App configuration
resource webAppConfig 'Microsoft.Web/sites/config@2022-09-01' = {
  name: 'web'
  parent: webApp
  properties: {
    // Enable AlwaysOn for production reliability
    alwaysOn: true
    
    // Health check configuration
    healthCheckPath: '/healthz'
    
    // Auto-heal configuration
    autoHealEnabled: true
    autoHealRules: {
      triggers: {
        statusCodes: [
          {
            status: 500
            subStatus: 0
            count: 10
            timeInterval: '00:05:00'
          }
          {
            status: 503
            subStatus: 0
            count: 5
            timeInterval: '00:05:00'
          }
        ]
        slowRequests: {
          timeTaken: '00:01:00'
          count: 10
          timeInterval: '00:05:00'
        }
      }
      actions: {
        actionType: 'Recycle'
        minProcessExecutionTime: '00:01:00'
      }
    }
    
    // Application Insights settings
    appSettings: [
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: appInsights.properties.ConnectionString
      }
      {
        name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
        value: '~3'
      }
      {
        name: 'XDT_MicrosoftApplicationInsights_Mode'
        value: 'recommended'
      }
    ]
  }
}

output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
