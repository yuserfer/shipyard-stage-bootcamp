# Browser verification log: release dashboard (reference checkpoint)

Environment: headless Chromium (Playwright), desktop 1280×900 and mobile 390×844, data from `python3 seed.py`.
This is the verification of the reference checkpoint. The browser check of the recorded Claude Code run is in the bootcamp repository: `parts/07-dashboard-wireframe/evidence/recorded-run-issues.md`.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Page loads, all four KPI cards populated (6 open, 2 done, 2 overdue, 5 notes) | Pass | `evidence/dashboard-desktop-1280.png` |
| 2 | Overdue due dates rendered in red | Pass | Rows "Rotate staging credentials", "Run load test" in the desktop screenshot |
| 3 | Browser console | Pass: no messages at either width | Playwright console capture: `[]` |
| 4 | Mobile 390 px: KPI cards 2×2, filters stacked, rows as cards | Pass | `evidence/dashboard-mobile-390.png` |
| 5 | Owner/status filters combine; tag chip toggles on and off; search hits title + body | Logic: pass · interaction: verify live | the dashboard logic tests (`node --test "dashboard/tests/*.mjs"`); the click-through is the Claude in Chrome step of the lab |
| 6 | API values are escaped before insertion into HTML | Partial: titles and tags escaped; note body passes through `formatBody` unescaped | Logged as a follow-up for the security review (Project 10A) |

Issue template for your own run (copy a row per issue):

| # | Flow | Issue | Evidence (console line / screenshot) | Fix | Status after re-check |
|---|---|---|---|---|---|
