# Azure Copilot & SRE Agent Demo

A sample Flask API demonstrating GitHub Copilot and Azure SRE Agent capabilities.

## Overview

This repository contains a simple Flask API that can be used to demonstrate:
- **GitHub Copilot** code generation capabilities
- **Azure SRE Agent** monitoring and diagnostics
- **Copilot Coding Agent** automated PR creation

## Getting Started

### Prerequisites

- Python 3.9+
- GitHub Copilot license
- Azure subscription (for SRE Agent)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/azure-copilot-sre-demo.git
cd azure-copilot-sre-demo
pip install -r requirements.txt
```

### Running the App

```bash
python src/app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message |
| `GET /api/users` | List users |
| `GET /api/reports` | List reports |

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Azure SRE Agent Documentation](https://learn.microsoft.com/en-us/azure/sre-agent/)

## License

MIT
