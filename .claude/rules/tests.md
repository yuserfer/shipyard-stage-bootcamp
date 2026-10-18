---
paths:
  - "tests/**/*.py"
---

# Test conventions

- One `unittest.TestCase` class per behaviour or acceptance criterion; name it `<Behaviour>Tests`.
- Test names read as sentences: `test_<what>_<expected>` (for example `test_empty_title_is_rejected`).
- Never touch the real `tasks.json`: point `SHIPCTL_DB` at a `tempfile.TemporaryDirectory()` in `setUp`.
- Assert on exit codes and on the exact user-facing message, not only on truthiness.
- No sleeps, no network, no ordering dependencies between tests.
