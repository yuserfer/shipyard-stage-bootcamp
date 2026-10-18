# Review Before Merge: BUG-101

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | **Scope:** stayed within approved files and acceptance criteria? | Yes | `git diff --stat`: `notes_api/service.py` (1 line), `tests/test_partial_update.py` (new) |
| 2 | **Diff:** can I explain every material line? | Yes | The body now uses the same "keep current unless provided" rule as the title |
| 3 | **Tests:** relevant tests pass, including new edge cases? | Yes | `Ran 32 tests … OK`; new cases: title-only, body-only, explicit empty body, empty patch, `updated_at` moves |
| 4 | **Security:** secrets, dependencies, permissions, unsafe inputs checked? | Yes | No new inputs, dependencies or permissions; validation path unchanged |
| 5 | **Runtime:** verified in the real interface? | Yes | `curl` reproduction from the bug report now returns the original body |
| 6 | **Rollback:** clean checkpoint, branch or commit to return to? | Yes | Branch `fix/bug-101`; baseline commit `start of part 05` |
| 7 | **Handoff:** risks, docs, ownership, next steps clear? | Yes | Diagnosis record in `docs/`; follow-up: add a PATCH contract test for every new field (owner: backend) |

Decision: ready for the engineer of record to merge.
