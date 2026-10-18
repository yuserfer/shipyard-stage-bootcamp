# Diagnosis record: BUG-101

## 1. Reproduce
Failing regression test written first, against the unfixed code:
```
$ python3 -m unittest tests.test_partial_update -q
FAIL: test_title_only_patch_keeps_body
AssertionError: '' != 'Rollback plan: redeploy v1.3'
Ran 5 tests … FAILED (failures=1)
```

## 2. Likely cause
`NoteService.update` merges the title correctly (`if "title" in data else current["title"]`) but not the body:
`body = _body(data.get("body"))` → a missing key becomes `None` → `_body(None)` returns `""` → the repository writes an empty body. The existing suite never sent a partial PATCH, so it stayed green.

## 3. Bounded fix
One line in `notes_api/service.py`, mirroring the title rule:
`body = _body(data["body"]) if "body" in data else current["body"]`.
No change to the repository, the HTTP layer or the schema.

## 4. Evidence
```
$ python3 -m unittest discover -s tests -q
Ran 32 tests … OK
```
`test_title_only_patch_keeps_body` fails before the fix and passes after. `test_explicit_empty_body_is_allowed` proves we did not over-correct.

## 5. Checkpoint exercise (planned unsuccessful attempt)
The lab deliberately tries a heavier approach first: "make `NoteRepository.update` accept optional columns". It widens the change beyond the bug and touches the repository, service and tests. Instead of patching forward, use `/rewind` → **Restore code** to return to the checkpoint before that prompt (the conversation is kept), then apply the one-line service fix. Note: `/rewind` restores edits made with Claude's file tools, not changes made through Bash commands.
