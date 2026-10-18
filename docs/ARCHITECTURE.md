# Shipyard architecture

```
shipctl.py ──writes──▶ tasks.json ◀──reads── notes_api/tasks_source.py
                                                    │
browser ──HTTP──▶ notes_api/server.py ──▶ notes_api/service.py ──▶ notes_api/repository.py ──▶ notes.db (SQLite)
   ▲                    │ serves dashboard/ at /
   └── dashboard/js/main.js ─▶ api.js (fetch) ─▶ render.js (DOM) ─▶ logic.js (pure rules)
```

## Backend (Python, standard library)
| Module | Responsibility | Must not |
|---|---|---|
| `notes_api/server.py` | routing, JSON in/out, status codes, static files | contain business rules or SQL |
| `notes_api/service.py` | validation, tags, partial updates, error types | know about HTTP or SQL |
| `notes_api/repository.py` | the only SQL (parameterised), tags table, search | validate input |
| `notes_api/tasks_source.py` | read-only view of shipctl's `tasks.json` | write tasks |

## Dashboard (ES modules, no build step)
| Module | Responsibility |
|---|---|
| `js/logic.js` | pure rules: overdue, filters, KPIs, owners, tags, escaping. Unit-tested with `node --test` |
| `js/api.js` | the only `fetch` calls; returns `[]` and logs on failure |
| `js/render.js` | one function per page region; reads the state it is given |
| `js/main.js` | owns `state`, wires events, orchestrates load → render |

## Data flow for a search
`input` event (debounced 200 ms) → `main.js` sets `state.q` → `api.fetchNotes(state)` → `GET /api/notes?q=…` → `service.list` → `repository.list` (LIKE … ESCAPE) → `render.renderNotes/renderTags/renderKpis`.

## Tests
- `tests/` — Python unittest, including end-to-end HTTP tests on an ephemeral port.
- `dashboard/tests/` — node:test for `js/logic.js`.
