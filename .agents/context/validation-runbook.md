# Validation Runbook

Use `npm.cmd` on Windows if PowerShell blocks `npm.ps1`.

Backend lint:

```powershell
npm.cmd run backend:lint
```

Backend typecheck:

```powershell
npm.cmd run backend:typecheck
```

Backend tests:

```powershell
npm.cmd run backend:test
```

Frontend production build:

```powershell
npm.cmd run frontend:build
```

Run both local services:

```powershell
npm.cmd run backend
npm.cmd run frontend
```

Health checks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/"
```

RAG validation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\scripts\search-context.ps1 -List
powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\scripts\search-context.ps1 -Query "auth scans reports user ownership" -Top 5
powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\scripts\search-context.ps1 -Query "modulos pentest sre custom interceptor" -Top 5
powershell -NoProfile -ExecutionPolicy Bypass -File .\.agents\scripts\search-context.ps1 -Query "vercel api frontend backend" -Top 5 -Json
```

Expected notes:

- Pytest can emit cache warnings in restricted Windows workspaces; passing tests are still valid.
- Vite may warn about large chunks; this is a build-size concern, not a failing build.
- If a command fails due sandbox path access, rerun with the minimal necessary approval.
