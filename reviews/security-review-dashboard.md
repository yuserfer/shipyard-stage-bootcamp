# Security review: Shipyard Notes API + dashboard (reference)

Reviewer: `security-reviewer` subagent (read-only: Read, Grep, Glob). Scope: `notes_api/`, `dashboard/js/`. Every finding cites file:line from the Project 8 checkpoint.

| # | Severity | Finding | Evidence | Fix |
|---|---|---|---|---|
| S1 | High | Stored XSS: note bodies are inserted as HTML without escaping | `dashboard/js/render.js:46` `<p>${formatBody(n.body)}</p>`; `dashboard/js/logic.js:43` `formatBody` only replaces `**bold**` | `formatBody(escapeHtml(body))`; add a test with `<img onerror>` in a body |
| S2 | Medium | Server listens on all interfaces by default | `notes_api/server.py:112` `host: str = "0.0.0.0"` | Default to `127.0.0.1`; opt in to wider binding via env var |
| S3 | Medium | No authentication, and CORS allows any origin to call write endpoints | `notes_api/server.py:35` `Access-Control-Allow-Origin: *` | Remove the header (same-origin dashboard) or restrict it; add a token for writes |
| S4 | Medium | Unbounded request body: `Content-Length` is trusted and read fully | `notes_api/server.py:54` `self.rfile.read(length)` | Reject `length > 64 KiB` with `413` before reading |
| S5 | Low | Internal exception details returned to clients | `notes_api/server.py:95` `{"error": repr(exc)}` | Log the exception server-side; return a generic message |

Not findings (checked): SQL uses parameters only (`repository.py`); `LIKE` wildcards escaped; static file serving rejects paths outside `dashboard/` (`server.py` `_static`, `DASHBOARD_DIR not in target.parents`); tags restricted by regex in `service.py`.

Verdict: BLOCKED for production until S1 is fixed; S2–S4 before any shared deployment.
