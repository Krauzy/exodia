# Backend Map

Backend root: `backend/`

Important entrypoints:

- `backend/app/main.py`: FastAPI app factory, CORS, router registration, `/api` compatibility aliases.
- `backend/main.py`: Vercel FastAPI service entrypoint exposing `main:app`.
- `backend/app/core/config.py`: environment-backed settings with `EXODIA_` prefix.
- `backend/app/database/session.py`: SQLAlchemy engine/session and startup schema compatibility helpers.
- `backend/app/database/models.py`: users, targets, scans, findings, reports, module logs, app settings, and custom modules.

API routes:

- `auth.py`: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`.
- `modules.py`: list built-in and user custom modules; create user custom modules.
- `targets.py`: user-scoped CRUD for targets.
- `scans.py`: user-scoped scan creation, lookup, logs, and cancellation.
- `events.py`: scan SSE stream with token validation.
- `reports.py`: list, read, and generate reports from owned scans.
- `sre.py`: direct SRE check endpoint.
- `pentest.py`: direct pentest surface check endpoint.
- `settings.py`: persisted application settings.
- `health.py`: health response.

Scan execution:

- `backend/app/jobs/manager.py` owns `JobManager` and `EventBus`.
- `start_scan()` creates an async task for a scan.
- `_run_scan()` sets status, resolves built-in or custom modules, persists findings/logs, computes risk score, and publishes SSE events.
- `cancel_scan()` cancels active tasks and persists cancellation.

Module system:

- Base contract is `SecurityModule` in `backend/app/modules/base.py`.
- Registry is in `backend/app/plugins/registry.py`.
- Built-in modules live under `backend/app/modules/`.
- Local plugin loader is `backend/app/plugins/loader.py`.
- User-created modules are stored in `CustomModule` rows and run through `CustomInterceptorModule`.

Persistence model:

- `User` owns targets, scans, reports, and custom modules.
- `Scan` owns findings, module execution logs, and generated reports.
- Reports currently store generated content in the database.
- Default database is SQLite via `EXODIA_DATABASE_URL`.

Tests:

- `backend/tests/test_api.py`: API, auth, ownership, custom module behavior.
- `backend/tests/test_modules.py`: built-in module behavior.
- `backend/tests/test_scoring_and_reports.py`: scoring and report content.
- `backend/tests/test_target_validation.py`: validation and authorization requirements.
