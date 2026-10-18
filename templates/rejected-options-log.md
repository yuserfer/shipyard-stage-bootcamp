# Rejected Options Log

> **How to use.** Fill in one entry for **every** rejected option from a Best-of-N comparison, right after you make the decision, while the reasoning is still fresh. Each entry uses the five required fields. Link the entry to the decision matrix. The last field matters most: it tells a future maintainer when to revisit the decision instead of re-arguing it.

---

## Decision header

| Field | Value |
|---|---|
| Decision | `__________` |
| Date | `__________` |
| Engineer of record | `__________` |
| Selected option | `__________` |
| Decision matrix | `__________` (path or link) |

## Rejected option: `<name>`

| Required field | Entry |
|---|---|
| Summary of the approach | `__________` |
| Main advantages | `__________` |
| Main disadvantages | `__________` |
| Primary reason for rejection | `__________` |
| Conditions under which the approach may become appropriate later | `__________` |

(Copy the block above for each rejected option.)

---

## Example: Shipyard, Project 4

| Field | Value |
|---|---|
| Decision | Notes API backend design |
| Date | 2026-10-14 |
| Engineer of record | Dana Ruiz |
| Selected option | B: layered router -> service -> SQLite repository (weighted 4.20) |
| Decision matrix | `decision/decision-matrix.md` |

### Rejected option: A, single-module JSON file store

| Required field | Entry |
|---|---|
| Summary of the approach | One Python module handles HTTP, validation, and storage. All notes live in one JSON file that is rewritten on every change. |
| Main advantages | Smallest possible code; no schema; trivial to read and demo; zero setup. |
| Main disadvantages | HTTP, validation, and storage are tangled, which makes unit testing hard. The whole-file rewrite is unsafe under concurrent requests. Search and tags would enlarge a single file that already does too much. |
| Primary reason for rejection | Low testability and maintenance scores (3 and 2). Projects 5 and 6 need isolated service tests and an extensible storage layer. |
| Conditions under which the approach may become appropriate later | A throwaway prototype or a single-user demo with fewer than about 100 notes, no concurrency, and no planned features. |

### Rejected option: C, event-sourced append-only log

| Required field | Entry |
|---|---|
| Summary of the approach | Every change is appended as an event (`NoteCreated`, `NoteUpdated`, `NoteDeleted`). Current state is rebuilt by replaying the log, with optional snapshots. |
| Main advantages | Full audit history and point-in-time reconstruction come for free; append-only writes; reducers are pure functions. |
| Main disadvantages | Highest complexity: event versioning, replay cost, and snapshots. "Deleted" notes stay in the log, which is a privacy and retention concern. Too much to build and explain in a 30-minute project. |
| Primary reason for rejection | Lowest simplicity score (1) and a maintenance burden (2) out of proportion to a notes service with no audit requirement. |
| Conditions under which the approach may become appropriate later | A compliance or audit requirement such as "show who changed this release note and when", or a need to rebuild state for incident review. Even then, consider first adding an audit table to option B. |
