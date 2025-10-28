FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY influxdb_queries.py ./
COPY mcp_server.py ./

RUN uv sync

# kleine notie: MCP servers normaal invoked by LLM clients 
CMD ["tail", "-f", "/dev/null"] 
# For development/testing, laten we het aan
