# Refactor request: maintainer-ready dashboard

The dashboard works, but `dashboard/app.js` mixes pure rules, HTTP calls, DOM rendering and event wiring in one file. A new maintainer joins next week.

1. Propose a bounded refactoring plan first (files, responsibilities, what will NOT change). Wait for approval.
2. Preserve behaviour exactly: same HTML ids, same API calls, same rendering. Existing tests are the guardrail and must pass unchanged in substance (only import paths may change).
3. Re-run the browser check at 1280 px and 390 px and compare with the evidence from Project 7.
4. Write `docs/ARCHITECTURE.md` (one page) and `docs/HANDOFF.md` (onboarding, known limitations, next steps). Update `README.md`.
5. Do not change the Python API, `seed.py`, `SAFETY.md`, `.claude/` or `briefs/`. Do not commit.
