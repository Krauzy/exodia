# Runtime And Deployment Context

Local development:

```powershell
npm.cmd run backend
npm.cmd run frontend
```

Backend listens on `http://127.0.0.1:8765` by default.
Frontend Vite listens on `http://127.0.0.1:5173` by default.

Separate instances:

- Web frontend reads `VITE_API_BASE_URL`.
- Electron reads `EXODIA_BACKEND_URL`.
- If `EXODIA_BACKEND_URL` is set, Electron does not spawn a local backend.
- Backend CORS is configured through `EXODIA_ALLOWED_ORIGINS`.

Docker Compose:

- `docker-compose.yml` defines separate `backend` and `frontend` services.
- Backend service runs `pip install -e .` then Uvicorn.
- Frontend service runs `npm install` then Vite host mode.

Vercel:

- `vercel.json` uses Vercel Services with `frontend` rooted at `frontend/` and `backend` rooted at `backend/`.
- `backend/main.py` exposes the FastAPI app as `main:app`.
- Top-level rewrites route `/api/(.*)` to the backend service and all other paths to the frontend service.
- Frontend production fallback uses `/api`.
- Backend registers `/api` aliases when no explicit `EXODIA_API_PREFIX` is configured.

Desktop packaging:

- `frontend/package.json` configures `electron-builder`.
- Current local package targets include Windows NSIS/zip, macOS dmg/zip, and Linux AppImage/deb.
- The README should not claim a GitHub Actions installer workflow unless `.github/workflows/build-installers.yml` exists in the current branch.

Production persistence warning:

- Default `EXODIA_DATABASE_URL` is SQLite.
- Serverless/service deployments need an external persistent database for real user history, targets, scans, and reports.
