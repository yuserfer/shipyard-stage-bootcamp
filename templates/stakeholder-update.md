# Stakeholder Update (One Page)

> **How to use.** Write this from the Production Readiness Report and the maintainer handoff, never from memory. In Cowork, give it both files and this template and ask for a one-page update. Without Cowork, use the `stakeholder-update` Skill in Claude Code, or fill the template yourself. Then check the draft line by line against the source reports. Every risk, fix, owner, and date must trace back to them, and nothing may be softened or invented. Translate technical findings into business impact; leave implementation detail in the report. The page has exactly the eight fields below.

---

**Project / release:** `__________`  **Date:** `__________`  **Prepared by:** `__________`  **Sources:** `__________`

### 1. Current release status
`On track / At risk / Blocked`. One sentence explaining why.

### 2. Features completed
- `__________`

### 3. Customer or business impact
What users and the business gain, and what they could lose.

### 4. Major risks
| Risk (plain language) | Likelihood | Impact | Mitigation |
|---|---|---|---|
| | | | |

### 5. Decisions required
| Decision | Options | Recommended | Needed by |
|---|---|---|---|
| | | | |

### 6. Top three fixes
1. `__________`
2. `__________`
3. `__________`

### 7. Owners and deadlines
| Action | Owner | Deadline |
|---|---|---|
| | | |

### 8. Recommended next step
`__________`

---

## Example: Shipyard v1.0 internal pilot

**Project:** Shipyard v1.0 internal pilot. **Date:** 2026-10-14. **Prepared by:** Dana Ruiz. **Sources:** Production Readiness Report (Notes API, `e41b7d2`) and the dashboard maintainer handoff.

**1. Status: At risk (conditional go).** The features are complete and tested. Three small security fixes are needed before the pilot can run beyond a single laptop.

**2. Features completed.**
- `shipctl` release task CLI: owners, due dates, filters.
- Notes API with search and tags.
- Release dashboard with release notes.
- Automated quality checks packaged as a reusable plugin.

**3. Business impact.** Release managers get one place to track release tasks and notes, which replaces a shared spreadsheet. If the security fixes are skipped, anyone on the office network could alter or delete release notes before a release.

**4. Major risks.**

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Unauthorized edits to release notes on a shared network | Medium | High | Restrict to the local machine until fixes land |
| Internal error details shown to users | Medium | Medium | Fix 2 below |
| Dashboard hard to use on phones | High | Low | Desktop use only for the pilot |

**5. Decisions required.**

| Decision | Options | Recommended | Needed by |
|---|---|---|---|
| Pilot scope | Single laptop now / wait for fixes / wait for login | Single laptop now; widen after the fixes | 2026-10-15 |
| Authentication | Build now / defer past the pilot | Defer; revisit before any shared deployment | 2026-10-24 |

**6. Top three fixes.**
1. Limit the service to the local machine by default.
2. Hide internal error details from users.
3. Reject oversized requests.

**7. Owners and deadlines.**

| Action | Owner | Deadline |
|---|---|---|
| Fixes 1 to 3 merged and verified | Sam Okafor | 2026-10-17 |
| Confirm pilot scope | Priya Shah (Release Manager) | 2026-10-15 |
| Authentication options paper | Dana Ruiz | 2026-10-24 |

**8. Next step.** Approve the single-laptop pilot today. We will confirm on 2026-10-17 that the fixes are verified, and then propose widening access.
