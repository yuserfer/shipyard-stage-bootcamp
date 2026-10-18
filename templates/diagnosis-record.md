# Diagnosis Record

> **How to use.** Open a record when a defect is reported and before anyone edits code. Ask Claude to investigate first: "Reproduce and explain; do not edit files yet." Fill the sections in order. Each section needs raw evidence (a command and its output), not a summary. The failing regression test is the contract: the fix is done when that test passes and nothing else breaks. The `test-debug-loop` Skill follows the same sequence.

---

| Field | Value |
|---|---|
| Bug ID / title | `__________` |
| Reported by / date | `__________` |
| Engineer of record | `__________` |
| Recovery point before investigation | `__________` (commit hash or branch) |

## 1. Reproduce
Steps, the exact command, expected result, actual result.

```text
$ <command>
<raw output>
```

## 2. Likely cause
| Field | Entry |
|---|---|
| Hypothesis | `__________` |
| Location (file, function) | `__________` |
| Evidence supporting it | `__________` |
| Confidence (low / medium / high) and what would disprove it | `__________` |

## 3. Failing regression test
| Field | Entry |
|---|---|
| Test file and name | `__________` |
| Red run (fails on unfixed code) | command and raw output below |

```text
$ <test command>
<raw output showing FAIL>
```

## 4. Bounded fix
| Field | Entry |
|---|---|
| Files allowed to change | `__________` |
| Change summary (what and why) | `__________` |
| Rejected attempt and how it was undone | `__________` |

## 5. Evidence
| Check | Command | Result (raw) |
|---|---|---|
| Regression test passes | | |
| Full relevant suite passes | | |
| Runtime reproduction now behaves correctly | | |
| `/goal` condition met (if used) | | |

Next step: complete the Review Before Merge checklist.

---

## Example: Shipyard, Project 5 (BUG-101)

**Bug.** BUG-101: a PATCH that sends only a title wipes the note body. Reported by the release team on 2026-10-14. Engineer of record: Dana Ruiz. Recovery point: `main` at `7c4b2f0`; the work happens on branch `fix/bug-101`.

**1. Reproduce.** Expected: the body is unchanged. Actual: the body is empty.

```text
$ curl -s -X POST localhost:8000/api/notes -H 'Content-Type: application/json' \
    -d '{"title":"Release v1.4","body":"Rollback plan: redeploy v1.3"}'
{"id": 1, "title": "Release v1.4", "body": "Rollback plan: redeploy v1.3", ...}
$ curl -s -X PATCH localhost:8000/api/notes/1 -H 'Content-Type: application/json' \
    -d '{"title":"Release v1.4.1"}'
{"id": 1, "title": "Release v1.4.1", "body": "", ...}
```

**2. Likely cause.**
- Hypothesis: `NoteService.update` calls `_body(data.get("body"))` unconditionally. A missing key becomes `None`, which is normalized to `""`.
- Location: `notes_api/service.py`, `NoteService.update`.
- Evidence: the repository layer writes exactly what the service passes, and a direct `repo.update(1, "t", "x")` keeps the body.
- Confidence: high. A failing service-level test would confirm it. If only the HTTP test failed, the cause would be in `server.py` instead.

**3. Failing regression test.** `tests/test_partial_update.py::PartialUpdateTests.test_title_only_patch_keeps_body`

```text
$ python3 -m unittest tests.test_partial_update -v
test_title_only_patch_keeps_body (...) ... FAIL
AssertionError: '' != 'Rollback plan: redeploy v1.3'
Ran 5 tests in 0.006s
FAILED (failures=1)
```

**4. Bounded fix.**
- Files allowed: `notes_api/service.py` and `tests/test_partial_update.py`.
- Change: the body is now read only when `"body" in data`; otherwise the code uses `current["body"]`. The title follows the same pattern.
- Rejected attempt: the first try made the repository use `COALESCE` with NULL. That leaked a business rule into the SQL layer and broke `test_explicit_empty_body_is_allowed`. It was undone with `/rewind` and **Restore code** to the checkpoint before that prompt, keeping the conversation. Afterwards `git status` was clean apart from the new test file.

**5. Evidence.**

| Check | Command | Result |
|---|---|---|
| Regression test | `python3 -m unittest tests.test_partial_update -v` | `Ran 5 tests ... OK` |
| Full suite | `python3 -m unittest discover -s tests -v; echo "exit=$?"` | `Ran 32 tests in 1.457s` / `OK` / `exit=0` |
| Runtime | The same PATCH `curl` as in step 1 | `"body": "Rollback plan: redeploy v1.3"` |
| `/goal` | `/goal python3 -m unittest discover -s tests exits 0 and test_title_only_patch_keeps_body is reported ok` | met after 3 turns |
