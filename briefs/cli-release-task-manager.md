# Engineering brief: `shipctl`, a CLI release task manager

## Outcome
A release manager can track the tasks that must finish before a release, from the terminal, with owners and due dates.

## Context
- Repository: Shipyard (see `README.md`, `SAFETY.md`).
- Python 3.10+ standard library only. No third-party packages, no `requirements.txt`.
- Single entry point `shipctl.py`; tests under `tests/` with `unittest`.

## Capabilities
1. Add a release task (title required).
2. Assign an owner.
3. Set a due date (`YYYY-MM-DD`).
4. List pending tasks (default view), ordered by due date; undated tasks last.
5. Mark a task as completed.
6. Delete a task.
7. Filter the list by owner and/or status (`pending`, `done`, `all`).

## Constraints
- Storage: a JSON file, default `./tasks.json`, overridable with the `SHIPCTL_DB` environment variable (tests must never touch the real file).
- Exit codes are a contract: `0` success, `1` user error (bad input, unknown id), `2` storage/I/O error.
- Errors go to stderr with a one-line `error: ...` message; normal output to stdout.
- Writes must be atomic (write a temp file, then replace).

## Protected areas
- Do not modify `SAFETY.md`, `.claude/`, or anything under `briefs/`.
- Do not commit. Do not push.

## Acceptance criteria
| # | Criterion |
|---|---|
| AC1 | `add "<title>"` prints `Added #<id>: <title>`; ids increase from 1 |
| AC2 | `add` rejects an empty title with exit code 1 |
| AC3 | `assign <id> <owner>` and `due <id> <YYYY-MM-DD>` update the task; invalid dates exit 1 |
| AC4 | `list` shows pending tasks sorted by due date, undated last |
| AC5 | `list --owner X --status S` filters, and the two filters combine (AND) |
| AC6 | `done <id>` and `delete <id>` work; unknown ids exit 1 with `#<id> not found` |
| AC7 | A corrupt `tasks.json` exits 2 with a clear message |
| AC8 | `README.md` documents every command with an example |

## Required evidence (not claims)
- The plan you followed, before any code.
- The exact test command and its raw output.
- A table mapping each acceptance criterion to the test(s) that prove it.
- A short terminal session showing the real CLI output for AC1, AC4 and AC5.

## Process
Propose a plan first and wait for approval. Then implement, test, and stop for review.
