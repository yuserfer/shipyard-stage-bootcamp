# Auto-memory review (Project 3)

Auto memory lives outside the repo at `~/.claude/projects/<project>/memory/` (index: `MEMORY.md`). Review it with `/memory`, edit or delete entries directly, and keep only facts that are true, durable and not already in `CLAUDE.md`.

| Entry Claude saved | Decision | Reason |
|---|---|---|
| "Tests must point SHIPCTL_DB at a temp dir" | Removed | Already in `.claude/rules/tests.md`; duplicates drift |
| "User prefers small diffs and wants the test command shown" | Kept | Durable collaboration preference, not a code fact |
| "Release v1.4 target is 2026-11-10" | Kept, dated | Project fact with an absolute date; revisit after the release |
| "shipctl uses argparse subparsers" | Removed | Derivable from the code |

Rule of thumb: CLAUDE.md for team-wide instructions (versioned, reviewed), rules for path-specific conventions, auto memory for personal working context — reviewed like any other input.
