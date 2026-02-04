// Diagnostic Settings for Azure Web App
// Deploy with: az deployment group create --resource-group rg-sre-agent-demo --template-file diagnostic-settings.bicep

param webAppName string = 'azure-copilot-sre-demo'
param logAnalyticsWorkspaceName string = 'ws-272c1bdc-swedencent'

// Get reference to existing web app
resource webApp 'Microsoft.Web/sites@2022-09-01' existing = {
  name: webAppName
}

// Get reference to existing Log Analytics workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: logAnalyticsWorkspaceName
}

// Diagnostic Settings for Web App
resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'send-to-log-analytics'
  scope: webApp
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 30
        }
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 30
        }
      }
      {
        category: 'AppServiceAppLogs'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 30
        }
      }
      {
        category: 'AppServicePlatformLogs'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 30
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: true
          days: 30
        }
      }
    ]
  }
}

output diagnosticSettingsId string = diagnosticSettings.id
