# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy project files
COPY . .

# Install dependencies
RUN poetry install --only main

# Add src directory to Python path
ENV PYTHONPATH=/app

# Environment variables will be provided at runtime through docker-compose
ENV OPENAI_API_KEY=""
ENV ALPACA_API_KEY=""
ENV ALPACA_SECRET_KEY=""
ENV ALPACA_PAPER_ENDPOINT="https://paper-api.alpaca.markets"
ENV ALPACA_LIVE_ENDPOINT="https://api.alpaca.markets"

# Command to run the application
CMD ["python", "src/agents.py", "--ticker", "AAPL", "--show-reasoning"]
