---
name: change-review
description: Review a Shipyard change (shipctl, Notes API, dashboard) against the seven-point Review Before Merge checklist (scope, diff, tests, security, runtime, rollback, handoff) and return a PASS / FAIL / NOT VERIFIED verdict per point, each backed by quoted command output or file:line evidence. Read-only; never commits or fixes.
when_to_use: Use when the user says "review this change", "review before merge", "is this ready to merge", "check my diff", "run the checklist", or after Claude finishes implementing a feature or bug fix and before anything is committed or merged.
argument-hint: "[optional: brief/acceptance-criteria file, branch, or files to focus on]"
allowed-tools: Read Grep Glob Bash(git diff *) Bash(git status *) Bash(git log *)
---

# Change Review (Review Before Merge)

**Focus / scope source:** $ARGUMENTS

If no argument was given, use the acceptance criteria from this conversation. If
there are none, ask the user what the change was supposed to do, then continue.

## Purpose

A completion claim is not evidence. This skill walks the seven-point checklist in
[checklist.md](checklist.md) and returns a verdict a human can trust because every
point cites a command and its real output, or a file and line.

## Shipyard specifics

- Protected areas (any edit is an automatic BLOCKED): `SAFETY.md`, `.claude/settings.json`, `briefs/`.
- Layering rules to check in the diff: SQL only in `notes_api/repository.py`; validation only in
  `notes_api/service.py`; `fetch` only in `dashboard/js/api.js`; pure rules in `dashboard/js/logic.js`.
- Every API value inserted into HTML must pass through `escapeHtml` (see `dashboard/js/logic.js`).
- Exit-code contract for `shipctl.py`: 0 ok, 1 user error, 2 storage error. Changing it is a FAIL on point 1.
- Runtime evidence for dashboard changes: `/browser-verification` at 1280 px and 390 px, or the
  screenshots in `evidence/`.

## Procedure

1. **Establish the baseline.** Identify the approved scope: brief file, issue, or
   acceptance criteria. List the files that were expected to change.
2. **Collect the change.** Run and keep the output of:
   - `git status --short`
   - `git diff --stat` and `git diff --staged --stat`
   - `git diff` and `git diff --staged` (read in full; for large diffs, file by file)
   - `git log --oneline -5`
   Include untracked files from `git status`; read them with Read.
3. **Walk the checklist.** For each of the seven points in
   [checklist.md](checklist.md), do the listed checks and record exactly one result:
   - `PASS`: the evidence shows the point is satisfied.
   - `FAIL`: the evidence shows a problem. Add a finding.
   - `NOT VERIFIED`: you could not check it. Say what is needed to check it.
4. **Run the tests** for point 3 (ask permission if prompted):
   `python3 -m unittest discover -s tests -q` and, if `dashboard/` changed and node
   exists, `node --test "dashboard/tests/*.mjs"`. Quote the final summary lines verbatim.
5. **Security (point 4).** Check the diff against the security checklist. If the
   `security-reviewer` subagent is available, delegate to it with the list of
   changed files and merge its findings. Otherwise use the
   `/security-review` skill from this pack or review inline.
6. **Runtime (point 5).** Use browser or CLI evidence from this session, or from
   `/browser-verification`. Without it, the result is `NOT VERIFIED`, never `PASS`.
7. **Decide the verdict:**
   - `READY TO MERGE`: all seven PASS.
   - `CHANGES REQUESTED`: any FAIL with severity Medium or lower, or any NOT VERIFIED.
   - `BLOCKED`: any FAIL with severity High or Critical, or out-of-scope edits to
     protected areas.
8. **Report** using the format below. Then stop. Do not fix anything unless the
   user asks you to after reading the review.

## Output format

```markdown
# Change Review: <one-line summary of the change>

**Verdict:** READY TO MERGE | CHANGES REQUESTED | BLOCKED
**Scope source:** <brief path / issue / conversation>
**Diff:** <N files changed, +X / -Y> (from `git diff --stat`)

| # | Check    | Result | Evidence |
|---|----------|--------|----------|
| 1 | Scope    | PASS   | Only `notes_api/service.py`, `tests/test_partial_update.py` changed; both in scope |
| 2 | Diff     | ...    | ... |
| 3 | Tests    | ...    | `python3 -m unittest discover -s tests -q` -> `Ran 24 tests ... OK` |
| 4 | Security | ...    | ... |
| 5 | Runtime  | ...    | ... |
| 6 | Rollback | ...    | ... |
| 7 | Handoff  | ...    | ... |

## Findings
1. **[High]** `path/file.py:42`: <problem>. Evidence: `<quoted line or output>`.
   Fix: <specific change>.
2. ...

## Not verified
- <point>: <what is missing and how to verify it>

## Commands run
    $ <command>
    <relevant output, verbatim, trimmed with "..." only in the middle>
```

## Rules

- Read-only. Do not edit files, stage, commit, push, merge, or rebase.
- Never write an output you did not see. If a command was not run, say so.
- Do not mark Runtime PASS from unit tests alone.
- Explain every material diff line you flag; do not summarize what you didn't read.
- Severity scale: Critical, High, Medium, Low (defined in [checklist.md](checklist.md)).

## Project-specific rules (customize this section)

Replace these with your project's rules during Part 9:
- Protected files: `<e.g. data/*.json formats, dashboard element IDs used by tests>`
- Required test commands: `python3 -m unittest discover -s tests -q`,
  `node --test "dashboard/tests/*.mjs"`
- Extra checks: `<e.g. README usage examples updated when CLI flags change>`

## Worked example (Shipyard)

After fixing the seeded Notes API defect, the user runs `/change-review`.
Claude runs `git diff --stat` (`2 files changed, 19 insertions(+), 3 deletions(-)`),
reads both hunks, and runs the suite. Output line: `Ran 18 tests in 0.041s` / `OK`.
The change is API-only, so Runtime cites the `curl -s localhost:8000/notes?tag=release`
response captured earlier in the session. The fix is uncommitted on `main`, so
Rollback is `FAIL` (Medium). Verdict: **CHANGES REQUESTED**, with the fix "move the
work to a branch and commit before merging".
