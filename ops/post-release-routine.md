# Post-Release Routine: Shipyard v1.4

Written from `templates/post-release-routine-brief.md`. Nothing is scheduled yet. Design first, schedule after the engineer of record approves it.

| Field | Value |
|---|---|
| Routine name | `shipyard-post-release-check` |
| Engineer of record | Arsen (human reviewer; Claude never decides) |
| Runs where | **Split.** Cloud routine for the read-only checks. Everything else stays local (see "Local vs cloud"). |

**Preconditions (not met today).** This repository has no git remote and no release tag (`git remote -v` and `git tag` both print nothing). A cloud routine runs against a pushed GitHub repository, so someone must first push the repo and create the `v1.4` tag, using their own credentials. The routine cannot be scheduled before then.

## 1. Trigger
Proposed: daily at 09:00 for 14 days after the `v1.4` tag is pushed. The minimum interval for cloud routines is 1 hour, so daily is allowed. The time and the 14-day window are proposals for the engineer of record to confirm, not facts from the project documents.

## 2. Repository scope
- **In scope:** this repository on GitHub, branch `main`. It may read everything except `.env*` and any credentials.
- **Out of scope:** other repositories, deployment infrastructure, any server it did not start itself, `SAFETY.md`, `.claude/settings.json` and `briefs/` (read only, never edited).

## 3. Required permissions (least privilege)
| Allowed | Not allowed |
|---|---|
| Clone and read the repository | Push, merge, tag, delete branches, or rewrite history |
| `python3 -m unittest discover -s tests -q` | Edit any file, including reports and docs |
| `node --test "dashboard/tests/*.mjs"` | Install packages or download anything |
| `python3 scripts/readiness_probe.py` (binds `127.0.0.1` on a free port, in-memory database, stops itself) | Start any other server or listen on a public interface |
| `git log v1.4..main --oneline` | Read `.env*`, keys or credentials |
| Open **one** GitHub issue labeled `post-release-check` when unhealthy; add at most one comment per day to it | Close or edit other issues, or contact anyone outside the repository |

Credentials: the GitHub connection only. No API keys, no `.env`, no production credentials.

## 4. Expected output
A Markdown summary in the routine run: date, commit range, test summary lines copied verbatim, probe lines copied verbatim, new commits since `v1.4`, status.

- **HEALTHY:** `Ran 54 tests` … `OK`; `ℹ pass 10` and `ℹ fail 0`; probe shows bind `127.0.0.1`, no CORS header, writes without a token answered `401`, oversized request answered `413`. Summary stays in the run. No issue.
- **UNHEALTHY:** any failed test, or any probe line unchanged from the current RED result (`bind address default: 0.0.0.0`, `CORS header: *`, `unauthenticated DELETE: HTTP 204`, `returned unescaped: True`, `no answer after 2 s`). Open one issue with the raw output and the first bad commit if it can be found.
- **Today's baseline is RED** (`ops/remote-verification-status.md`). Until fixes 1–3 are merged, the routine will report UNHEALTHY every run. Schedule it after the fixes, or it will only repeat a known result.

## 5. Human approval point
The routine only reports. Any fix, revert, hotfix, push, tag or release decision belongs to Arsen, after reading the issue and reproducing the failure locally. Claude proposes; the human reviews and merges.

## 6. Completion or stop condition
- **One run:** ends after one report.
- **Dedupe:** if a `post-release-check` issue is already open, no new issue; at most one comment per day.
- **Retire:** Arsen disables the routine after 14 days. The schedule does not end on its own, so set a calendar reminder.
- **Stop and alert:** disable it immediately if it ever attempts a disallowed action.
- **Could not run:** if any command cannot run (for example Node missing), report UNHEALTHY with "check could not run". Never report HEALTHY.

## Local vs cloud
| Must stay local | Can run as a cloud routine |
|---|---|
| Anything needing `.env`, credentials or other secrets | Python and dashboard test suites (pushed code only) |
| `git push`, remotes, tags, commits, force-pushes (blocked for Claude in `SAFETY.md`) | `scripts/readiness_probe.py` (its own loopback server inside the cloud sandbox) |
| Fixes, reverts and hotfixes | `git log v1.4..main` |
| Phone-width and real-browser checks (need Chrome and the dashboard running) | Opening or commenting on the single `post-release-check` issue |
| Checks against a scratch database (`SHIPCTL_DB`) or the shared VM | Writing the summary |
| Short-lived interactive monitoring: use `/loop` in an open session, which expires after 7 days | |

Cloud routines run with no permission prompts, so the prompt below is the safety boundary.

## 7. Prompt
```text
You are a read-only post-release checker for this repository, branch main.
1. Run: python3 -m unittest discover -s tests -q. Capture the raw output.
2. Run: node --test "dashboard/tests/*.mjs". Capture the raw output.
3. Run: python3 scripts/readiness_probe.py. Capture the raw output.
4. Run: git log v1.4..main --oneline.
5. Write a summary: date, commit range, the raw test and probe summary lines, new commits, status HEALTHY or UNHEALTHY.
   HEALTHY only if all tests pass and the probe shows bind 127.0.0.1, no CORS header, 401 for writes without a token, and 413 for an oversized request.
6. If UNHEALTHY and no open issue labeled post-release-check exists, open one with the raw output. If one exists, add a single comment.
Never edit files, push, merge, tag, revert, install anything, read .env or credentials, or close issues.
If any step cannot run, report UNHEALTHY with the reason and stop.
```
