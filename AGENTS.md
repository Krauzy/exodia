# Exodia Agent Guide

Use this file as the operational entrypoint for future Codex work in this repository.

## Startup Checklist

1. Run the local context RAG before broad source searches:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\scripts\search-context.ps1 -Query "your task keywords" -Top 5
   ```

2. Read the returned context files, then verify current source with `rg` and direct file reads before editing.
3. Check `git status --short --branch` before changing files. Do not revert user changes.
4. Keep Exodia defensive: authorized targets only, no stealth, credential theft, destructive payloads, exploit chaining, persistence, or firewall bypass.
5. Prefer small changes aligned with the existing FastAPI, SQLAlchemy, React, Vite, Electron, and Tailwind patterns.

## Project Shape

- `backend/`: FastAPI API, SQLAlchemy models, migrations, scan jobs, built-in modules, custom interceptor modules, reports, tests.
- `frontend/`: Electron shell and Vite React renderer, React Query data fetching, Zustand UI state, Tailwind UI.
- `docs/`: architecture, security model, plugin development, authorized-use policy.
- `.agents/`: agent config, context chunks, and the local lexical RAG retriever.
- `vercel.json`: two-service Vercel deployment with Vite frontend and FastAPI backend routed through `/api`.

## Local Commands

Use `npm.cmd` on Windows when PowerShell blocks `npm.ps1`.

```powershell
npm.cmd run backend:lint
npm.cmd run backend:typecheck
npm.cmd run backend:test
npm.cmd run frontend:build
```

Run the app locally:

```powershell
npm.cmd run backend
npm.cmd run frontend
```

Backend health:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health"
```

## Editing Rules

- For backend API behavior, inspect the route in `backend/app/api/routes/`, the schema in `backend/app/schemas/`, and persistence in `backend/app/database/models.py`.
- For scan behavior, inspect `backend/app/jobs/manager.py`, `backend/app/modules/base.py`, and the module implementation under `backend/app/modules/`.
- For frontend API behavior, inspect `frontend/src/services/api.ts`, `frontend/src/types/api.ts`, the relevant page in `frontend/src/features/`, and shared hooks in `frontend/src/hooks/`.
- For desktop behavior, inspect `frontend/electron/`.
- Update tests when changing auth, ownership, scan jobs, custom module validation, reports, or routing.
- Update `.agents/context/` and `.agents/context/index.json` when a change alters architecture, commands, routes, modules, deployment, or safety boundaries.

## Commit Convention

Use the repository convention:

```text
exodia/feature: descricao curta
exodia/refact: descricao curta
exodia/hotfix: descricao curta
exodia/doc: descricao curta
```
