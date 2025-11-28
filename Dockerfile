FROM python:3.12-slim as base

WORKDIR /app

# Install system deps + Docker CLI
RUN apt-get update && apt-get install -y \
    gcc g++ git postgresql-client \
    ca-certificates curl gnupg lsb-release \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list \
    && apt-get update && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy root workspace metadata
COPY pyproject.toml uv.lock ./

# Copy agents workspace metadata + source
COPY agents/pyproject.toml agents/uv.lock ./agents/
COPY agents/src/ ./agents/src/
COPY agents/knowledge/ ./agents/knowledge/

# Install ALL dependencies (main + agents workspace) into system Python
RUN uv pip install --system -e . -e ./agents

# Copy application code
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/
COPY migrations/ ./migrations/

RUN mkdir -p /app/output /app/agents/output

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN useradd -m -u 1000 pharma_user && \
    chown -R pharma_user:pharma_user /app

USER pharma_user

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
