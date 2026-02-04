# Azure Infrastructure

This directory contains Infrastructure as Code (IaC) files for deploying and managing Azure resources.

## Azure Monitor Alert for HTTP 5xx Errors

### Overview

The `alert-http5xx.bicep` file defines an Azure Monitor metric alert that monitors HTTP 5xx errors on the `azure-copilot-sre-demo` web app.

**Alert Configuration:**
- **Name:** `azure-copilot-sre-demo-http5xx-alert`
- **Signal:** `Http5xx` metric (Microsoft.Web/sites)
- **Condition:** Total > 20 over 5 minutes
- **Severity:** 2 (Warning)
- **Evaluation Frequency:** 1 minute
- **Window Size:** 5 minutes

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and configured
- Appropriate permissions to create alerts in the target resource group
- Logged in to Azure: `az login`

### Deployment

#### Option 1: Deploy with default settings (no action group)

```bash
cd infrastructure
chmod +x deploy-alert.sh
./deploy-alert.sh
```

#### Option 2: Deploy with a specific resource group

```bash
./deploy-alert.sh rg-sre-agent-demo
```

#### Option 3: Deploy with action group for notifications

```bash
./deploy-alert.sh rg-sre-agent-demo "/subscriptions/272c1bdc-9fac-4d46-b472-ac3c51f3b400/resourceGroups/rg-sre-agent-demo/providers/microsoft.insights/actionGroups/prod-oncall"
```

#### Option 4: Deploy using Azure CLI directly

```bash
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file alert-http5xx.bicep \
  --parameters alert-http5xx.parameters.json
```

### Customization

To customize the alert parameters, edit `alert-http5xx.parameters.json`:

- **threshold**: Change the number of HTTP 5xx errors that trigger the alert
- **evaluationFrequency**: How often the alert condition is evaluated
- **windowSize**: Time window for aggregating metric data
- **alertSeverity**: 0 (Critical), 1 (Error), 2 (Warning), 3 (Informational), 4 (Verbose)
- **actionGroupResourceId**: Resource ID of an action group for notifications

### Verification

After deployment, verify the alert:

1. **Azure Portal:**
   - Navigate to [Alerts Management](https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AlertsManagementBladeV2)
   - Or go to the web app resource → Alerts → Alert rules

2. **Azure CLI:**
   ```bash
   az monitor metrics alert show \
     --name azure-copilot-sre-demo-http5xx-alert \
     --resource-group rg-sre-agent-demo
   ```

### Testing the Alert

To test if the alert fires correctly, you can generate HTTP 5xx errors by:

1. Intentionally causing errors in the application
2. Using load testing tools to trigger error conditions
3. Monitoring the alert status in Azure Portal

### Additional Resources

- [Azure Monitor Alerts Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview)
- [Metric Alert Resource Schema](https://learn.microsoft.com/en-us/azure/templates/microsoft.insights/metricalerts)
- [Web App Metrics](https://learn.microsoft.com/en-us/azure/app-service/web-sites-monitor)
