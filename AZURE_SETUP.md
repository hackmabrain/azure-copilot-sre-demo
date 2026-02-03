# Azure Web App Monitoring Setup

This document provides step-by-step instructions for configuring monitoring, observability, and high availability features for the `azure-copilot-sre-demo` Azure Web App.

## Prerequisites

- Azure CLI installed and authenticated
- Appropriate permissions on the Azure subscription and resource group
- Resource details:
  - **Resource Group**: `rg-sre-agent-demo`
  - **Web App**: `azure-copilot-sre-demo`
  - **Location**: Sweden Central
  - **App Service Plan**: `plan-azure-copilot-sre-demo`

## 1. Enable Application Insights

### Option A: Configure via Azure Portal

1. Navigate to your Web App in the Azure Portal
2. Go to **Application Insights** under **Settings**
3. Click **Turn on Application Insights**
4. Select the existing Application Insights resource: `appinsights-azure-copilot-sre-demo`
5. Click **Apply**

### Option B: Configure via Azure CLI

```bash
# Get the Application Insights instrumentation key
AI_RESOURCE="appinsights-azure-copilot-sre-demo"
RESOURCE_GROUP="rg-sre-agent-demo"
WEB_APP="azure-copilot-sre-demo"

# Get the connection string
AI_CONNECTION_STRING=$(az monitor app-insights component show \
  --app $AI_RESOURCE \
  --resource-group $RESOURCE_GROUP \
  --query connectionString \
  --output tsv)

# Configure the Web App with Application Insights
az webapp config appsettings set \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="$AI_CONNECTION_STRING"

# Verify the setting
az webapp config appsettings list \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --query "[?name=='APPLICATIONINSIGHTS_CONNECTION_STRING']"
```

## 2. Configure Diagnostic Settings → Log Analytics

```bash
WEB_APP="azure-copilot-sre-demo"
RESOURCE_GROUP="rg-sre-agent-demo"
WORKSPACE="ws-272c1bdc-swedencent"

# Get the Web App resource ID
WEB_APP_ID=$(az webapp show \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

# Get the Log Analytics workspace resource ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --workspace-name $WORKSPACE \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

# Create diagnostic settings for the Web App
az monitor diagnostic-settings create \
  --name "DiagnosticsToLogAnalytics" \
  --resource $WEB_APP_ID \
  --workspace $WORKSPACE_ID \
  --logs '[
    {
      "category": "AppServiceHTTPLogs",
      "enabled": true
    },
    {
      "category": "AppServiceConsoleLogs",
      "enabled": true
    },
    {
      "category": "AppServiceAppLogs",
      "enabled": true
    },
    {
      "category": "AppServiceAuditLogs",
      "enabled": true
    },
    {
      "category": "AppServiceIPSecAuditLogs",
      "enabled": true
    },
    {
      "category": "AppServicePlatformLogs",
      "enabled": true
    }
  ]' \
  --metrics '[
    {
      "category": "AllMetrics",
      "enabled": true
    }
  ]'

# Verify diagnostic settings
az monitor diagnostic-settings show \
  --name "DiagnosticsToLogAnalytics" \
  --resource $WEB_APP_ID
```

## 3. Enable Health Check

```bash
WEB_APP="azure-copilot-sre-demo"
RESOURCE_GROUP="rg-sre-agent-demo"

# Configure health check path
az webapp config set \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --generic-configurations '{"healthCheckPath": "/health"}'

# Verify health check configuration
az webapp config show \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --query "healthCheckPath"
```

**Note**: The `/health` endpoint is already implemented in the Flask application and returns detailed health information including response time and system checks.

## 4. Enable Always On

```bash
WEB_APP="azure-copilot-sre-demo"
RESOURCE_GROUP="rg-sre-agent-demo"

# Enable Always On to prevent cold starts
az webapp config set \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --always-on true

# Verify Always On is enabled
az webapp config show \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --query "alwaysOn"
```

**Benefits of Always On**:
- Reduces cold start times
- Keeps the application warm and responsive
- Improves overall availability

## 5. Configure Auto-Heal Rules

```bash
WEB_APP="azure-copilot-sre-demo"
RESOURCE_GROUP="rg-sre-agent-demo"

# Enable auto-heal with sample rules
az webapp config set \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --auto-heal-enabled true

# Configure auto-heal rules via Azure Portal or ARM template
# Example rules to configure:
# 1. Recycle on high memory (> 1GB for 60 seconds)
# 2. Recycle on frequent 5xx errors (> 10 in 5 minutes)
# 3. Recycle on slow requests (> 30 seconds)
```

### Auto-Heal Configuration (via Portal)

1. Navigate to **Diagnose and solve problems**
2. Select **Diagnostic Tools**
3. Click **Auto Healing**
4. Configure conditions:
   - **Request count**: Trigger after 100 requests with > 5% 5xx errors
   - **Slow requests**: Trigger if requests take > 30 seconds
   - **Memory limit**: Trigger if memory usage > 1GB for 60 seconds
5. Configure action: **Recycle Process**

## 6. Create Baseline Alerts

### Alert for High Error Rate (5xx)

```bash
WEB_APP="azure-copilot-sre-demo"
RESOURCE_GROUP="rg-sre-agent-demo"
ACTION_GROUP="application insights smart detection"

# Get the Web App resource ID
WEB_APP_ID=$(az webapp show \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

# Create alert for HTTP 5xx errors
az monitor metrics alert create \
  --name "High-5xx-Error-Rate" \
  --resource-group $RESOURCE_GROUP \
  --scopes $WEB_APP_ID \
  --condition "avg Http5xx > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --description "Alert when 5xx error rate exceeds 5 requests in 5 minutes" \
  --severity 2
```

