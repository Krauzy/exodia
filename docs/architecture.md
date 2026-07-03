# Architecture

Exodia is split into a local Python backend and an Electron React frontend.

## Backend

The backend exposes REST endpoints and an SSE stream:

- `/health`
- `/auth/register`
- `/auth/login`
- `/auth/me`
- `/modules`
- `/targets`
- `/scans`
- `/events/scans/{scan_id}`
- `/reports`
- `/sre/check`
- `/pentest/check`
- `/settings`

FastAPI owns HTTP contracts. SQLAlchemy persists users, targets, scans, findings, reports, module logs, and app
settings in SQLite. Targets, scans, and reports store `user_id`; findings and logs inherit ownership from their
scan. The job manager starts asynchronous scan tasks and publishes events to the in-memory event bus.

Security modules implement `SecurityModule` from `app/modules/base.py`. Each module returns a `ModuleResult` with
normalized findings and raw observation data. Pentest checks are regular modules tagged `PENTEST`; SRE checks are
regular modules tagged `SRE`. User-defined modules are stored as `CustomModule` rows and exposed as module ids in the
form `custom:{id}` with the `CUSTOM` tag.

## Frontend

The frontend can run as a Vite web app against any configured backend URL. `VITE_API_BASE_URL` defines the API
base for web deployments, and `EXODIA_BACKEND_URL` defines it for Electron.

Electron starts the backend process only when no external backend URL is configured. In managed mode it waits for
`/health`, loads the React renderer, and stops the backend on app shutdown. The renderer uses:

- React Query for server state.
- Zustand for local navigation state.
- React Hook Form and Zod for target forms.
- TanStack Table for target listing.
- Recharts for dashboard charts.
- Monaco Editor for report inspection.

The renderer has no direct Node.js access. Electron uses `contextIsolation: true` and `nodeIntegration: false`.

## Authentication and Ownership

The UI stores a local bearer token after login or registration. API requests include that token in the
`Authorization` header. Native `EventSource` cannot send custom headers, so scan event streams pass the token as a
query parameter and the backend still validates that the scan belongs to the authenticated user.

Protected resources are scoped by user:

- Targets are listed, read, updated, and deleted by `Target.user_id`.
- Scans are created only for targets owned by the same user and listed by `Scan.user_id`.
- Reports are generated only from scans owned by the same user and listed by `Report.user_id`.

## Desktop Packaging

GitHub Actions builds installers on native Windows, Linux, and macOS runners. Before `electron-builder`
runs, the workflow creates a platform-native backend executable with PyInstaller and copies it into
`frontend/resources/backend`. The packaged Electron app starts this executable from its resources folder.

For installed apps, runtime data is written under Electron's `userData` directory:

- `backend/exodia.db` for SQLite.
- `backend/plugins` for local plugins.

When no packaged backend executable is present, development builds fall back to Python and `backend-source`. When
`EXODIA_BACKEND_URL` is set, packaged and development Electron shells use that backend instead of spawning Python.

## Scan Flow

1. User registers a target and documents authorized scope.
2. User searches and selects built-in, SRE, PENTEST, or CUSTOM modules and checks the authorization confirmation.
3. Backend creates a pending scan and schedules an async job.
4. Each module runs with bounded options and logs events.
5. Findings are persisted with normalized severity.
6. SSE emits progress and findings to the UI.
7. User generates HTML, Markdown, or JSON reports.

## Custom Module Flow

The Modules page lets an authenticated user create an interceptor module with name, title, description, severity,
tags, and Python code. The code must define `analyze(request, response)`. The backend validates its AST before saving:
imports, dunder access, dynamic execution, arbitrary builtins, class definitions, and top-level statements outside the
function are rejected.

When a custom module runs in a scan, the backend performs a bounded HTTP GET to the target, creates safe request and
response objects, calls `analyze`, and converts returned dictionaries into normalized findings.

## SRE and Pentest Modules

SRE and Pentest checks are normal scan modules. SRE modules are tagged `SRE` and cover DNS, HTTP availability,
latency, redirect behavior, and TLS health. Pentest modules are tagged `PENTEST` and cover bounded rate-limit signals,
CORS Origin behavior, URL token exposure, entity enumeration signals, clickjacking headers, passive SQL error leakage,
and IDOR-sensitive identifier exposure. They do not perform credential guessing, authentication bypass, destructive
payloads, or exploit chaining.
