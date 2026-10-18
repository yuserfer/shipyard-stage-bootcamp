# Engineering Brief

> **How to use.** Write a brief instead of a one-line prompt whenever a change touches more than one file or has acceptance criteria worth checking. Fill every section and paste the finished brief into Claude Code. Keep the plan-first instruction at the end. Read Claude's plan, challenge it, and approve it before any code is written. You can use plan mode (Shift+Tab until the mode shows `plan`) or rely on the explicit instruction in section 8. The `feature-brief` Skill in the Skills Pack generates this structure from a rough idea.

---

## 1. Outcome
What will be true when this is done? Describe the result, not the activity.

`__________`

## 2. Context
Relevant files, existing behavior, users, and links to earlier decisions.

`__________`

## 3. Constraints
Language, dependencies, style, performance, compatibility, time box.

- `__________`

## 4. Protected areas
Files, directories, data, or systems that must not be changed.

- `__________`

## 5. Acceptance criteria
Each one must be testable, and it must be possible to fail it.

| # | Criterion | How it will be checked |
|---|---|---|
| AC1 | `__________` | `__________` |

## 6. Required evidence
What Claude must show. A claim of completion is not evidence.

- `__________`

## 7. Decision points
Stop and ask me before: `__________`

## 8. Plan-first instruction
> Before editing any file, read the relevant code and propose a numbered plan: the files you will change, the tests you will add, and how each acceptance criterion will be demonstrated. Then stop and wait for my approval. After implementation, map each acceptance criterion to its evidence: the command you ran and its raw output.

---

## Example: Shipyard, Project 2 (`shipctl`)

**1. Outcome.** Release managers can track release tasks from the terminal: add a task, assign an owner, set a due date, list pending tasks, mark tasks done, delete tasks, and filter by owner or status.

**2. Context.** This is a new single-file CLI, `shipctl.py`, in an empty Shipyard repo. Tasks are stored in a JSON file whose path is set by `SHIPCTL_DB` and defaults to `tasks.json`. Users are release managers on macOS, Linux, or WSL.

**3. Constraints.**
- Python 3 standard library only (`argparse`, `json`, `datetime`), with no third-party packages.
- Exit codes: 0 means success, 1 means usage or user error, 2 means an I/O error.
- Writes are atomic (write a temp file, then rename it).
- Tests use `unittest` and live in `tests/`.

**4. Protected areas.** `.env`, `.github/`, and `docs/` must not be modified. No network access.

**5. Acceptance criteria.**

| # | Criterion | Check |
|---|---|---|
| AC1 | `shipctl add "Tag v1.4" --owner dana --due 2026-10-20` creates a pending task with that owner and due date | unit test plus a manual run |
| AC2 | `shipctl list` shows only pending tasks, sorted by due date | unit test |
| AC3 | `shipctl list --owner dana` and `--status done` filter correctly | unit test |
| AC4 | `shipctl done 1` marks task 1 done; `shipctl delete 1` removes it | unit test |
| AC5 | An invalid date or an unknown ID prints `error: ...` to stderr and exits 1 | unit test |
| AC6 | README has a usage example for every command | review |

**6. Required evidence.**
- The full output of `python3 -m unittest discover -s tests -v`, including the exit code.
- A terminal transcript of AC1 to AC4 run against a temporary `SHIPCTL_DB`.
- A table that maps each acceptance criterion to a test name.

**7. Decision points.** Ask me before changing the storage format, adding a subcommand that is not listed above, or adding any dependency.

**8. Plan first.** (Use the instruction above, unchanged.)
