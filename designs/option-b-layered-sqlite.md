# Option B: layered router / service / SQLite repository

**Shape.** Package `notes_api/` with three layers:
- `server.py` — HTTP only: routing, JSON in/out, status codes.
- `service.py` — business rules: validation, partial updates, error types (`ValidationError` → 400, `NotFound` → 404). No HTTP, no SQL.
- `repository.py` — the only module that writes SQL (`sqlite3`, parameterised queries, one connection guarded by a lock).

**Data model.** Table `notes(id INTEGER PK AUTOINCREMENT, title, body, created_at, updated_at)`; timestamps in UTC with microseconds.

**Request flow.** `PATCH /api/notes/7` → `server` parses → `service.update(7, data)` validates and merges → `repository.update(...)` → JSON.

**Testing.** Service rules unit-tested with an in-memory repository (`:memory:`); end-to-end tests run the real server on port 0.

**Risks.** Three files instead of one; SQLite file locking under heavy concurrent writes (acceptable for an internal tool; WAL mode is the next step).
