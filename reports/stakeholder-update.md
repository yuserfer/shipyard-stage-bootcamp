# Shipyard v1.4: Stakeholder Update

## Current release status
**Conditional go** for the internal rollout, only after fixes 1–3 below are merged and their verification tests pass. **No-go** for anything internet-facing until authentication is reviewed again. Tests are green (Python: 54 passed; dashboard: 10 passed).

## Features completed
- Notes API and dashboard, with the `shipctl.py` command-line tool, are built, layered and fully tested.
- Security review done: the database is queried safely, search wildcards are handled, and file serving cannot be tricked into leaking other files. No secrets are in the repository.
- Maintainer handoff guide written.
- Release-notes panel for v1.4 is built and tested: the API route, dashboard panel and tests are in the repository, and the test suites pass. The final integration and browser check (task T8 in `docs/team-plan.md`) is not confirmed.

## Customer or business impact
- Users are internal engineers on a shared VM. The issues below affect the whole engineering org, not external customers.
- Until fixed, one colleague's note could run code in everyone's browser, and anyone on the network can edit or delete notes.
- Release managers see readiness in one page instead of chasing three tools.
- Release notes are generated from the same notes engineers already write, so there is less manual work on release day.
- Fixes are estimated at about a day of work (reviewers' estimate, not a commitment).

## Major risks
| Severity | In plain language |
|---|---|
| **High** | A note containing markup can run script in other people's browsers. |
| **High** | No login. Anyone who can reach the server can edit or delete notes, and any web page can call it. |
| **Medium** | One oversized request can tie up the server. |
| Low | Error messages show internal details to users. |
| Low | Failures are not logged by default, so problems are hard to spot. |

Not verified, so not blocking: database slowdown under many simultaneous writers (load test not yet run) and slow task loading at thousands of tasks.

## Decisions required
1. Approve the conditional go: ship internally only after fixes 1–3 are merged. *Owner: VP Engineering.*
2. Confirm that internet-facing use stays no-go until authentication is re-reviewed. *Owner: Product lead.*
3. Confirm the approach for fix 2: server listens locally by default, with a token required for any change. *Owner: not assigned.*

## Top three fixes
1. **Escape note text before display** (High, small). Verified by a new test and a browser check.
2. **Local-only by default, remove open cross-site access, require a token for changes** (High, medium). Verified by tests: a write without a token is rejected; the probe script shows the new defaults.
3. **Reject requests over 64 KiB** (Medium, small). Verified by a test: a 70 KiB body is rejected in under a second.

## Owners and deadlines
| Item | Owner | Deadline |
|---|---|---|
| Fix 1 | Frontend owner | Not set |
| Fixes 2 and 3 | Backend owner | Not set |
| Re-review and merge approval | Engineer of record | Not set |
| Load test on Notes API | QA | Not set |

No dates appear in the source documents. They need to be set.

## Recommended next step
Set deadlines with the three owners, merge fixes 1–3, then have the engineer of record run the re-review. Roll out internally only once that passes.
