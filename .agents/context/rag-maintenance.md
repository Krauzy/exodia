# RAG Maintenance

The Exodia local RAG is intentionally simple:

- File-backed context chunks under `.agents/context/`.
- A JSON index at `.agents/context/index.json`.
- A dependency-free PowerShell retriever at `.agents/scripts/search-context.ps1`.
- Lexical scoring with accent normalization and a small Portuguese-to-English synonym set.

Update rules:

- Update context docs when source behavior changes.
- Update `index.json` tags and keywords when adding or renaming context files.
- Keep chunks short enough to read quickly.
- Do not treat cached context as source of truth. Always verify live files before edits.
- Prefer adding a focused chunk over making one large document.

Good context categories:

- Project overview.
- Backend map.
- Frontend map.
- Security and authorization.
- Runtime and deployment.
- Validation runbook.
- RAG maintenance.

Good validation queries:

- `auth scans reports user ownership`
- `custom interceptor analyze request response`
- `modulos pentest sre tags`
- `frontend api base url electron`
- `vercel services api rewrite`
