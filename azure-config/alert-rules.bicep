// Azure Monitor Alert Rules for azure-copilot-sre-demo Web App
// Deploy with: az deployment group create --resource-group rg-sre-agent-demo --template-file alert-rules.bicep

param webAppName string = 'azure-copilot-sre-demo'
param location string = 'swedencentral'
param actionGroupName string = 'ag-sre-demo-alerts'
param actionGroupEmail string = 'alerts@example.com'

// Get reference to existing web app
resource webApp 'Microsoft.Web/sites@2022-09-01' existing = {
  name: webAppName
}

// Action Group for alert notifications
resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: actionGroupName
  location: 'global'
  properties: {
    groupShortName: 'SREAlerts'
    enabled: true
    emailReceivers: [
      {
        name: 'Email Alert'
        emailAddress: actionGroupEmail
        useCommonAlertSchema: true
      }
    ]
  }
}

// Alert 1: High HTTP 5xx Error Rate
resource alert5xxRate 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${webAppName}-high-5xx-rate'
  location: 'global'
  properties: {
    description: 'Alert when HTTP 5xx error rate is high'
    severity: 2
    enabled: true
    scopes: [
      webApp.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'High 5xx rate'
          metricName: 'Http5xx'
          metricNamespace: 'Microsoft.Web/sites'
          operator: 'GreaterThan'
          threshold: 10
          timeAggregation: 'Total'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Alert 2: High Response Time (P95 Latency)
resource alertHighLatency 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${webAppName}-high-latency'
  location: 'global'
  properties: {
    description: 'Alert when response time exceeds 2 seconds'
    severity: 3
    enabled: true
    scopes: [
      webApp.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'High response time'
          metricName: 'HttpResponseTime'
          metricNamespace: 'Microsoft.Web/sites'
          operator: 'GreaterThan'
          threshold: 2
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Alert 3: High CPU Usage
resource alertHighCPU 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${webAppName}-high-cpu'
  location: 'global'
  properties: {
    description: 'Alert when CPU usage exceeds 80%'
    severity: 2
    enabled: true
    scopes: [
      webApp.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'High CPU usage'
          metricName: 'CpuPercentage'
          metricNamespace: 'Microsoft.Web/sites'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Alert 4: High Memory Usage
resource alertHighMemory 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${webAppName}-high-memory'
  location: 'global'
  properties: {
    description: 'Alert when memory usage exceeds 80%'
    severity: 2
    enabled: true
    scopes: [
      webApp.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'High memory usage'
          metricName: 'MemoryPercentage'
          metricNamespace: 'Microsoft.Web/sites'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Alert 5: Health Check Failures
resource alertHealthCheck 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${webAppName}-health-check-failure'
  location: 'global'
  properties: {
    description: 'Alert when health check probe fails'
    severity: 1
    enabled: true
    scopes: [
      webApp.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'Health check failures'
          metricName: 'HealthCheckStatus'
          metricNamespace: 'Microsoft.Web/sites'
          operator: 'LessThan'
          threshold: 100
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// Output for reference
output actionGroupId string = actionGroup.id
output alertIds array = [
  alert5xxRate.id
  alertHighLatency.id
  alertHighCPU.id
  alertHighMemory.id
  alertHealthCheck.id
]
