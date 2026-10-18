# Engineering brief: Notes API (design tournament)

## Outcome
Release engineers can create, read, update and delete short engineering notes over HTTP, so the dashboard (Project 7) can show them.

## Functional scope
- `GET /api/health` → `{"status": "ok"}`
- `POST /api/notes` `{title, body}` → `201` + note
- `GET /api/notes` → newest first; `GET /api/notes/{id}`
- `PATCH /api/notes/{id}` partial update of `title` and/or `body`
- `DELETE /api/notes/{id}` → `204`
- Validation: title required, ≤ 120 chars; body ≤ 10,000 chars; errors as `{"error": "..."}` with `400`/`404`.

## Constraints
- Python 3.10+ standard library only (`http.server`, `json`, `sqlite3` are fine). No frameworks.
- Tests with `unittest`, against a real server on an ephemeral port.
- Do not modify `shipctl.py`, `SAFETY.md`, `.claude/`, `briefs/`.

## Tournament rules (do this BEFORE writing any code)
1. Propose **three genuinely different** designs. Different means a different shape of the system (module structure, persistence model, consistency model) — not the same design with renamed files.
2. Write each design to `designs/option-<a|b|c>-<slug>.md`: structure, data model, request flow, how it is tested, risks.
3. Score all three in `decision/decision-matrix.md` with these fixed, weighted criteria (1–5):
   simplicity ×2, testability ×3, security ×2, scalability ×1, maintenance ×2.
4. Pick a winner. Do not merge the three into a hybrid unless the hybrid is coherent and you explain why.
5. Record every rejected option in `decision/rejected-options-log.md`: summary, main advantages, main disadvantages, primary reason for rejection, conditions under which it may become appropriate later.
6. Stop for human approval of the choice. Only then implement the winner.

## Required evidence
- The three design files and the filled matrix, before implementation.
- Test command and raw output after implementation.
