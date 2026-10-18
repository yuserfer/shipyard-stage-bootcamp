# Post-Release Routine Brief

> **How to use.** Design the routine on paper before you schedule anything. Routines are a research preview on Pro, Max, Team, and Enterprise plans. They run in the cloud against your GitHub repository, run autonomously with no permission picker, and use subscription usage. You manage them with `/schedule` (alias `/routines`) or at claude.ai/code/routines. Because nobody approves each step, the brief itself is the safety boundary. Keep the routine read-only and report-only. Put the human approval point before any action that changes shared state, and make sure the routine has a stop condition. For checks that must see local files or credentials, use `/loop` in an open session (it expires after 7 days) or a desktop scheduled task instead.

---

| Field | Value |
|---|---|
| Routine name | `__________` |
| Engineer of record | `__________` |
| Runs where | cloud routine / `/loop` in a local session / desktop scheduled task |

## 1. Trigger
Schedule (the minimum interval for cloud routines is 1 hour), GitHub event, or API call.

`__________`

## 2. Repository or project scope
Repository, branch, and paths it may read. State explicitly what is out of scope.

`__________`

## 3. Required permissions
| Allowed | Not allowed |
|---|---|
| | |

Credentials or connectors needed (keep them to a minimum, and never production secrets): `__________`

## 4. Expected output
Format, location, and audience. Include an example of a "healthy" and an "unhealthy" result.

`__________`

## 5. Human approval point
Which step requires a human, and who that human is.

`__________`

## 6. Completion or stop condition
When a single run ends, when the routine stops and alerts, and when the whole routine is retired.

`__________`

## 7. Prompt (what the routine is told)
```text
<paste the routine prompt; restate scope, forbidden actions, output format and stop condition>
```

---

## Example: Shipyard post-release verification

| Field | Value |
|---|---|
| Routine name | `shipyard-post-release-check` |
| Engineer of record | Dana Ruiz |
| Runs where | Cloud routine, because the checks need only the pushed repository |

**1. Trigger.** Daily at 09:00 for 14 days after the v1.0 tag. Created with `/schedule daily Shipyard post-release check at 9am`.

**2. Scope.**
- In scope: the `shipyard` GitHub repository, `main` branch. It may read everything except `.env*`.
- Out of scope: other repositories, deployment infrastructure, and any running server.

**3. Permissions.**

| Allowed | Not allowed |
|---|---|
| Clone and read the repository; run `python3 -m unittest discover -s tests -v` | Push to `main`, merge, tag, or delete branches |
| Run `git log v1.0..main --oneline` to list new commits | Edit source files |
| Open **one** GitHub issue labeled `post-release-check` when something is unhealthy | Close or edit other issues; contact anyone outside the repo |

Credentials: the GitHub connection only. No API keys, no `.env`, no production credentials.

**4. Expected output.** A Markdown summary with the date, commit range checked, test result (`Ran N tests`, `OK`/`FAILED`), new commits since v1.0, and a status of HEALTHY or UNHEALTHY.
- When healthy: post the summary in the routine run only.
- When unhealthy: open one issue with the raw failing output and the first bad commit (if it can be identified), and assign it to Dana Ruiz.

**5. Human approval point.** The routine never fixes or reverts anything. Any revert, hotfix, or release decision is made by the engineer of record, after reading the issue and reproducing the failure locally.

**6. Stop condition.**
- Each run ends after one report.
- If an UNHEALTHY issue is already open, the routine adds no new issues; it adds at most one comment per day.
- Dana disables the routine after 14 days, using a calendar reminder; the schedule does not end on its own. She disables it immediately if it ever attempts a disallowed action.
- If the test command cannot run, the routine reports UNHEALTHY with "check could not run". It never reports HEALTHY.

**7. Prompt.**
```text
You are a read-only post-release checker for the shipyard repo, branch main.
1. Run: python3 -m unittest discover -s tests -v. Capture the raw output.
2. Run: git log v1.0..main --oneline.
3. Write a summary: date, commit range, test result lines, new commits, status HEALTHY or UNHEALTHY.
4. If UNHEALTHY and no open issue labeled post-release-check exists, open one with the raw output, assigned to Dana Ruiz. If one exists, add a single comment.
Never edit files, push, merge, tag, revert, or close issues. If any step cannot run, report UNHEALTHY with the reason and stop.
```
