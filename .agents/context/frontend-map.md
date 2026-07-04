# Frontend Map

Frontend root: `frontend/`

Runtime layers:

- `frontend/src/app/App.tsx`: auth gate and active view rendering.
- `frontend/src/components/layout/Sidebar.tsx`: grouped navigation.
- `frontend/src/services/api.ts`: typed API client, auth header injection, SSE subscription, production `/api` fallback.
- `frontend/src/types/api.ts`: TypeScript API contracts mirrored from backend schemas.
- `frontend/src/hooks/useApiQueries.ts`: React Query wrappers for health, targets, modules, scans, and reports.
- `frontend/src/store/useAuthStore.ts`: token/user persistence.
- `frontend/src/store/useAppStore.ts`: selected view, target, and scan state.

Feature pages:

- `features/auth/AuthPage.tsx`: login and registration.
- `features/dashboard/DashboardPage.tsx`: health, target, scan, and module summary.
- `features/targets/*`: list, create, edit, and inspect targets.
- `features/scans/*`: create scans, watch live scan events, inspect results.
- `features/modules/ModulesPage.tsx`: search modules and create custom interceptor modules.
- `features/reports/ReportsPage.tsx`: generate and inspect report outputs.
- `features/settings/SettingsPage.tsx`: application settings.
- `features/about/AboutPage.tsx`: product/safety information.

Electron:

- `frontend/electron/main.ts`: creates the window, starts/stops backend when managed, blocks external window creation.
- `frontend/electron/backend-process.ts`: chooses packaged backend executable or Python fallback, waits for `/health`.
- `frontend/electron/preload.ts`: exposes `window.exodia.apiBaseUrl` and platform.
- Renderer runs with `contextIsolation: true`, `nodeIntegration: false`, and sandbox enabled.

Frontend conventions:

- Use existing UI primitives in `frontend/src/components/ui/`.
- Use React Query for server state and Zustand for local view state.
- Keep API shapes aligned with `frontend/src/types/api.ts` and backend schemas.
- Keep production web API calls relative to `/api`; Electron overrides through `window.exodia.apiBaseUrl`.
