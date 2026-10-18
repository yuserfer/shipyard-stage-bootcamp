# Shipyard

Release-management toolkit used in the Claude Code Bootcamp. The engineer of record is the human; Claude proposes, the human reviews and merges.

## Stack
- Python 3.10+ standard library only. Plain HTML/CSS/JavaScript (ES modules) for the dashboard.
- No package managers: never add `requirements.txt`, `pyproject.toml`, or npm dependencies.

## Commands
- Python tests: `python3 -m unittest discover -s tests -q`
- Dashboard tests (when `dashboard/` exists): `node --test dashboard/tests/`
- CLI: `python3 shipctl.py <command>`; set `SHIPCTL_DB` to a scratch file when experimenting.

## Conventions
- Exit codes are a public contract: `0` ok, `1` user error, `2` storage error.
- Errors: one line `error: ...` on stderr. Normal output on stdout.
- Command handlers are `cmd_<name>`; private helpers start with `_`.
- Every behaviour change ships with a test that fails without the change.
- Prefer small, reviewable diffs. Stop and show the diff and test output before any commit.

## Do not
- Do not edit `SAFETY.md`, `.claude/settings.json` or `briefs/`.
- Do not commit, push, or rewrite git history.
- Do not read `.env` or any credentials.
- Do not claim tests pass without showing the command and its raw output.

## More context
- Safety boundary: @SAFETY.md
- Path-specific rules live in `.claude/rules/` (loaded only for matching files).
