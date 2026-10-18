# Review Before Merge Checklist

> **How to use.** Complete this checklist before you merge any change made by Claude Code. Do not merge until every row has a status of Pass or N/A, plus concrete evidence: a command and its raw output, a file and line, a screenshot path, or a commit hash. Statements like "Claude said tests pass" or "looks fine" do not count as evidence. N/A needs a one-line reason. The engineer of record signs at the bottom. The `change-review` Skill applies the same seven points automatically, but its output is input to this checklist, not a replacement for it.

---

| Field | Value |
|---|---|
| Change / branch | `__________` |
| Brief or issue | `__________` |
| Engineer of record | `__________` |
| Date | `__________` |

| # | Check | Question | Status (Pass / Fail / N/A) | Evidence |
|---|---|---|---|---|
| 1 | Scope | Did the change stay within the approved files and acceptance criteria? | | |
| 2 | Diff | Can I explain every material line that changed? | | |
| 3 | Tests | Do the relevant tests pass, including new edge cases? | | |
| 4 | Security | Were secrets, dependencies, permissions, and unsafe inputs checked? | | |
| 5 | Runtime | Was the feature verified in the real interface? | | |
| 6 | Rollback | Is there a clean checkpoint, branch, or commit to return to? | | |
| 7 | Handoff | Are risks, documentation, ownership, and next steps clear? | | |

**Decision:** merge / fix first / reject

**Signed (engineer of record):** `__________`

### Useful evidence commands
- Scope: `git diff --stat main...HEAD`, then compare the file list with the brief.
- Diff: `git diff main...HEAD`. Annotate any line you cannot explain and resolve it before merging.
- Tests: `python3 -m unittest discover -s tests -v; echo "exit=$?"`.
- Security: `git diff main...HEAD | grep -inE "api[_-]?key|token|secret|password"`, plus a check of any new imports and the input handling paths.
- Runtime: a `curl` transcript for API changes, or Claude in Chrome or manual browser evidence for UI changes.
- Rollback: `git log --oneline -5` and `git status`.

---

## Example: Shipyard, Project 5 (BUG-101: PATCH with only a title wipes the body)

| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | Scope | Pass | `git diff --stat main...fix/bug-101` shows `notes_api/service.py` (+2 -1) and `tests/test_partial_update.py` (new). Both are in the brief. No other files changed. |
| 2 | Diff | Pass | `service.update` now falls back to `current["body"]` when `"body"` is not in the request. I can explain all 3 changed lines. The new test file covers five cases. |
| 3 | Tests | Pass | `python3 -m unittest discover -s tests -v`: `Ran 32 tests in 1.457s` / `OK`, `exit=0`. The regression test `test_title_only_patch_keeps_body` failed on `main` with `AssertionError: '' != 'Rollback plan: redeploy v1.3'` (output saved in `evidence/bug-101-red.txt`). |
| 4 | Security | Pass | No new imports or dependencies. `_body()` validation is unchanged and still enforces type and length. The grep for secrets in the diff returned nothing. |
| 5 | Runtime | Pass | `curl -s -X PATCH localhost:8000/api/notes/1 -H 'Content-Type: application/json' -d '{"title":"Release v1.4.1"}'` returned body `"Rollback plan: redeploy v1.3"` (saved in `evidence/bug-101-curl.txt`). |
| 6 | Rollback | Pass | Branch `fix/bug-101` with one commit, `a91d0e2`. `main` is untouched at `7c4b2f0`. `git status` is clean. |
| 7 | Handoff | Pass | The diagnosis record is in `docs/diagnosis-bug-101.md`. Known gap: there is no test for PATCH with unknown fields; it is logged as a follow-up for the backend owner. |

**Decision:** merge. **Signed:** Dana Ruiz.
