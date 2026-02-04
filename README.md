# Azure Copilot & SRE Agent Demo

A sample Flask API demonstrating GitHub Copilot and Azure SRE Agent capabilities with comprehensive monitoring and observability.

## Overview

This repository contains a simple Flask API that can be used to demonstrate:
- **GitHub Copilot** code generation capabilities
- **Azure SRE Agent** monitoring and diagnostics
- **Copilot Coding Agent** automated PR creation
- **Azure Application Insights** telemetry and monitoring
- **Azure Monitor** alerting and dashboards

## Features

### API Endpoints
- `GET /` - Welcome message
- `GET /api/users` - List users
- `GET /health` - Legacy health check (backward compatibility)
- `GET /healthz` - Comprehensive health check with system metrics
- `POST /api/orders` - Create a new order with validation

### Monitoring & Observability
- **Application Insights Integration** - Automatic request, dependency, and exception tracking
- **Custom Telemetry** - Order metrics, performance tracking, and custom dimensions
- **Health Checks** - `/healthz` endpoint with CPU, memory, and disk metrics
- **Azure Monitor Alerts** - 5+ alert rules for critical metrics (5xx errors, latency, CPU, memory, health checks)
- **Diagnostic Logs** - HTTP logs, console logs, and platform logs streamed to Log Analytics
- **Availability Tests** - Multi-region ping tests from 5 geographic locations
- **Monitoring Dashboard** - Real-time view of app health, performance, and resource usage

## Getting Started

### Prerequisites

- Python 3.9+
- GitHub Copilot license
- Azure subscription (for SRE Agent)

### Installation

```bash
git clone https://github.com/hackmabrain/azure-copilot-sre-demo.git
cd azure-copilot-sre-demo
pip install -r requirements.txt
```

### Running the App Locally

```bash
# Without Application Insights (local development)
python app.py

# With Application Insights (set connection string)
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=...;IngestionEndpoint=..."
python app.py
```

The API will be available at `http://localhost:8080`

### Running Tests

```bash
pytest
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message with version |
| `/api/users` | GET | List sample users |
| `/health` | GET | Legacy health check |
| `/healthz` | GET | Comprehensive health check with metrics |
| `/api/orders` | POST | Create a new order |

### Example: Create Order

```bash
curl -X POST https://azure-copilot-sre-demo.azurewebsites.net/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "items": [{"product": "Widget", "quantity": 2}],
    "total": 49.99
  }'
```

## Azure Monitoring Setup

The application includes comprehensive monitoring and observability features. See the [Azure Configuration Guide](./azure-config/README.md) for detailed setup instructions.

### Quick Deploy Monitoring Infrastructure

```bash
cd azure-config

# 1. Configure web app (AlwaysOn, health checks, auto-heal)
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file webapp-config.bicep

# 2. Enable diagnostic settings
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file diagnostic-settings.bicep

# 3. Create alert rules
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file alert-rules.bicep \
  --parameters actionGroupEmail='your-email@example.com'

# 4. Setup availability tests
az deployment group create \
  --resource-group rg-sre-agent-demo \
  --template-file availability-test.bicep

# 5. Deploy monitoring dashboard
az portal dashboard create \
  --resource-group rg-sre-agent-demo \
  --name 'azure-copilot-sre-demo-dashboard' \
  --input-path monitoring-dashboard.json
```

### Monitoring Features

- **Application Insights** - Captures all requests, dependencies, exceptions, and custom telemetry
- **Health Endpoint** - `/healthz` provides detailed health status with resource metrics
- **Alert Rules** - Automated alerts for high error rates, latency, CPU, memory, and health check failures
- **Log Analytics** - All logs centralized for querying with KQL
- **Dashboard** - Real-time monitoring of key metrics
- **Availability Tests** - Multi-region uptime monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Web App                            │
│                 (azure-copilot-sre-demo)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Flask Application (app.py)                  │  │
│  │  - API Endpoints                                      │  │
│  │  - Health Checks (/healthz)                           │  │
│  │  - OpenCensus Middleware                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Telemetry
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Insights                            │
│          (appinsights-azure-copilot-sre-demo)               │
│                                                              │
│  - Request tracking                                          │
│  - Exception tracking                                        │
│  - Custom metrics & dimensions                               │
│  - Performance monitoring                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Logs & Metrics
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             Log Analytics Workspace                          │
│            (ws-272c1bdc-swedencent)                         │
│                                                              │
│  - HTTP logs                                                 │
│  - Console logs                                              │
│  - Platform logs                                             │
│  - KQL queries                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Alerts
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Azure Monitor Alerts                        │
│                                                              │
│  - HTTP 5xx rate alerts                                      │
│  - High latency alerts                                       │
│  - CPU/Memory alerts                                         │
│  - Health check failure alerts                               │
└─────────────────────────────────────────────────────────────┘
```

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Azure SRE Agent Documentation](https://learn.microsoft.com/en-us/azure/sre-agent/)

## License

MIT
