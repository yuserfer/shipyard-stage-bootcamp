# Rejected Options Log: Notes API

## Option A: single module, JSON file store
- **Summary:** one file holds HTTP, validation and persistence; data in `notes.json`.
- **Main advantages:** smallest possible code; zero schema; trivial to read in a demo.
- **Main disadvantages:** whole-file rewrite on every change; business rules tangled with HTTP; search means full scans.
- **Primary reason for rejection:** testability — partial-update rules can only be tested through HTTP.
- **Could become appropriate if:** we need a throwaway prototype or a single-user offline tool with fewer than ~100 notes.

## Option C: event-sourced append-only log
- **Summary:** every change is an appended event; state is a projection rebuilt at start-up.
- **Main advantages:** complete audit trail; time travel; natural fit for a future activity feed.
- **Main disadvantages:** most moving parts; replay cost grows; privacy deletion needs compaction; no team experience.
- **Primary reason for rejection:** complexity without a current requirement (nobody asked for an audit trail).
- **Could become appropriate if:** compliance requires an immutable history of note edits, or the dashboard needs a "what changed" feed.
