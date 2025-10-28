FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY influxdb_queries.py ./
COPY mcp_server.py ./
COPY api_server.py ./

RUN uv sync

EXPOSE 8000

# Run HTTP API server for reverse proxy access
CMD ["uv", "run", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
