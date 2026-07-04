# Project Overview

Exodia is a defensive audit console for authorized vulnerability analysis, operational checks, scan history, and reporting.

The project is split into:

- `backend/`: Python 3.12 FastAPI app with Pydantic v2, SQLAlchemy 2.x, SQLite, Alembic, async scan jobs, SSE events, report exporters, plugin loading, and tests.
- `frontend/`: Vite React renderer and Electron shell with TypeScript, Tailwind, React Query, Zustand, React Hook Form, Zod, TanStack Table, Recharts, Monaco Editor, and Lucide icons.
- `docs/`: architecture, security model, authorized-use policy, and plugin development guidance.
- `.agents/`: local agent configuration and context RAG.

Core product capabilities:

- Local authentication with bearer tokens.
- User-scoped targets, scans, findings, logs, custom modules, and reports.
- Built-in modules for web headers, TLS, robots.txt, security.txt, technology fingerprinting, and safe port probing.
- SRE modules tagged `SRE` for DNS, HTTP availability, latency, redirects, and TLS health.
- Pentest modules tagged `PENTEST` for bounded checks around rate-limit signals, CORS reflection, JWT URL exposure, entity enumeration signals, clickjacking headers, SQL error exposure, and IDOR review.
- User-created custom interceptor modules with constrained Python `analyze(request, response)` code.
- Live scan progress through SSE and persisted module execution logs.
- HTML, Markdown, and JSON report generation.
- Electron desktop packaging support and Vercel two-service deployment config.

Safety posture:

- Exodia is for owned, approved, or lab environments only.
- Scans require explicit authorization confirmation.
- Built-in modules avoid command execution and destructive probes.
- The custom interceptor validator blocks imports, dunder access, unsafe builtins, dynamic calls, classes, and top-level statements outside `analyze`.
