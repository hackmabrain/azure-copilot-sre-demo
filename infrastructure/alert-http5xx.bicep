@description('Name of the alert')
param alertName string = 'azure-copilot-sre-demo-http5xx-alert'

@description('Description of the alert')
param alertDescription string = 'Alert when HTTP 5xx errors exceed 20 in 5 minutes'

@description('Severity of the alert (0-4, where 0 is critical and 4 is informational)')
@minValue(0)
@maxValue(4)
param alertSeverity int = 2

@description('Resource ID of the web app to monitor')
param webAppResourceId string

@description('Resource ID of the action group to notify')
param actionGroupResourceId string = ''

@description('Evaluation frequency in ISO 8601 duration format')
param evaluationFrequency string = 'PT1M'

@description('Window size in ISO 8601 duration format')
param windowSize string = 'PT5M'

@description('Threshold for HTTP 5xx errors')
param threshold int = 20

@description('Tags to apply to the alert')
param tags object = {}

resource metricAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: alertName
  location: 'global'
  tags: tags
  properties: {
    description: alertDescription
    severity: alertSeverity
    enabled: true
    scopes: [
      webAppResourceId
    ]
    evaluationFrequency: evaluationFrequency
    windowSize: windowSize
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'Http5xxErrors'
          metricName: 'Http5xx'
          metricNamespace: 'Microsoft.Web/sites'
          operator: 'GreaterThan'
          threshold: threshold
          timeAggregation: 'Total'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    autoMitigate: true
    actions: actionGroupResourceId != '' ? [
      {
        actionGroupId: actionGroupResourceId
      }
    ] : []
  }
}

output alertId string = metricAlert.id
output alertName string = metricAlert.name
