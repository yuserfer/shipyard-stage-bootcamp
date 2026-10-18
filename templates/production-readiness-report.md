# Production Readiness Report

> **How to use.** Fill this in after a structured production review: a security review, a code review, and runtime checks. All seven required sections must be present; the capstone treats a missing section as a failed gate. Severity-rank the findings, and tie every significant finding to evidence under the evidence rule below. Anything Claude or a reviewer suspects but has not shown goes under "Speculative concerns", not into the ranked findings. Keep the report to one or two pages. The `release-readiness` Skill drafts this structure; you verify it and sign it.

## Severity scale

| Severity | Definition | Release impact |
|---|---|---|
| **Critical** | Exploitable now, or causes data loss or corruption, credential exposure, or a full outage on the main path | No-go until fixed |
| **High** | Likely to cause a security weakness, incorrect data, or an outage of an important feature under realistic use | No-go, or conditional go with a dated fix and mitigation |
| **Medium** | Degrades reliability, security posture, or maintainability; has a workaround or limited exposure | Fix in the next iteration; may ship |
| **Low** | Minor defect, polish, or hardening opportunity | Backlog |
| **Info** | An observation with no current risk | None |

## Evidence rule

Every finding rated **Medium or above** must cite at least one piece of verifiable evidence:
- **Code**: file plus function, or a line at a named commit.
- **Configuration**: file and key.
- **Test**: the command and raw output, or a failing test name.
- **Runtime**: the exact request or step and the observed response, or a screenshot path.

"Claude reported..." is not evidence; the artifact Claude pointed at is. A finding without evidence is either verified by you or moved to Speculative concerns. Speculative items cannot be the sole basis for a no-go, but each one needs a verification action.

---

| Field | Value |
|---|---|
| Project / release | `__________` |
| Commit reviewed | `__________` |
| Reviewer (engineer of record) | `__________` |
| Tools used | `__________` (e.g. `/security-review`, `/code-review high`, security-reviewer subagent, tests, browser checks) |
| Date | `__________` |

## 1. Concise risk summary
Three to five sentences: what was reviewed, the overall risk level, and the single most important issue.

`__________`

## 2. Severity-ranked findings

| ID | Severity | Finding | Area | Evidence ref | Effort (S/M/L) | Business impact |
|---|---|---|---|---|---|---|
| F1 | | | | E1 | | |

**Speculative concerns (not verified):**

| ID | Concern | Why it is unverified | Verification action |
|---|---|---|---|
| S1 | | | |

## 3. Evidence for each significant finding

| Ref | Type (code / config / test / runtime) | Exact evidence |
|---|---|---|
| E1 | | |

## 4. Top three fixes
Order by severity, then by effort and business impact.

| # | Fix | Addresses | Effort |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## 5. Recommended next-step owner
Name: `__________` / Role: `__________` / Due: `__________`

## 6. Verification action
How we will prove the top fixes worked: commands, tests, and runtime checks.

`__________`

## 7. Recommendation
**Go / Conditional go / No-go:** `__________`

Conditions (for a conditional go): `__________`

---

## Example: Shipyard Notes API v1.0 (internal pilot)

| Field | Value |
|---|---|
| Release | Notes API v1.0 for an internal pilot with the release team |
| Commit reviewed | `e41b7d2` |
| Reviewer | Dana Ruiz |
| Tools used | `/security-review`, `/code-review high`, `engineering-quality:security-reviewer` subagent, full test suite, manual `curl` checks |
| Date | 2026-10-14 |

**1. Risk summary.** We reviewed the Notes API (server, service, and repository) and its tests. The core CRUD paths are correct and well tested; 23 tests pass, and the BUG-101 regression is covered. The main risk is exposure: the server binds to all interfaces with no authentication and returns internal exception details on errors. Overall risk for an internal, localhost-only pilot is **Medium**. On a shared network it would be **High**.

**2. Findings.**

| ID | Severity | Finding | Area | Evidence | Effort | Business impact |
|---|---|---|---|---|---|---|
| F1 | High | The default bind address is `0.0.0.0` and there is no authentication, so anyone on the network can create, edit, or delete notes | Security / deployment | E1, E2 | S | Release notes could be altered or deleted by anyone on the office Wi-Fi |
| F2 | Medium | The 500 handler returns `repr(exc)` to the client, leaking internal details | Error handling | E3 | S | Gives attackers internals; confuses users |
| F3 | Medium | The request body is read using the client-supplied `Content-Length` with no size cap | Input validation | E4 | S | A single large request can exhaust memory |
| F4 | Low | `Access-Control-Allow-Origin: *` on all responses | Security | E5 | S | Any web page can call the API from a browser on the same network |

| ID | Concern | Why unverified | Verification action |
|---|---|---|---|
| S1 | SQL injection in search | The repository uses `?` placeholders throughout. No injectable path was found, but the search added in Project 6 was not fuzzed | Add a test with the query `' OR 1=1 --` and assert that no extra rows come back |

**3. Evidence.**

| Ref | Type | Evidence |
|---|---|---|
| E1 | Code | `notes_api/server.py`, `create_server(host="0.0.0.0", ...)` at `e41b7d2` |
| E2 | Runtime | From a second machine, `curl -s -X DELETE http://<laptop-ip>:8000/api/notes/1 -o /dev/null -w "%{http_code}"` printed `204` |
| E3 | Code + runtime | `notes_api/server.py`, `_dispatch`, `except Exception` sends `{"error": repr(exc)}`. With the DB file made read-only, a POST returned `{"error": "OperationalError('attempt to write a readonly database')"}` |
| E4 | Code | `notes_api/server.py`, `_json_body` calls `self.rfile.read(length)` with `length` taken straight from the header |
| E5 | Config | `notes_api/server.py`, `_send` sets `Access-Control-Allow-Origin: *` |

**4. Top three fixes.**

| # | Fix | Addresses | Effort |
|---|---|---|---|
| 1 | Default the bind address to `127.0.0.1`; allow `HOST` to override it only when explicitly set | F1 | S |
| 2 | Log exceptions server-side and return a generic `{"error": "internal error"}` | F2 | S |
| 3 | Reject bodies over 64 KB with HTTP 413 before reading | F3 | S |

**5. Owner.** Sam Okafor (backend owner), due 2026-10-17.

**6. Verification action.**
- New tests: `test_default_bind_is_loopback`, `test_500_hides_internals`, and `test_oversized_body_returns_413`.
- Rerun the E2 `curl` from a second machine and expect the connection to be refused.
- Rerun the E3 reproduction and expect the generic message.
- The full suite must exit 0.

**7. Recommendation.** **Conditional go** for the internal pilot, provided fixes 1 to 3 are merged and verified by 2026-10-17. Until then the server runs on localhost only. **No-go** for any shared-network deployment until authentication is designed.
