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
COPY server.py ./

# Create empty directories required by pyproject.toml
RUN mkdir -p tests legacy

# Install dependencies using UV
RUN uv pip install --system -e .

# Install FastAPI and uvicorn for the server
RUN uv pip install --system fastapi uvicorn[standard]

# Expose port 8000
EXPOSE 8000

# Start custom FastAPI server
CMD ["python", "server.py"]
