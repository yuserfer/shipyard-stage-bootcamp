# Maintainer handoff: Shipyard dashboard

## Start here (15 minutes)
1. `python3 seed.py --force && python3 -m notes_api.server` → open http://localhost:8000/
2. `python3 -m unittest discover -s tests -q` and `node --test dashboard/tests/` — both must be green.
3. Read `docs/ARCHITECTURE.md`, then `dashboard/js/main.js` (entry point).

## How to change things safely
- New rule (e.g. "at risk" tasks): add a pure function to `js/logic.js` with a test first, then render it.
- New API field: service rule + repository change + an HTTP test; never put SQL outside `repository.py`.
- Keep HTML ids stable: `render.js` and the browser check depend on them.

## Known limitations
| Limitation | Impact | Suggested next step |
|---|---|---|
| Note bodies go through `formatBody` without HTML escaping | Stored XSS if a note contains markup | Escape first, then apply `**bold**` (security review, Project 10A) |
| No authentication; CORS allows `*` | Anyone who can reach the port can edit notes | Bind to localhost by default; add an API token |
| Release version `v1.4` and target date are hard-coded | Manual edit per release | Read from a small config endpoint |
| `GET /api/tasks` reads the file on every request | Fine for tens of tasks, not thousands | Cache by file mtime |
| No pagination on `GET /api/notes` | Large lists render slowly | `?limit=&offset=` in the repository |

## Ownership
- Backend (`notes_api/`): backend owner. Dashboard (`dashboard/`): frontend owner. Tests and browser checks: QA owner.
- Engineer of record for merges: the human reviewer, never Claude.
