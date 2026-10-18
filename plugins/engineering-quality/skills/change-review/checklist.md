# Review Before Merge Checklist

The seven points, verbatim from the workshop:

1. **Scope:** Did the change stay within the approved files and acceptance criteria?
2. **Diff:** Can I explain every material line that changed?
3. **Tests:** Do the relevant tests pass, including new edge cases?
4. **Security:** Were secrets, dependencies, permissions, and unsafe inputs checked?
5. **Runtime:** Was the feature verified in the real interface?
6. **Rollback:** Is there a clean checkpoint, branch, or commit to return to?
7. **Handoff:** Are risks, documentation, ownership, and next steps clear?

Each point gets exactly one result: `PASS`, `FAIL`, or `NOT VERIFIED`.

---

## 1. Scope

Checks:
- Compare `git status --short` and `git diff --stat` with the files the brief allowed.
- Map each acceptance criterion to the diff hunk that implements it.
- Look for protected-area edits (CLAUDE.md "do not touch" list, data formats, CI config).
- Look for drive-by changes: reformatting, renames, unrelated refactors.

Evidence: file list from `git diff --stat`; AC-to-hunk mapping.
FAIL if: an unapproved file changed, a protected area changed, or an AC has no implementation.

## 2. Diff

Checks:
- Read every hunk. For each material change, write one line explaining it.
- Flag dead code, debug prints, commented-out blocks, TODOs added without an owner.
- Flag changed behaviour not covered by the brief (error messages, defaults, exit codes).

Evidence: `path:line` references with a one-line explanation each.
FAIL if: a material line can't be explained or contradicts the brief.

## 3. Tests

Checks:
- Run `python3 -m unittest discover -s tests -q` (Python changes).
- Run `node --test dashboard/tests/` (dashboard changes, if node exists).
- Confirm new tests exist for new behaviour and edge cases (empty input, missing
  record, invalid type, boundary values).
- Confirm no test was deleted, skipped (`@unittest.skip`, `test.skip`), or weakened
  (looser assertion, changed expected value) without a stated reason.

Evidence: the command and its final summary lines, verbatim.
FAIL if: any test fails, or behaviour changed without a test.
NOT VERIFIED if: tests could not be run (say why).

## 4. Security

Checks (details in the security-review skill's checklist):
- Secrets: no keys, tokens, passwords, or `.env` content added to code, tests, or logs.
- Dependencies: any new import or package is necessary, pinned, and from a known source.
- Permissions: no widened file modes, permission rules, or hook bypasses.
- Unsafe inputs: user input is validated before storage, file paths, shell, or HTML.

Evidence: findings with `path:line`, or "checked X, Y, Z; no issues" listing what was checked.
FAIL if: any High/Critical security finding.

## 5. Runtime

Checks:
- CLI: run the real command and quote output (e.g. `python3 shipctl.py list --owner alice`).
- API: start the server and quote a real request/response.
- UI: browser evidence (screenshot path, console output) from `/browser-verification`.

Evidence: the command or browser action plus observed result.
NOT VERIFIED if: only unit tests ran. Unit tests alone never earn a PASS here.

## 6. Rollback

Checks:
- `git log --oneline -5`: is there a commit from before the change?
- Is the work on a feature branch or worktree, not directly on `main`?
- Are uncommitted changes small enough to discard safely? (Note: `/rewind` does not
  undo Bash-made file changes.)

Evidence: branch name and the commit SHA to return to.
FAIL if: the change sits uncommitted on `main` mixed with unrelated work.

## 7. Handoff

Checks:
- README or docs updated if usage, flags, endpoints, or setup changed.
- Known risks and limitations written down.
- Owner named for follow-ups; next step stated.

Evidence: doc paths changed, or the handoff note text.
FAIL if: user-visible behaviour changed and docs did not.

---

## Severity scale

| Severity | Meaning | Merge impact |
|----------|---------|--------------|
| Critical | Data loss, credential exposure, remote code execution, auth bypass | Blocks merge |
| High | Wrong results for normal use, unvalidated input reaching storage/shell/HTML, failing tests | Blocks merge |
| Medium | Edge-case bug, missing test for new behaviour, docs out of date | Fix before or right after merge, with an owner |
| Low | Style, naming, minor clarity | Optional |