### Alert for High Response Time

```bash
# Create alert for high response time
az monitor metrics alert create \
  --name "High-Response-Time" \
  --resource-group $RESOURCE_GROUP \
  --scopes $WEB_APP_ID \
  --condition "avg ResponseTime > 5000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --description "Alert when average response time exceeds 5 seconds" \
  --severity 3
```

### Alert for High CPU Usage

```bash
# Get the App Service Plan resource ID
APP_SERVICE_PLAN_ID=$(az appservice plan show \
  --name "plan-azure-copilot-sre-demo" \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

# Create alert for high CPU usage
az monitor metrics alert create \
  --name "High-CPU-Usage" \
  --resource-group $RESOURCE_GROUP \
  --scopes $APP_SERVICE_PLAN_ID \
  --condition "avg CpuPercentage > 80" \
  --window-size 10m \
  --evaluation-frequency 5m \
  --description "Alert when CPU usage exceeds 80% for 10 minutes" \
  --severity 2
```

### Alert for High Memory Usage

```bash
# Create alert for high memory usage
az monitor metrics alert create \
  --name "High-Memory-Usage" \
  --resource-group $RESOURCE_GROUP \
  --scopes $APP_SERVICE_PLAN_ID \
  --condition "avg MemoryPercentage > 85" \
  --window-size 10m \
  --evaluation-frequency 5m \
  --description "Alert when memory usage exceeds 85% for 10 minutes" \
  --severity 2
```

### Alert for Low Availability

```bash
# Create alert for availability drops
az monitor metrics alert create \
  --name "Low-Availability" \
  --resource-group $RESOURCE_GROUP \
  --scopes $WEB_APP_ID \
  --condition "avg HealthCheckStatus < 99" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --description "Alert when availability drops below 99%" \
  --severity 1
```

## 7. Verification Steps

### Verify Application Insights Integration

```bash
# Check that telemetry is being sent
# 1. Navigate to Application Insights in Azure Portal
# 2. Go to Live Metrics to see real-time telemetry
# 3. Check Application Map for dependencies
# 4. Review Performance and Failures tabs

# Or use Azure CLI to query recent requests
AI_RESOURCE="appinsights-azure-copilot-sre-demo"
az monitor app-insights query \
  --app $AI_RESOURCE \
  --analytics-query "requests | take 10" \
  --resource-group $RESOURCE_GROUP
```

### Verify Diagnostic Logs

```bash
# Query Log Analytics for recent logs
WORKSPACE="ws-272c1bdc-swedencent"

az monitor log-analytics query \
  --workspace $WORKSPACE \
  --analytics-query "AppServiceHTTPLogs | take 10" \
  --resource-group $RESOURCE_GROUP
```

### Test Health Check Endpoint

```bash
# Test the health check endpoint
WEBAPP_URL="https://azure-copilot-sre-demo-fadjcnb8hmhsfngh.swedencentral-01.azurewebsites.net"

curl -s "$WEBAPP_URL/health" | jq
```

Expected response:
```json
{
  "status": "healthy",
  "message": "App is running",
  "timestamp": "2024-02-03T23:30:00.000Z",
  "version": "1.0.0",
  "response_time_ms": 12.34,
  "checks": {
    "application_insights": {
      "status": "configured"
    },
    "environment": {
      "status": "ok",
      "python_version": "3.11.0"
    }
  }
}
```

### Verify Alerts

```bash
# List all alerts
az monitor metrics alert list \
  --resource-group $RESOURCE_GROUP \
  --output table

# Test an alert by triggering its condition (e.g., generate 5xx errors)
```

## 8. Post-Deployment Checklist

- [ ] Application Insights connection string configured
- [ ] Telemetry visible in Application Insights (requests, dependencies, exceptions)
- [ ] Diagnostic settings created with logs streaming to Log Analytics
- [ ] Health check enabled and responding correctly
- [ ] Always On enabled
- [ ] Auto-Heal rules configured
- [ ] Baseline alerts created and tested
- [ ] Alerts routed to appropriate action group

## 9. Monitoring Dashboard

After completing the setup, create a monitoring dashboard:

1. Navigate to Azure Portal
2. Create a new Dashboard
3. Add the following tiles:
   - Application Insights: Request rate and response time
   - Application Insights: Failed requests
   - Web App: CPU and Memory usage
   - Web App: HTTP 5xx errors
   - Log Analytics: Recent console logs
   - Alerts: Active alerts

## 10. Additional Recommendations

### Security Considerations

```bash
# Review and tighten IP restrictions if needed
az webapp config access-restriction show \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP

# Example: Add IP restriction (optional)
# az webapp config access-restriction add \
#   --name $WEB_APP \
#   --resource-group $RESOURCE_GROUP \
#   --rule-name "AllowOfficeIP" \
#   --action Allow \
#   --ip-address "203.0.113.0/24" \
#   --priority 100
```

### Performance Optimization

- Monitor the Basic B2 plan performance
- Consider scaling up if sustained load increases
- Current average CPU: ~0.03% (very low)
- Scale up if CPU consistently exceeds 70%

### Backup and Disaster Recovery

```bash
# Configure automated backups (requires Standard tier or higher)
# Current plan: Basic B2 (backups not available)
# To enable backups, upgrade to Standard or Premium tier
```

## Support and Resources

- [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/)
- [Application Insights Documentation](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [App Service Diagnostics](https://docs.microsoft.com/azure/app-service/overview-diagnostics)
- [Auto-Healing Documentation](https://azure.github.io/AppService/2018/09/10/Announcing-the-New-Auto-Healing-Experience-in-App-Service-Diagnostics.html)
