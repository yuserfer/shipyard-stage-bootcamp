# Production Readiness Report: Shipyard v1.4 (Notes API + dashboard)

**Scope:** `notes_api/`, `dashboard/`, `shipctl.py` at the Project 9C checkpoint. **Target:** shared internal VM, whole engineering org.
**Reviewers:** `/engineering-quality:security-review` + `security-reviewer` subagent (read-only), `/code-review`, human engineer of record.

## Risk summary
The code is well layered and fully tested (Python `Ran 54 tests … OK`, dashboard `# pass 10`), SQL is parameterised and static serving is path-safe. But on a shared VM, any colleague's note can run script in everyone's browser (stored XSS), the API is open to the whole network with no authentication, and one oversized request can tie up a worker thread. These are fixable in about a day.

## Findings (severity-ranked, verified)
| # | Severity | Finding | Evidence | Effort |
|---|---|---|---|---|
| F1 | **High** | Stored XSS: note bodies rendered as HTML without escaping | `dashboard/js/render.js:46` `<p>${formatBody(n.body)}</p>`; `dashboard/js/logic.js:43` only converts `**bold**`. Runtime: `node -e "…formatBody('<img src=x onerror=alert(1)>')"` → `"<img src=x onerror=alert(1)>"` (unchanged) | S |
| F2 | **High** | No authentication; server listens on every interface; CORS `*` lets any web page call write endpoints | `notes_api/server.py:128` `host: str = "0.0.0.0"`; `notes_api/server.py:37` `Access-Control-Allow-Origin: *`. Runtime: `python3 scripts/readiness_probe.py` → `bind address default: 0.0.0.0`, `CORS header: *`, `unauthenticated DELETE: HTTP 204` | M |
| F3 | **Medium** | Unbounded request body: the server trusts `Content-Length` and blocks reading it | `notes_api/server.py:64` `self.rfile.read(length)`. Runtime: `Content-Length: 5000000` with a 1-byte body → client `TimeoutError` while the handler thread waits | S |
| F4 | Low | Internal exception details leak to clients | `notes_api/server.py:111` `{"error": repr(exc)}` | S |
| F5 | Low | No request logging by default; failures are invisible in operation | `notes_api/server.py` `log_message` is silent unless `NOTES_API_LOG` is set | S |

### Speculative concerns (not verified; do not block)
- SQLite write contention under many concurrent writers (no load test yet; owner: QA, task "Run load test on Notes API").
- `tasks.json` read on every `GET /api/tasks` may be slow with thousands of tasks.

### Checked and fine
Parameterised SQL only (`repository.py`); `LIKE` wildcards escaped; static path traversal blocked (`server.py:45`); tags validated by regex; no secrets in the repository (`git grep -nE "(api[_-]?key|secret|password|token)"` → no matches in code).

## Top three fixes
| Fix | Change | Owner | Verification |
|---|---|---|---|
| 1 (F1) | `formatBody(escapeHtml(body))`, then apply `**bold**` | Frontend owner | New test in `dashboard/tests/logic.test.mjs`: `<img onerror>` body renders as text; browser check shows the literal text |
| 2 (F2) | Default bind `127.0.0.1`; remove the CORS header (same-origin dashboard); require `Authorization: Bearer <token>` for POST/PATCH/DELETE, token from an env var | Backend owner | HTTP tests: write without token → `401`; `scripts/readiness_probe.py` shows bind `127.0.0.1` and no CORS header |
| 3 (F3) | Reject `Content-Length > 64 KiB` with `413` before reading; add a socket timeout | Backend owner | HTTP test: 70 KiB body → `413` in under a second |

**Recommended next-step owner:** backend owner (fixes 2 and 3), frontend owner (fix 1); engineer of record approves the re-review.

## Recommendation
**Conditional go** for the internal rollout, **only after** fixes 1–3 are merged and their verification tests pass. **No-go** for anything internet-facing until authentication is reviewed again.
