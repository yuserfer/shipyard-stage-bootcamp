# Maintainer Handoff

> **How to use.** Write this after a refactor or at the end of a feature, once the tests and browser checks pass again. A new maintainer should be able to run the project, understand its structure, and know what is risky, all within 30 minutes and without asking you. Ask Claude to draft it from the code. Then check every command yourself and remove anything you cannot verify. Keep it under two pages, and link to code instead of copying it.

---

| Field | Value |
|---|---|
| Project / component | `__________` |
| Handoff from / to | `__________` |
| Commit | `__________` |
| Date | `__________` |

## 1. Architecture note
- **Purpose:** `__________`
- **Main parts and responsibilities:**

| Part | Path | Responsibility | Depends on |
|---|---|---|---|
| | | | |

- **Data flow (one paragraph or a small diagram):** `__________`
- **Key decisions (with links):** `__________`

## 2. Onboarding
| Step | Command | Expected result |
|---|---|---|
| Prerequisites | | |
| Run tests | | |
| Run the app | | |
| Verify in the browser | | |

Conventions a newcomer must know: `__________`

## 3. Behavior preserved (refactors only)
| Guardrail | Before (commit) | After (commit) |
|---|---|---|
| Test suite result | | |
| Browser checklist result | | |

## 4. Known limitations
| Limitation | Impact | Workaround |
|---|---|---|
| | | |

## 5. Next steps
| # | Task | Why | Suggested owner | Size (S/M/L) |
|---|---|---|---|---|
| 1 | | | | |

## 6. Ownership and contacts
Code owner: `__________` / Escalation: `__________`

---

## Example: Shipyard, Project 8 (release dashboard)

The release dashboard was handed from Dana Ruiz to Sam Okafor at commit `e41b7d2` on 2026-10-14.

**1. Architecture.**

**Purpose:** a single-page view of release tasks and notes for release managers.

| Part | Path | Responsibility | Depends on |
|---|---|---|---|
| Entry | `dashboard/index.html`, `dashboard/js/main.js` | Layout and boot; owns state, wires events | `render.js`, `api.js` |
| API client | `dashboard/js/api.js` | All `fetch` calls; error normalization | Notes API at `:8000` |
| Rendering | `dashboard/js/render.js` | One function per page region (KPIs, tasks, tags, notes) | `logic.js` |
| Rules | `dashboard/js/logic.js` | Pure rules: overdue, filters, KPIs, escaping (node --test) | none |
| Styles | `dashboard/styles.css` | Layout, breakpoints at 768 and 1280 px | none |

**Data flow:** `main.js` calls `api.js`. The results go into `state` and to `render.js`, which renders each region into the DOM. User actions update `state`, call `api.js` if needed, and then re-render the affected regions.

**Key decisions:** no framework and no build step (see `CLAUDE.md`). All network access goes through `api.js`.

**2. Onboarding.**

| Step | Command | Expected |
|---|---|---|
| Prerequisites | `python3 --version` | 3.10 or later |
| Tests | `python3 -m unittest discover -s tests -v` | `OK` |
| API | `python3 -m notes_api.server` | `Shipyard Notes API on http://localhost:8000/api/notes` |
| Dashboard | `python3 -m http.server 8080 -d dashboard` | Page loads with no console errors |
| Browser | Follow `templates/browser-verification-checklist.md`, rows F1 to F4 | All pass |

**Conventions:** use `textContent` for user data, and every component handles its four states.

**3. Behavior preserved.** Before the refactor (`5e8a1c3`): 23 tests passed and browser rows F1 to F4 passed. After the refactor (`e41b7d2`): 23 tests pass and F1 to F4 pass. The diff only moves code; it adds no new behavior.

**4. Known limitations.**

| Limitation | Impact | Workaround |
|---|---|---|
| The task table overflows at 375 px (UI-3) | Mobile users must scroll sideways | Use a tablet or desktop |
| No authentication on the API | Anyone on the network can edit notes | Bind to `127.0.0.1` only |
| The API URL is hard-coded in `api.js` | Cannot point at another host without an edit | Edit `API_BASE` |

**5. Next steps.**

| # | Task | Why | Owner | Size |
|---|---|---|---|---|
| 1 | Make the task table responsive | Fixes UI-3 | Frontend owner | S |
| 2 | Make `API_BASE` configurable | Needed for any non-local deploy | Frontend owner | S |
| 3 | Add release notes view | Next feature (Project 9 Agent Team) | Agent Team lead | M |

**6. Ownership.** Code owner: Sam Okafor. Escalation: Dana Ruiz.
