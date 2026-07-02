# Architecture

Exodia is split into a local Python backend and an Electron React frontend.

## Backend

The backend exposes REST endpoints and an SSE stream:

- `/health`
- `/modules`
- `/targets`
- `/scans`
- `/events/scans/{scan_id}`
- `/reports`
- `/sre/check`
- `/settings`

FastAPI owns HTTP contracts. SQLAlchemy persists targets, scans, findings, reports, module logs, and app settings in SQLite. The job manager starts asynchronous scan tasks and publishes events to the in-memory event bus.

Security modules implement `SecurityModule` from `app/modules/base.py`. Each module returns a `ModuleResult` with normalized findings and raw observation data.

## Frontend

Electron starts the backend process, waits for `/health`, loads the React renderer, and stops the backend on app shutdown. The renderer uses:

- React Query for server state.
- Zustand for local navigation state.
- React Hook Form and Zod for target forms.
- TanStack Table for target listing.
- Recharts for dashboard charts.
- Monaco Editor for report inspection.

The renderer has no direct Node.js access. Electron uses `contextIsolation: true` and `nodeIntegration: false`.

## Desktop Packaging

GitHub Actions builds installers on native Windows, Linux, and macOS runners. Before `electron-builder`
runs, the workflow creates a platform-native backend executable with PyInstaller and copies it into
`frontend/resources/backend`. The packaged Electron app starts this executable from its resources folder.

For installed apps, runtime data is written under Electron's `userData` directory:

- `backend/exodia.db` for SQLite.
- `backend/plugins` for local plugins.

When no packaged backend executable is present, development builds fall back to Python and `backend-source`.

## Scan Flow

1. User registers a target and documents authorized scope.
2. User selects modules and checks the authorization confirmation.
3. Backend creates a pending scan and schedules an async job.
4. Each module runs with bounded options and logs events.
5. Findings are persisted with normalized severity.
6. SSE emits progress and findings to the UI.
7. User generates HTML, Markdown, or JSON reports.

## SRE Check Flow

The SRE page sends a single authorized URL to `/sre/check`. The backend performs DNS resolution,
a bounded HTTP request, redirect observation, and HTTPS certificate inspection when applicable.
It returns operational probes, recommendations, and a simple health score without performing
load testing, brute force, exploitation, or destructive behavior.
