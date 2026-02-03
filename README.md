# Azure Copilot & SRE Agent Demo

A sample Flask API demonstrating GitHub Copilot and Azure SRE Agent capabilities with comprehensive monitoring and observability features.

## Overview

This repository contains a simple Flask API that can be used to demonstrate:
- **GitHub Copilot** code generation capabilities
- **Azure SRE Agent** monitoring and diagnostics
- **Copilot Coding Agent** automated PR creation
- **Application Insights** integration for telemetry and monitoring
- **Enhanced health checks** with detailed status reporting

## Features

- ✅ RESTful API with Flask
- ✅ Application Insights integration for telemetry
- ✅ Enhanced health check endpoint with response time metrics
- ✅ Structured logging
- ✅ Comprehensive error handling
- ✅ Ready for Azure App Service deployment

## Getting Started

### Prerequisites

- Python 3.9+
- GitHub Copilot license
- Azure subscription (for SRE Agent and Application Insights)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/azure-copilot-sre-demo.git
cd azure-copilot-sre-demo
pip install -r requirements.txt
```

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure Application Insights (optional for local development):
   ```bash
   # Get your connection string from Azure Portal or Azure CLI
   az monitor app-insights component show \
     --app appinsights-azure-copilot-sre-demo \
     --resource-group rg-sre-agent-demo \
     --query connectionString
   
   # Add it to your .env file
   APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=...;IngestionEndpoint=..."
   ```

### Running the App

```bash
python app.py
```

The API will be available at `http://localhost:8080`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Welcome message with API version |
| `GET /api/users` | GET | List users |
| `GET /health` | GET | Enhanced health check with detailed status |
| `POST /api/orders` | POST | Create a new order |

### Health Check Response

The `/health` endpoint provides detailed health information:

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

## Monitoring & Observability

This application includes comprehensive monitoring features:

- **Application Insights Integration**: Automatic telemetry collection for requests, dependencies, and exceptions
- **Health Checks**: Detailed health endpoint for Azure App Service health monitoring
- **Structured Logging**: All operations are logged with appropriate levels
- **Performance Metrics**: Response time tracking and measurement

For complete Azure infrastructure setup (diagnostic settings, alerts, auto-heal, etc.), see [AZURE_SETUP.md](AZURE_SETUP.md).

## Deployment to Azure

The application is configured for automatic deployment to Azure App Service via GitHub Actions. See `.github/workflows/main_azure-copilot-sre-demo.yml` for the deployment pipeline.

### Required Azure Configuration

After deployment, configure the following in Azure App Service:

1. **Application Insights**: Set `APPLICATIONINSIGHTS_CONNECTION_STRING` in App Settings
2. **Health Check**: Enable with path `/health`
3. **Always On**: Enable to prevent cold starts
4. **Diagnostic Settings**: Configure log streaming to Log Analytics
5. **Auto-Heal**: Configure automatic recovery rules
6. **Alerts**: Set up monitoring alerts for availability, errors, and performance

See [AZURE_SETUP.md](AZURE_SETUP.md) for detailed setup instructions.

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 style guidelines. Key conventions:
- Use Python 3.11+ features
- Include type hints for function parameters and return values
- Include docstrings for all public functions
- Use environment variables for configuration

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Azure SRE Agent Documentation](https://learn.microsoft.com/en-us/azure/sre-agent/)
- [Application Insights Documentation](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)

## License

MIT
