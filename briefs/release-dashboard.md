# Engineering brief: release dashboard from a wireframe

## Input
`wireframes/release-dashboard.png` (hand-drawn). Treat the annotations as requirements.

## Outcome
A release manager opens one page and knows, in ten seconds, whether v1.4 is on track.

## Scope
- Header with release name and target-date badge.
- Four KPI cards: open tasks, completed, overdue (pending with a past due date, shown in red), notes.
- Release tasks table from `GET /api/tasks` with owner and status filters (combine with AND, default *pending*), overdue due dates in red, empty-state message.
- Engineering notes from `GET /api/notes`: search box (title + body), tag chips (click to filter, click again to clear).
- Responsive: under 760 px, KPI cards become 2×2, filters stack, table rows become stacked cards.

## Constraints
- Plain HTML, CSS and JavaScript ES modules in `dashboard/`. No frameworks, no build step, no CDN.
- The existing Python server serves `dashboard/` at `/` and adds a read-only `GET /api/tasks` that reads shipctl's `tasks.json` (`SHIPCTL_DB` respected).
- Escape every value that comes from the API before inserting it into HTML.
- Pure logic (filters, KPIs, overdue rule) must be testable with `node --test`.

## Verification (Claude in Chrome)
1. `python3 seed.py && python3 -m notes_api.server` then open `http://localhost:8000/`.
2. Exercise: owner filter, status filter, combined filters, search, tag toggle on/off.
3. Read the console: zero errors.
4. Resize to 390 px wide: check the 2×2 cards and stacked rows.
5. Record every issue in `docs/browser-issue-log.md` with before/after status, then fix and re-verify.

Fallback without Chrome: use `templates/browser-verification-checklist.md` and the captured evidence in `evidence/`.
