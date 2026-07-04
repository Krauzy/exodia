# Security And Authorization Context

Exodia must remain a defensive, authorized-use tool.

Mandatory boundaries:

- Do not add credential theft, phishing, malware, persistence, evasion, stealth scanning, reverse shells, firewall bypass, destructive payloads, or automated exploitation.
- Do not turn rate-limit checks into credential brute force. Current behavior is bounded signaling, not guessing.
- Require explicit authorization confirmation before scans and direct SRE/Pentest checks.
- Preserve user ownership checks for targets, scans, reports, and custom modules.
- Keep health public, but keep operational resources authenticated.

Authentication:

- Backend token helpers live in `backend/app/core/auth.py`.
- Protected dependencies live in `backend/app/api/dependencies.py`.
- Frontend stores auth through `frontend/src/store/useAuthStore.ts`.
- API calls inject bearer tokens in `frontend/src/services/api.ts`.
- SSE uses token query parameters because native `EventSource` cannot send custom headers.

Custom interceptor modules:

- Users create custom modules with name, title, description, severity, tags, and Python code.
- Code must define exactly `analyze(request, response)`.
- The validator in `backend/app/modules/custom_interceptor.py` blocks imports, dunder access, unsafe builtins, dynamic calls, classes, lambdas, top-level statements outside the function, and several control-flow constructs.
- The backend performs the HTTP request and passes immutable request/response objects into the function.

Reports:

- Generated reports include authorized-use disclaimers.
- Reports are generated only from scans owned by the authenticated user.

When changing security-sensitive code, run:

```powershell
npm.cmd run backend:lint
npm.cmd run backend:typecheck
npm.cmd run backend:test
```
