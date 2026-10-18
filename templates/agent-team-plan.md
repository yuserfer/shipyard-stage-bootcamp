# Agent Team Plan

> **How to use.** Write this plan before you launch an Agent Team, and use it to steer and review the team.
>
> - **Availability.** Agent Teams are experimental and off by default. Enable them with `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` in settings, or set the same variable in your shell.
> - **When to use a team.** Only when the work splits into parallel tracks that need to talk to each other. For a single focused task, use one session or a subagent. Teams cost significantly more tokens, and the cost grows with each teammate.
> - **Plan approval.** The docs state that a teammate's plan is auto-approved without the lead reviewing it. Section 4 therefore adds a human approval gate.
> - **Limitations.** `/rewind` and `/resume` do not restore in-process teammates, and teammate permissions are fixed at spawn. Make a git recovery point first.
>
> Learners without access complete sections 6 and 7 using the supplied transcript, task board, and diffs.

---

| Field | Value |
|---|---|
| Feature | `__________` |
| Lead (main session) / engineer of record | `__________` |
| Recovery point | `__________` |
| Display mode | `in-process` (default) / `tmux` / `iterm2` |
| Budget (tokens or time) | `__________` |

## 1. Roles
| Role | Responsibility | Model / effort | Spawn instruction (summary) |
|---|---|---|---|
| Lead | Splits the work, reviews, integrates | | |
| | | | |

## 2. File ownership
Each file has exactly one writer. Shared files are owned by the lead or changed through one task.

| Path | Owner | Others may |
|---|---|---|
| | | read only |

## 3. Task list
| ID | Task | Owner | Depends on | Done when (evidence) |
|---|---|---|---|---|
| T1 | | | | |

## 4. Plan approval
- Start the lead in plan mode, so teammates work read-only until their plan is ready.
- Do not rely on the automatic approval. Tell the lead: "Before any teammate edits files, present every teammate's plan to me and wait for my approval."
- Human approval of the plans: `approved by ______ at ______`

## 5. Quality gates
| Gate | Mechanism | Blocks |
|---|---|---|
| Tests pass before a task is marked complete | `TaskCompleted` hook that runs the suite and exits 2 on failure | task completion |
| No edits outside owned files | Spawn instructions plus a review of the diff stat per teammate | integration |
| Review | `/engineering-quality:change-review` on the integrated diff, plus the security-reviewer subagent | acceptance |
| Runtime | Browser verification of the integrated feature | acceptance |

## 6. Coordination risks
| Risk | Likelihood | Mitigation | Observed? |
|---|---|---|---|
| Two teammates edit the same file | | | |
| API contract drift between frontend and backend | | | |
| Task status lags behind the real state | | | |
| Token cost exceeds the budget | | | |

## 7. Retrospective
| Question | Answer |
|---|---|
| What did parallelism actually save? | |
| Where did coordination fail or need steering? | |
| Which gate caught a real problem? | |
| Would a single session or a subagent have been better? Why? | |
| What changes next time? | |

---

## Example: Shipyard, Project 9C (release notes on the dashboard)

| Field | Value |
|---|---|
| Feature | Release notes: tag notes `release-note` in the API; show them grouped by version on the dashboard |
| Lead / engineer of record | Instructor session / Luca Berton |
| Recovery point | `e41b7d2`, branch `feature/release-notes` |
| Display | `in-process` |
| Budget | 45 minutes |

**1. Roles.**

| Role | Responsibility | Model / effort |
|---|---|---|
| Lead | Splits the work, owns the API contract, integrates | default / high |
| Frontend owner | Release notes component and its states | sonnet / medium |
| Backend owner | Release-notes query endpoint in the Notes API | sonnet / medium |
| Test and verification owner | API tests, browser verification, evidence | sonnet / medium |

**2. File ownership.**

| Path | Owner | Others may |
|---|---|---|
| `notes_api/**` | Backend owner | read |
| `dashboard/js/release-notes.js`, `dashboard/js/main.js`, `dashboard/index.html`, `dashboard/styles.css` | Frontend owner | read |
| `tests/test_release_notes.py`, `dashboard/tests/release-notes.test.mjs`, `evidence/` | Test owner | read |
| `docs/team-plan.md` (frozen contract) | Lead | read |

**3. Tasks.**

| ID | Task | Owner | Depends on | Done when |
|---|---|---|---|---|
| T1 | Write the API contract for `GET /api/notes?tag=release-note` | Lead | none | Contract committed |
| T2 | Implement the tag filter in the service and repository | Backend | T1 | `tests/test_release_notes.py` passes |
| T3 | Write end-to-end tests for T1's contract | Test | T1 | Tests fail before T2 and pass after it |
| T4 | Release notes component (loading, empty, error, populated) | Frontend | T1 | Renders against the contract fixture |
| T5 | Integrated browser verification | Test | T2, T4 | Checklist F1 to F4 pass, with evidence |

**4. Plan approval.** The lead was in plan mode and showed all three plans to the engineer of record. One change was requested: the frontend plan had edited `main.js`, which nobody owned, so wiring moved to the lead. Approved by Luca Berton at 14:31.

**5. Gates.**
- `TaskCompleted` hook runs `python3 -m unittest discover -s tests` and exits 2 on failure.
- `/engineering-quality:change-review` runs on the integrated diff.
- The `engineering-quality:security-reviewer` subagent checks the new query parameter.

**6. Coordination risks observed.** The backend first returned `tags` as a comma string while the contract said list. The test owner's T3 caught this, and the lead messaged the backend owner directly. Task T4 showed "in progress" for about 2 minutes after it had finished.

**7. Retrospective.**
- Parallelism saved about 10 minutes on T2 and T4.
- Writing the contract first (T1) prevented most of the drift.
- The hook blocked one premature completion.
- For a change this size, one session plus a test subagent would have been cheaper. A team is worth it when there are three or more independent tracks.
