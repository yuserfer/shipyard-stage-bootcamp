# Option C: event-sourced append-only log

**Shape.** Every change is an event (`NoteCreated`, `NoteEdited`, `NoteDeleted`) appended to `events.jsonl`. Current state is a projection rebuilt in memory at start-up and updated on each event.

**Data model.** `{"seq": n, "type": "...", "note_id": i, "at": ts, "data": {...}}`; projection `{id: note}`.

**Request flow.** `PATCH` → validate against the projection → append `NoteEdited` (fsync) → apply to projection → respond.

**Testing.** Pure functions for `apply(event, state)` are easy to test; end-to-end tests need start-up replay.

**Risks.** Most moving parts; replay time grows with history; deleting data for privacy requests needs compaction; the team has no event-sourcing experience; the audit trail is the only real benefit and nobody asked for it yet.
