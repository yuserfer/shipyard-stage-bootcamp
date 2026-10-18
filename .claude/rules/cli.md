---
paths:
  - "shipctl.py"
---

# shipctl CLI rules

- New commands: add a `cmd_<name>(args) -> str` handler and register it in `build_parser()`.
- Handlers return the text to print; `main()` prints it and maps exceptions to exit codes.
- Raise `UserError` for bad input (exit 1); let `OSError` surface for storage problems (exit 2).
- Output must stay stable and greppable: one record per line, no colour codes.
- Update the command table in `README.md` in the same change.
