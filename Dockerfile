# ──────────────────────────────────────────────
# Stage 1 — deps: install dependencies with uv
# ──────────────────────────────────────────────
FROM python:3.14-slim AS deps

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy only dependency manifests first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install deps into a virtual env inside the image
RUN uv sync --frozen --no-install-project

# ──────────────────────────────────────────────
# Stage 2 — dev: hot-reload for local development
# (used by docker-compose by default)
# ──────────────────────────────────────────────
FROM deps AS dev

WORKDIR /app

# Copy venv from deps stage
COPY --from=deps /app/.venv .venv

# App code is bind-mounted at runtime — no COPY here
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ──────────────────────────────────────────────
# Stage 3 — prod: lean, no uv, no dev tools
# ──────────────────────────────────────────────
FROM python:3.14-slim AS prod

WORKDIR /app

# Copy only the venv (no uv binary needed in prod)
COPY --from=deps /app/.venv .venv

# Copy application code
COPY app/ ./app/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
