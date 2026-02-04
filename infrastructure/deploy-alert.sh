#!/bin/bash

# Deploy Azure Monitor HTTP 5xx Alert for azure-copilot-sre-demo Web App
# 
# Usage: ./deploy-alert.sh [resource-group] [action-group-id]
#
# Arguments:
#   resource-group  : Target Azure resource group (default: rg-sre-agent-demo)
#   action-group-id : Optional action group resource ID for notifications
#
# Example with action group:
#   ./deploy-alert.sh rg-sre-agent-demo "/subscriptions/272c1bdc-9fac-4d46-b472-ac3c51f3b400/resourceGroups/rg-sre-agent-demo/providers/microsoft.insights/actionGroups/prod-oncall"

set -e

RESOURCE_GROUP="${1:-rg-sre-agent-demo}"
ACTION_GROUP_ID="${2:-}"

echo "Deploying Azure Monitor HTTP 5xx alert..."
echo "Resource Group: $RESOURCE_GROUP"

# Execute deployment
echo "Executing deployment..."
if [ -n "$ACTION_GROUP_ID" ]; then
  echo "Action Group: $ACTION_GROUP_ID"
  az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file alert-http5xx.bicep \
    --parameters alert-http5xx.parameters.json \
    --parameters actionGroupResourceId="$ACTION_GROUP_ID"
else
  echo "Action Group: None (alert will be created without notifications)"
  az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file alert-http5xx.bicep \
    --parameters alert-http5xx.parameters.json
fi

echo "✓ Alert deployed successfully!"
echo ""
echo "To view the alert in Azure Portal:"
echo "https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AlertsManagementBladeV2"

