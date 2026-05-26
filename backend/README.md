# Luminary backend

FastAPI service powering authentication, recommendations, the chatbot, and the memory layer.

## Quick start

```bash
# from /backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

cp .env.example .env                # fill in real values

# Make sure the database is running (from repo root):
#   docker compose up -d db

uvicorn app.main:app --reload
```

The API is then available on `http://localhost:8000` with interactive docs at `/docs`.

## Layout

```
backend/
├── app/
│   ├── main.py            FastAPI entry point
│   ├── core/              Settings, logging, security helpers
│   ├── api/               Route handlers, grouped by resource
│   ├── models/            SQLModel ORM classes (will be added per sprint)
│   ├── services/          Auth, recommendation, chatbot, memory services
│   └── prompts/           LLM prompt templates as Markdown
├── db/init/               SQL scripts run by docker-entrypoint-initdb
├── tests/                 pytest test suite
├── pyproject.toml
├── Dockerfile
└── .env.example
```

## Testing

```bash
pytest                 # run all tests
pytest --cov=app       # with coverage report
ruff check .           # lint
ruff format .          # format
```

## Conventions

- Endpoint paths live in `app/api/*.py`, grouped by resource (e.g. `auth.py`, `recommendations.py`).
- Pure business logic lives in `app/services/*.py` and is unit-testable without spinning up FastAPI.
- All third-party APIs (LLM, Google Books, TMDb, etc.) are wrapped in an `app/services/<adapter>.py` so they can be mocked in tests and swapped without touching call sites.
- Secrets only come from environment variables loaded by `app/core/config.py`.
