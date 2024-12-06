# AI Hedge Fund

An AI-powered hedge fund that uses multiple agents to make trading decisions. The system employs several specialized agents working together:

1. Market Data Agent - Gathers and preprocesses market data
2. Quantitative Agent - Analyzes technical indicators and generates trading signals
3. Risk Management Agent - Evaluates portfolio risk and sets position limits
4. Portfolio Management Agent - Makes final trading decisions and generates orders

## Prerequisites

### Required Software
- Python 3.9 or higher
- Docker Desktop
- Git

### Python Package Management
- Poetry (Python package manager)
  ```bash
  # Install Poetry
  python -m pip install poetry
  
  # Configure Poetry to create virtualenvs in project directory
  poetry config virtualenvs.in-project true
  ```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ai-hedge-fund.git
   cd ai-hedge-fund
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your API keys
   # Required keys:
   # - OPENAI_API_KEY
   # - FINANCIAL_DATASETS_API_KEY
   ```

4. Local Development:
   ```bash
   # Activate virtual environment
   poetry shell
   
   # Run the application
   python src/agents.py
   ```

5. Docker Development:
   ```bash
   # Build the Docker image
   docker build -t ai-hedge-fund .
   
   # Run with Docker Compose
   docker-compose up
   ```

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
  - [Running the Hedge Fund](#running-the-hedge-fund)
  - [Running the Hedge Fund (with Reasoning)](#running-the-hedge-fund-with-reasoning)
  - [Running the Backtester](#running-the-backtester)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Multi-agent architecture for sophisticated trading decisions
- Technical analysis using MACD, RSI, Bollinger Bands, and OBV
- Risk management with position sizing recommendations
- Portfolio management with automated trading decisions
- Backtesting capabilities with performance analytics
- Support for multiple stock tickers

## Setup

Clone the repository:
```bash
git clone https://github.com/your-repo/ai-hedge-fund.git
cd ai-hedge-fund
```

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Set up your environment variables:
```bash
cp .env.example .env
export OPENAI_API_KEY='your-api-key-here'
export FINANCIAL_DATASETS_API_KEY='your-api-key-here'
```

## Usage

### Running the Hedge Fund

```bash
poetry run python src/agents.py --ticker AAPL
```

**Example Output:**
```json
{
  "action": "buy",
  "quantity": 50000,
}
```

You can optionally specify the start and end dates to make decisions for a specific time period.

```bash
poetry run python src/agents.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01
```

### Running the Hedge Fund (with Reasoning)
This will print the reasoning of each agent to the console.

```bash
poetry run python src/agents.py --ticker AAPL --show-reasoning
```

**Example Output:**
```
==========         Quant Agent          ==========
{
  "signal": "bearish",
  "confidence": 0.5,
  "reasoning": {
    "MACD": {
      "signal": "neutral",
      "details": "MACD Line crossed neither above nor below Signal Line"
    },
    "RSI": {
      "signal": "bearish",
      "details": "RSI is 72.07 (overbought)"
    },
    "Bollinger": {
      "signal": "bearish",
      "details": "Price is above upper band"
    },
    "OBV": {
      "signal": "bullish",
      "details": "OBV slope is 30612582.00 (bullish)"
    }
  }
}
========================================

==========    Risk Management Agent     ==========
{
  "max_position_size": 10000.0,
  "risk_score": 6,
  "trading_action": "hold",
  "reasoning": "The overall signal is bearish with moderate confidence, indicated by overbought RSI and price above the Bollinger band, suggesting potential downside. However, the bullish OBV could offset some bearish pressure. Therefore, it's prudent to hold off on new positions until clearer direction emerges."
}
========================================

==========  Portfolio Management Agent  ==========
{
  "action": "hold",
  "quantity": 0,
  "reasoning": "The team's analysis indicates a bearish outlook with moderate confidence due to overbought RSI and price above the Bollinger band, while the bullish OBV suggests some counterbalancing. The risk management team recommends holding off on new positions until clearer direction emerges. Additionally, the current portfolio has no shares to sell, and the risk profile advises against new purchases."
}
========================================
```

### Running the Backtester

```bash
poetry run python src/backtester.py --ticker AAPL
```

**Example Output:**
```
Starting backtest...
Date         Ticker Action Quantity    Price         Cash    Stock  Total Value
----------------------------------------------------------------------
2024-01-01   AAPL   buy       519.0   192.53        76.93    519.0    100000.00
2024-01-02   AAPL   hold          0   185.64        76.93    519.0     96424.09
2024-01-03   AAPL   hold          0   184.25        76.93    519.0     95702.68
2024-01-04   AAPL   hold          0   181.91        76.93    519.0     94488.22
2024-01-05   AAPL   hold          0   181.18        76.93    519.0     94109.35
2024-01-08   AAPL   sell        519   185.56     96382.57      0.0     96382.57
2024-01-09   AAPL   buy       520.0   185.14       109.77    520.0     96382.57
```

You can optionally specify the start and end dates to backtest over a specific time period.

```bash
poetry run python src/backtester.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01
```

## Project Status

### Current Development Progress

#### Completed Features
- Market Data Agent
  - Basic market data retrieval
  - Data preprocessing pipeline
  - Historical data access

- Quantitative Agent
  - MACD implementation
  - RSI implementation
  - Bollinger Bands implementation
  - OBV implementation
  - Basic signal generation

- Risk Management Agent
  - Position sizing calculations
  - Risk scoring system
  - Maximum position limits
  - Basic reasoning output

- Portfolio Management Agent
  - Basic trading decisions
  - Order generation
  - Multi-agent integration
  - Decision reasoning output

- System Infrastructure
  - Poetry setup
  - Environment configuration
  - Basic CLI interface
  - Logging system
  - Project structure
  - Installation scripts
  - Environment management

- Backtesting
  - Basic backtesting functionality
  - Performance tracking
  - Transaction logging

### Upcoming Development Priorities

#### Next Steps
1. Implement Real-time Data Streaming
2. Develop Advanced Indicator Combinations
3. Enhance Risk Management Metrics
4. Create Portfolio Rebalancing Mechanism
5. Integrate Sentiment Analysis
6. Set Up Advanced Logging and Monitoring
7. Develop Automated Testing Suite

#### Pending Features
- Real-time market data streaming
- Advanced risk metrics
- Portfolio rebalancing
- Sentiment analysis integration
- Web interface
- Performance optimization
- Database integration
- Automated testing suite

### Infrastructure Roadmap

#### Docker and Containerization
- [x] Create Dockerfile
- [x] Docker Compose setup
- [ ] Container orchestration
- [ ] Local testing suite

#### Cloud Deployment
- [ ] Cloud provider selection
- [ ] Infrastructure as Code (IaC)
- [ ] CI/CD Pipeline
- [ ] Monitoring and Logging setup

### Trading Environment

#### Paper Trading
- [x] Paper trading API setup
- [x] Paper trading client implementation
- [ ] Performance tracking
- [ ] Strategy validation framework

#### Production Trading
- [x] Live trading API setup
- [x] Live trading client implementation
- [ ] Production deployment checklist
- [ ] Production monitoring system
- [ ] Alert system for trade execution

## Project Structure
```
ai-hedge-fund/
├── src/
│   ├── agents.py # Main agent definitions and workflow
│   ├── backtester.py # Backtesting functionality
│   ├── tools.py # Technical analysis tools
├── pyproject.toml # Poetry configuration
├── .env.example # Environment variables
└── README.md # Documentation
```

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
