.PHONY: up down logs test build install

# ── Docker Aliases ───────────────────────────
up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

# ── Testing & Setup ─────────────────────────
test:
	uv run pytest tests/ -W ignore

install:
	uv sync --frozen --no-install-project
	uv run pre-commit install -t pre-push

start:
	uv run uvicorn app.main:app --reload

# ── Code Quality ────────────────────────────
lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .
