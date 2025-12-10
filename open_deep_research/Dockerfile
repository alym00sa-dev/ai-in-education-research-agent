# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml ./
COPY langgraph.json ./
COPY README.md ./

# Copy source code
COPY src/ ./src/

# Create empty directories required by pyproject.toml
RUN mkdir -p tests legacy

# Install dependencies using UV
RUN uv pip install --system -e .

# Install langgraph-cli with inmem support
RUN uv pip install --system "langgraph-cli[inmem]"

# Expose port 8000 (LangGraph server default)
EXPOSE 8000

# Start LangGraph server in production mode
CMD ["langgraph", "start", "--host", "0.0.0.0", "--port", "8000"]
