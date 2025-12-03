# =============================================================================
# OmniMCP Dockerfile
# Multi-runtime container supporting:
#   - Python 3.12 with uv/uvx for Python-based MCP servers
#   - Node.js 20 LTS with npm/npx for Node-based MCP servers
#   - npx mcp-remote for connecting to remote MCP servers
# =============================================================================

# Base image with uv pre-installed
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Build arguments and environment
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Paris

# Node.js environment variables
ENV NVM_DIR=/root/.nvm
ENV NODE_VERSION=20.11.0

# Install system dependencies
RUN apt update --fix-missing && \
    apt install --yes --no-install-recommends \
        tzdata dialog apt-utils \
        gcc pkg-config git curl build-essential \
        ca-certificates gnupg \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Install NVM and Node.js
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION && \
    nvm use default

# Add node and npm to path
ENV NODE_PATH=$NVM_DIR/versions/node/v$NODE_VERSION/lib/node_modules
ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# Verify installations
RUN node --version && npm --version && npx --version
RUN uv --version && uvx --version

# Setup working directory
WORKDIR /app
RUN chmod -R g+rwx /app

# Create data directories
RUN mkdir -p /data/qdrant /data/tool_offloaded_data /app/config

# Copy project files
COPY . ./

# Install Python dependencies
RUN uv venv && uv sync --frozen --no-dev

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    TRANSPORT=http \
    HOST=0.0.0.0 \
    PORT=8000 \
    QDRANT_DATA_PATH=/data/qdrant \
    TOOL_OFFLOADED_DATA_PATH=/data/tool_offloaded_data \
    CONFIG_PATH=/app/config/mcp-servers.json

EXPOSE 8000

# Run using uv
ENTRYPOINT ["uv", "run", "omnimcp"]
CMD ["--help"]