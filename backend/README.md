# Exodia Backend

FastAPI backend for Exodia, a local defensive audit platform for authorized environments.

## Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

## Checks

```bash
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m mypy app
```

## Migrations

```bash
alembic upgrade head
```
