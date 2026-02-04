# Azure Monitoring Configuration

This directory contains Azure infrastructure-as-code templates for configuring monitoring, alerting, and observability for the `azure-copilot-sre-demo` web app.

## Overview

The configuration includes:

1. **Application Insights Integration** - Telemetry collection for requests, dependencies, exceptions, and custom traces
2. **Alert Rules** - 5+ alert rules for critical metrics
3. **Diagnostic Settings** - Log streaming to Log Analytics workspace
4. **Health Checks & Auto-Heal** - Automatic recovery from failures
5. **Availability Tests** - Multi-region ping tests
6. **Monitoring Dashboard** - Comprehensive view of app health and performance

## Prerequisites

- Azure CLI installed and logged in
- Contributor access to resource group `rg-sre-agent-demo`
- Existing resources:
  - Web App: `azure-copilot-sre-demo`
  - Application Insights: `appinsights-azure-copilot-sre-demo`
  - Log Analytics Workspace: `ws-272c1bdc-swedencent`

## Deployment Instructions

### 1. Deploy Web App Configuration (AlwaysOn, Health Checks, Auto-Heal)

This configures the web app with:
- AlwaysOn enabled
- Health check path: `/healthz`
- Auto-heal rules for 5xx errors and slow requests
- Application Insights connection string

```bash
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file webapp-config.bicep \
  --parameters webAppName='azure-copilot-sre-demo' \
               appInsightsName='appinsights-azure-copilot-sre-demo'
```

### 2. Deploy Diagnostic Settings

This enables log streaming to Log Analytics:
- AppServiceHTTPLogs
- AppServiceConsoleLogs
- AppServiceAppLogs
- AppServicePlatformLogs
- AllMetrics

```bash
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file diagnostic-settings.bicep \
  --parameters webAppName='azure-copilot-sre-demo' \
               logAnalyticsWorkspaceName='ws-272c1bdc-swedencent'
```

### 3. Deploy Alert Rules

This creates 5 alert rules:
1. High HTTP 5xx error rate (>10 errors in 5 min)
2. High response time (>2 seconds avg)
3. High CPU usage (>80%)
4. High memory usage (>80%)
5. Health check failures (<100% healthy)

**Note:** Update the email address before deploying.

```bash
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file alert-rules.bicep \
  --parameters webAppName='azure-copilot-sre-demo' \
               actionGroupEmail='your-email@example.com'
```

### 4. Deploy Availability Tests

This creates ping tests from 5 geographic locations:
- Netherlands
- UK South
- US East
- Southeast Asia
- Sweden

```bash
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file availability-test.bicep \
  --parameters webAppName='azure-copilot-sre-demo' \
               appInsightsName='appinsights-azure-copilot-sre-demo' \
               webAppUrl='https://azure-copilot-sre-demo.azurewebsites.net'
```

### 5. Deploy Monitoring Dashboard

```bash
az portal dashboard create \
  --resource-group rg-sre-agent-demo \
  --name 'azure-copilot-sre-demo-dashboard' \
  --input-path monitoring-dashboard.json
```

After deployment, get the dashboard URL:

```bash
az portal dashboard show \
  --resource-group rg-sre-agent-demo \
  --name 'azure-copilot-sre-demo-dashboard' \
  --query id -o tsv
```

The dashboard can be accessed in the Azure Portal under: Home > Dashboard > Azure Copilot SRE Demo - Monitoring Dashboard

## Verification

### 1. Verify Application Insights Connection

After deployment, telemetry should appear within 10 minutes:

```bash
# Check if telemetry is being received
az monitor app-insights metrics show \
  --app appinsights-azure-copilot-sre-demo \
  --resource-group rg-sre-agent-demo \
  --metric requests/count \
  --interval PT1H
```

### 2. Verify Health Check Endpoint

```bash
curl https://azure-copilot-sre-demo.azurewebsites.net/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1675456789.123,
  "version": "1.0.0",
  "checks": {
    "cpu_usage_percent": 15.2,
    "memory_usage_percent": 45.8,
    "disk_usage_percent": 32.1
  }
}
```

### 3. Verify Diagnostic Logs in Log Analytics

Query logs in Log Analytics workspace:

