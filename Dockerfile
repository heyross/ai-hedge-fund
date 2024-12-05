# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src/ ./src/
COPY README.md ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Environment variables will be provided at runtime
ENV OPENAI_API_KEY=""
ENV ALPACA_API_KEY=""
ENV ALPACA_SECRET_KEY=""
ENV ALPACA_PAPER_ENDPOINT="https://paper-api.alpaca.markets"
ENV ALPACA_LIVE_ENDPOINT="https://api.alpaca.markets"

# Command to run the application
CMD ["poetry", "run", "python", "src/agents.py"]
