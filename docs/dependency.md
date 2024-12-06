# System Dependencies and Installation Requirements

## System Requirements

### Operating System Support
- Windows 10/11 64-bit
- Linux (Ubuntu 20.04+ or similar distributions)

### Base Requirements
- Python 3.10 or higher
- Git
- Poetry (Python package manager)
- Ollama (Local LLM runtime)
- 16GB RAM minimum (32GB recommended)
- 50GB free disk space (for models and data)

## Core Dependencies

### Python Environment Management
- Poetry 1.7.0+
- Python 3.10+
- pip (latest version)

### LLM Components
- Ollama runtime
- Compatible LLM models:
  - Llama2
  - Mistral
  - CodeLlama
  - (Other models supported by Ollama)

### Trading Dependencies
- Alpaca Trade API (Paper/Live trading)
- WebSocket support
- Internet connection for market data

### Data Science Stack
- pandas 2.2.0+
- numpy 1.24.0+
- matplotlib 3.9.2+

### API and Web Components
- FastAPI 0.95.1+
- uvicorn 0.22.0+
- websockets 11.0.2+

### AI/ML Components
- langchain 0.0.350+
- langchain-openai 0.0.2+
- langchain-community 0.0.21+
- ollama 0.1.0+

### Development Tools
- black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)
- pytest (testing)
- pre-commit hooks

## System-Specific Requirements

### Windows-Specific
- Windows Terminal (recommended)
- PowerShell 5.1+
- Visual C++ Build Tools
- Windows Subsystem for Linux (optional, for better Docker support)

### Linux-Specific
- build-essential package
- Python development headers
- OpenSSL development packages
- libffi-dev

## Installation Prerequisites

### Windows
1. Enable Windows Terminal
2. Install Visual Studio Build Tools
3. Install Python 3.10+
4. Install Git
5. Configure Windows PowerShell execution policy

### Linux
1. Update package manager
```bash
sudo apt update && sudo apt upgrade -y
```
2. Install system dependencies
```bash
sudo apt install -y build-essential python3-dev python3-pip git curl
```

## Network Requirements
- Outbound access to:
  - GitHub (for repository access)
  - PyPI (for Python packages)
  - Alpaca API endpoints
  - Market data providers
  - Model download endpoints

## Hardware Recommendations

### Minimum Requirements
- CPU: 4 cores
- RAM: 16GB
- Storage: 50GB free space
- Internet: 10Mbps+ stable connection

### Recommended Specifications
- CPU: 8+ cores
- RAM: 32GB
- Storage: 100GB+ SSD
- Internet: 50Mbps+ stable connection

## Development Environment Setup

### Required IDE Extensions
- Python extension
- Git integration
- JSON/YAML support
- Markdown support
- Docker support (optional)

### Recommended Tools
- Docker Desktop (for containerization)
- Postman (API testing)
- pgAdmin (database management)
- Visual Studio Code or PyCharm

## Security Requirements
- Secure storage for API keys
- Environment variable management
- Network firewall access for required services
- User permissions for installation directories

## Monitoring and Logging
- Log directory write permissions
- Disk space monitoring
- System resource monitoring
- Network connectivity monitoring
