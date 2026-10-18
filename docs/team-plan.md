# Parallel task plan: release notes (v1.4)

| ID | Task | Owner | Depends on | Files |
|---|---|---|---|---|
| T1 | Freeze the JSON + Markdown contract (copy from the brief into the task description) | Lead | – | – |
| T2 | `build_release_notes` + `to_markdown` in `notes_api/releases.py` | Backend | T1 | `notes_api/releases.py` |
| T3 | `GET /api/releases/<v>/notes` route, `?format=markdown`, `400` on bad version | Backend | T2 | `notes_api/server.py` |
| T4 | Panel markup + styles | Frontend | T1 | `dashboard/index.html`, `dashboard/styles.css` |
| T5 | `release-notes.js` (`releaseNotesHtml`, `mountReleaseNotes`) + wire into `main.js` | Frontend | T1 | `dashboard/js/release-notes.js`, `dashboard/js/main.js` |
| T6 | Python tests: grouping order, exclusivity, Markdown, HTTP, invalid version | Test | T1 | `tests/test_release_notes.py` |
| T7 | Node tests for `releaseNotesHtml` (sections, escaping, empty) | Test | T1 | `dashboard/tests/release-notes.test.mjs` |
| T8 | Integration: full suites + browser check 1280/390 px + change review | Test + Lead | T3, T5, T6, T7 | `evidence/` |

File ownership is disjoint, so teammates never edit the same file. The only shared surface is the contract in T1.

## Coordination risks
| Risk | Mitigation |
|---|---|
| Frontend builds against a different response shape | Contract frozen in T1; T6 asserts the exact shape |
| Two teammates edit `main.js` / `server.py` | Ownership in each spawn prompt; plans are auto-approved, so the lead and the human read them and steer by message; per-file diff review |
| Teammate reports "done" without evidence | `TaskCompleted` quality gate: task closes only with test output |
| Token cost grows with each teammate | Three teammates max; Sonnet for teammates; stop idle teammates |
| Task status lags behind reality | Lead checks the task list and messages the teammate directly |
