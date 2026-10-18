# Option A: single module, JSON file store

**Shape.** One file `notes_api.py`: `http.server` handler, validation and persistence together. Notes live in `notes.json`, loaded on every request and rewritten atomically on every change.

**Data model.** `[{id, title, body, created_at, updated_at}]`, ids = max + 1.

**Request flow.** `do_POST` → parse JSON → validate inline → load file → append → write temp file → rename → respond.

**Testing.** Start the server in a thread, point `NOTES_FILE` at a temp file, hit it with `urllib`.

**Risks.** Every write rewrites the whole file (O(n)); concurrent writers need a process-wide lock; validation and HTTP code interleave, so business rules are hard to unit-test without HTTP; search (Project 6) means scanning everything in Python.
