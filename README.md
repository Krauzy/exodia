# Exodia

Exodia is a local desktop platform for authorized vulnerability analysis, audit automation, and defensive security reporting.

It is designed for owned, approved, or lab environments. It does not implement destructive, evasive, persistent, malware, credential theft, phishing, reverse shell, brute force, unauthorized exploitation, or firewall bypass capabilities.

## Stack

- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, SQLite, Alembic, httpx, asyncio, SSE, Loguru, pytest, ruff, mypy.
- Frontend: Electron, React, TypeScript, Vite, TailwindCSS, Radix-ready component structure, React Query, Zustand, React Hook Form, Zod, TanStack Table, Recharts, Monaco Editor, Lucide React.
- Packaging: electron-builder.

## Screenshots

Screenshots are intentionally left as placeholders until the first packaged UI build is captured.

- `docs/screenshots/dashboard.png`
- `docs/screenshots/scan-running.png`
- `docs/screenshots/report-viewer.png`

## Development

Install backend dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Run the backend:

```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8765
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run the Vite frontend:

```bash
npm run dev
```

Run the Electron desktop app:

```bash
cd frontend
npm run electron:dev
```

From the repository root, equivalent npm scripts are available:

```bash
npm run backend
npm run frontend
npm run electron
```

## Authentication

Exodia now uses local user authentication. Register or log in from the desktop/web UI before creating targets or
running scans. Targets, scan history, findings, logs, and reports are scoped to the authenticated user.

The backend exposes:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

## Separate Frontend and Backend Instances

The backend and frontend can run independently. The frontend reads `VITE_API_BASE_URL`, and Electron reads
`EXODIA_BACKEND_URL`; when that Electron variable is set, it does not spawn a local Python backend.

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

When the frontend is hosted on a different origin, set `EXODIA_ALLOWED_ORIGINS` on the backend as a JSON list,
for example `["https://app.example.com"]`.

## Build

```bash
cd frontend
npm run electron:dist
```

## GitHub Actions Installers

The workflow in `.github/workflows/build-installers.yml` builds installable desktop artifacts on native runners:

- Windows: NSIS `.exe` installer and `.zip`.
- Linux: `.AppImage` and `.deb`.
- macOS: `.dmg` and `.zip`.

Each runner also builds a platform-native `exodia-backend` executable with PyInstaller and bundles it into the Electron app. Installed apps store the SQLite database and local plugins under the app user-data directory instead of writing inside the installation folder.

Run it manually from GitHub Actions with **Build Installers**, or let it run on pushes to `main`/`master` and pull requests. Download generated installers from the workflow artifacts.

## Project Structure

```text
backend/    FastAPI API, modules, jobs, database, reports, plugins, tests
frontend/   Electron main process and React renderer
docs/       Architecture, security model, plugin docs, authorized-use policy
```

## Built-in Modules

- Web Security Headers Analyzer
- TLS Analyzer
- Robots.txt Checker
- Security.txt Checker
- Technology Fingerprint
- Safe Port Probe
- Pentest modules tagged `PENTEST`: rate limit, CORS reflected Origin, JWT in URL, entity enumeration, clickjacking, SQL Injection exposure, and IDOR review.
- SRE modules tagged `SRE`: DNS, HTTP availability, latency budget, redirect behavior, and TLS health.

## Custom Interceptor Modules

Authenticated users can create custom modules from the Modules page. A custom module runs as a normal scan module
tagged `CUSTOM`. Its Python code must define:

```python
def analyze(request, response):
    return []
```

The backend performs the HTTP request, passes safe request/response objects into the function, validates the AST,
and blocks imports, filesystem access, dynamic execution, dunder access, and unsafe builtins.

## Roadmap

- Add report file persistence and signed report metadata.
- Add richer target ownership evidence fields.
- Add module option forms per plugin.
- Add import/export for local audit projects.
