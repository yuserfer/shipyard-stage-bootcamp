# Shipyard v1.4: release update

**Status: Conditional go** for the internal rollout, after three fixes (about one engineering day). Not for external use yet.

**Completed for v1.4**
- Release task tracking (`shipctl`) with owners, due dates and per-owner status.
- Notes API with search and tags; one data-loss bug (BUG-101) found and fixed with a regression test.
- Release dashboard: KPIs, filters, notes, and generated release notes with one-click Markdown copy.
- Engineering Quality plugin: automatic tests after every edit, unsafe commands blocked, standard review checklist.

**Business impact**
- Release managers see readiness in one page instead of chasing three tools.
- Release notes are generated from the same notes engineers already write: less manual work on release day.

**Major risks (plain language)**
1. A note containing hidden script could run in every colleague's browser (High).
2. Anyone on the network can edit or delete notes; there is no login (High).
3. One malformed request can slow the service for everyone (Medium).

**Decisions required**
- Approve one engineering day to fix the three risks before rollout. *Owner: VP Engineering.*
- Confirm the rollout stays internal-only until a login is reviewed. *Owner: Product lead.*

**Top three fixes and owners**
| Fix | Owner | Deadline |
|---|---|---|
| Escape note content in the dashboard | Frontend owner | set at approval (T + 1 day) |
| Localhost by default + token for changes | Backend owner | set at approval (T + 1 day) |
| Reject oversized requests | Backend owner | set at approval (T + 1 day) |

**Recommended next step**
Approve the fix day today; we re-run the production review and send a final go/no-go the next morning.

_Source: `reports/production-readiness.md` (evidence for every risk), `docs/HANDOFF.md`._
