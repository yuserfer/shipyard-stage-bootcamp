# Team brief: release notes for the dashboard (Agent Team sprint)

## Outcome
The dashboard shows the release notes for v1.4, grouped into sections, and anyone can copy them as Markdown for the release announcement.

## Behaviour
- Notes tagged `release:<version>` belong to that release.
- Sections, in this order, by the first matching tag: `backend` → Backend, `dashboard` → Dashboard, `ops` → Operations, `qa` → Quality, `decision` → Decisions; anything else → Other changes. A note appears once.
- `GET /api/releases/<version>/notes` → `{version, count, sections:[{key, title, notes}]}`; `?format=markdown` → `text/markdown` changelog using the first body line. Invalid version (not `v<major>.<minor>[.<patch>]`) → `400`.
- Dashboard panel "Release notes v1.4" between the tasks and the engineering notes, with a "Copy as Markdown" button. Escape every API value.

## Team (lead + three teammates)
| Role | Owns (only these files) | Done when |
|---|---|---|
| Backend owner | `notes_api/releases.py` (new), route in `notes_api/server.py` | endpoint returns the contract above |
| Frontend owner | `dashboard/index.html`, `dashboard/styles.css`, `dashboard/js/release-notes.js` (new), `dashboard/js/main.js` | panel renders and copies Markdown |
| Test & verification owner | `tests/test_release_notes.py`, `dashboard/tests/release-notes.test.mjs`, browser check | all suites green, browser evidence at 1280/390 px |

## Rules
- Teammates plan first, read-only. Note: Claude Code auto-approves a teammate's plan in the lead session without review, so the lead and the human read each plan and message any teammate whose plan strays outside its ownership.
- The API contract above is frozen; frontend and tests build against it in parallel.
- Quality gate before acceptance: full test suites, `/engineering-quality:change-review`, browser check.
- No commits by teammates. The lead summarises; the human accepts.

## Enable (instructor machine)
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (experimental, off by default). Display mode: in-process (default) or `--teammate-mode tmux`.