```kusto
// HTTP logs
AppServiceHTTPLogs
| where TimeGenerated > ago(1h)
| project TimeGenerated, CsHost, CsMethod, CsUriStem, ScStatus, TimeTaken
| order by TimeGenerated desc

// Application logs
AppServiceConsoleLogs
| where TimeGenerated > ago(1h)
| project TimeGenerated, ResultDescription
| order by TimeGenerated desc

// Platform logs
AppServicePlatformLogs
| where TimeGenerated > ago(1h)
| project TimeGenerated, Level, Message
| order by TimeGenerated desc
```

### 4. Verify Alert Rules

List all alert rules:

```bash
az monitor metrics alert list \
  --resource-group rg-sre-agent-demo \
  --output table
```

### 5. Verify Availability Tests

Check availability test status:

```bash
az monitor app-insights web-test list \
  --resource-group rg-sre-agent-demo \
  --output table
```

## Dashboard Metrics

The monitoring dashboard includes the following visualizations:

1. **Request Rate** - Total requests per minute
2. **HTTP 5xx Errors** - Server error count
3. **Response Time (P95)** - 95th percentile latency
4. **Exception Count** - Application exceptions from App Insights
5. **CPU Usage** - CPU percentage
6. **Memory Usage** - Memory percentage
7. **Thread Count** - Active thread count

## Sample KQL Queries

### Request Performance Analysis

```kusto
requests
| where timestamp > ago(24h)
| summarize 
    count=count(),
    avg_duration=avg(duration),
    p95_duration=percentile(duration, 95),
    p99_duration=percentile(duration, 99)
  by name
| order by count desc
```

### Exception Analysis

```kusto
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc
```

### Custom Dimension Analysis (Order Metrics)

```kusto
traces
| where timestamp > ago(24h)
| where message contains "Order created"
| extend order_total = toreal(customDimensions.order_total)
| summarize 
    total_orders=count(),
    avg_order_value=avg(order_total),
    total_revenue=sum(order_total)
  by bin(timestamp, 1h)
```

## Maintenance

### Update Alert Thresholds

Edit the `alert-rules.bicep` file and redeploy:

```bash
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file alert-rules.bicep
```

### Update Health Check Interval

Edit the `webapp-config.bicep` file and redeploy.

### Add More Availability Test Locations

Edit the `availability-test.bicep` file to add more test locations. Available locations can be listed with:

```bash
az monitor app-insights web-test list-locations --output table
```

## Troubleshooting

### Telemetry Not Appearing

1. Check the Application Insights connection string is set:
   ```bash
   az webapp config appsettings list \
     --name azure-copilot-sre-demo \
     --resource-group rg-sre-agent-demo \
     | grep -i APPLICATIONINSIGHTS
   ```

2. Check application logs for errors:
   ```bash
   az webapp log tail \
     --name azure-copilot-sre-demo \
     --resource-group rg-sre-agent-demo
   ```

### Health Check Failing

1. Test the endpoint directly:
   ```bash
   curl -v https://azure-copilot-sre-demo.azurewebsites.net/healthz
   ```

2. Check health check configuration:
   ```bash
   az webapp config show \
     --name azure-copilot-sre-demo \
     --resource-group rg-sre-agent-demo \
     --query "{healthCheckPath:healthCheckPath,alwaysOn:alwaysOn}"
   ```

### Alerts Not Firing

1. Verify alert rules are enabled:
   ```bash
   az monitor metrics alert show \
     --name azure-copilot-sre-demo-high-5xx-rate \
     --resource-group rg-sre-agent-demo \
     --query enabled
   ```

2. Check metric data is available:
   ```bash
   az monitor metrics list \
     --resource /subscriptions/272c1bdc-9fac-4d46-b472-ac3c51f3b400/resourceGroups/rg-sre-agent-demo/providers/Microsoft.Web/sites/azure-copilot-sre-demo \
     --metric Http5xx
   ```

## Resources

- [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/)
- [Application Insights for Python](https://docs.microsoft.com/azure/azure-monitor/app/opencensus-python)
- [App Service Monitoring](https://docs.microsoft.com/azure/app-service/monitor-app-service)
- [Kusto Query Language (KQL)](https://docs.microsoft.com/azure/data-explorer/kusto/query/)
