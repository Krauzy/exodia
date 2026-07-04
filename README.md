# Exodia

Exodia is a defensive audit console for authorized vulnerability analysis, site reliability checks, scan history, and technical reporting.

It is designed for owned, approved, or lab environments. It must not be used for credential theft, phishing, malware, persistence, evasion, stealth scanning, firewall bypass, destructive payloads, reverse shells, unauthorized exploitation, or exploit chaining.

## Features

- Local user authentication with bearer tokens.
- User-scoped targets, scan history, findings, execution logs, custom modules, and reports.
- Target management for web, API, and host assets with authorization scope documentation.
- Searchable modules, targets, and scan flows in the UI.
- Built-in defensive modules for web headers, TLS, robots.txt, security.txt, technology fingerprinting, and safe port probing.
- SRE modules tagged `SRE` for DNS resolution, HTTP availability, latency budget, redirect behavior, and TLS health.
- Pentest modules tagged `PENTEST` for bounded checks around rate-limit signals, CORS reflected Origin, JWT URL exposure, entity enumeration signals, clickjacking headers, passive SQL error leakage, and IDOR review.
- User-created custom interceptor modules tagged `CUSTOM`.
- Custom module code runs as `analyze(request, response)` with AST validation and restricted builtins.
- Async scan execution with persisted findings and module execution logs.
- Live scan progress through Server-Sent Events.
- HTML, Markdown, and JSON report generation.
- Electron desktop shell with managed or external backend modes.
- Separate frontend and backend runtime support for local, Docker, and hosted deployments.
- Vercel Services configuration for a Vite frontend and FastAPI backend routed through `/api`.
- Local project-agent configuration and file-backed context RAG under `.agents/`.

## Stack

- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, Alembic, httpx, asyncio, SSE, Loguru, pytest, ruff, mypy.
- Frontend: Electron, React, TypeScript, Vite, TailwindCSS, React Query, Zustand, React Hook Form, Zod, TanStack Table, Recharts, Monaco Editor, Lucide React.
- Packaging: electron-builder.
- Deployment: Docker Compose for local split services and Vercel Services for hosted frontend/backend split.

## Project Structure

```text
backend/    FastAPI API, modules, jobs, database, reports, plugins, tests
frontend/   Electron main process and React renderer
docs/       Architecture, security model, plugin docs, authorized-use policy
.agents/    Specialized agent config, context chunks, and local RAG search
```

## Development

Install backend dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

From the repository root, run the backend and frontend in separate terminals:

```bash
npm run backend
npm run frontend
```

On Windows PowerShell, use `npm.cmd` if script execution policy blocks `npm.ps1`:

```powershell
npm.cmd run backend
npm.cmd run frontend
```

Open the app at:

```text
http://127.0.0.1:5173/
```

Backend health:

```text
http://127.0.0.1:8765/health
```

Run the Electron desktop app:

```bash
npm run electron
```

## Authentication

Register or log in before creating targets or running scans. Targets, scan history, findings, logs, custom modules, and reports are scoped to the authenticated user.

Backend auth endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

## Separate Frontend And Backend Instances

The backend and frontend can run independently. The frontend reads `VITE_API_BASE_URL`, and Electron reads `EXODIA_BACKEND_URL`. When `EXODIA_BACKEND_URL` is set, Electron does not spawn a local Python backend.

```bash
npm run backend:host
```

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8765 npm run dev:host
```

For Electron against an already running backend:

```bash
cd frontend
EXODIA_BACKEND_URL=http://127.0.0.1:8765 npm run electron:external
```

When the frontend is hosted on a different origin, set `EXODIA_ALLOWED_ORIGINS` on the backend as a JSON list, for example:

```json
["https://app.example.com"]
```

## Docker Compose

Run split services locally:

```bash
docker compose up --build
```

The Compose file starts:

- Backend on `http://127.0.0.1:8765`
- Frontend on `http://127.0.0.1:5173`

## Vercel Services

`vercel.json` configures two services:

- `frontend`: Vite app rooted at `frontend/`
- `backend`: FastAPI app rooted at `backend/`, entrypoint `main:app`

Top-level rewrites route `/api/(.*)` to the backend and all other paths to the frontend. The frontend production fallback uses `/api`, and the backend exposes `/api` aliases when no explicit API prefix is configured.

For production use, configure persistent storage through `EXODIA_DATABASE_URL`. The default SQLite database is suitable for local development, not durable hosted persistence.

## Desktop Build

```bash
cd frontend
npm run electron:dist
```

Configured local targets include:

- Windows: NSIS installer and zip.
- Linux: AppImage and deb.
- macOS: dmg and zip.

There is no installer GitHub Actions workflow in the current branch. Add one before documenting CI-generated installers.

## Built-In Modules

- Web Security Headers Analyzer
- TLS Analyzer
- Robots.txt Checker
- Security.txt Checker
- Technology Fingerprint
- Safe Port Probe
- `PENTEST`: rate limit, CORS reflected Origin, JWT in URL, entity enumeration, clickjacking, SQL Injection exposure, and IDOR review.
- `SRE`: DNS, HTTP availability, latency budget, redirect behavior, and TLS health.

## Custom Interceptor Modules

Authenticated users can create custom modules from the Modules page. A custom module runs as a normal scan module tagged `CUSTOM`. Its Python code must define:

```python
def analyze(request, response):
    return []
```

The backend performs the HTTP request, passes safe request/response objects into the function, validates the AST, and blocks imports, filesystem access, dynamic execution, dunder access, and unsafe builtins.

## Specialized Agent And RAG

This repository includes a project-specialized agent setup:

- `AGENTS.md`: operational guide for future agents.
- `.agents/exodia.agent.json`: machine-readable agent configuration.
- `.agents/context/index.json`: indexed context documents.
- `.agents/context/*.md`: compact architecture, runtime, security, and validation context.
- `.agents/scripts/search-context.ps1`: dependency-free lexical RAG retriever for PowerShell.

Use it before broad source searches:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\scripts\search-context.ps1 -Query "auth scans reports user ownership" -Top 5
```

List indexed context:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\scripts\search-context.ps1 -List
```

The RAG is an orientation cache, not a source-of-truth replacement. Always verify live source before editing.

## Validation

```powershell
npm.cmd run backend:lint
npm.cmd run backend:typecheck
npm.cmd run backend:test
npm.cmd run frontend:build
```

## Next Steps

1. Replace default SQLite persistence in hosted deployments with PostgreSQL or another durable external database.
2. Add a GitHub Actions workflow that builds and publishes Windows, Linux, and macOS installers from native runners.
3. Add CI checks for backend lint, backend typecheck, backend tests, frontend build, and RAG script validation.
4. Add database migrations and configuration for production-grade multi-user deployments.
5. Add signed report metadata, report file persistence, and report integrity verification.
6. Add per-module option forms in the UI based on `ModuleParameter` metadata.
7. Add module execution timeouts, concurrency controls, and cancellation coverage per module.
8. Add richer target authorization evidence fields, including owner, approval window, allowed modules, and operational limits.
9. Add audit logs for authentication, target changes, module creation, scan creation, cancellation, and report generation.
10. Add encrypted secret handling for future integrations instead of storing sensitive values in plain settings.
11. Add role-based access control for analyst, reviewer, and admin workflows.
12. Add export/import for local audit projects, including targets, scans, reports, and custom modules.
13. Add visual regression checks for key frontend pages and responsive layouts.
14. Add a persistent background worker model for long-running scans outside the FastAPI process.
15. Add plugin signing or trust prompts for local plugin loading.
