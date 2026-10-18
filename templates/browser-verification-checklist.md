# Browser Verification Checklist (Manual Fallback)

> **How to use.** Use this checklist if you cannot use Claude in Chrome. That includes WSL, where the integration is not supported, plans without access, a missing extension, and Bedrock, Vertex, or Foundry setups. Run the same checks Claude would run, in Chrome or another Chromium browser with DevTools open, and capture evidence for each one. If you received the supplied captured browser evidence instead of running the app, review those captures against the same rows. Record every problem in the issue log. After a fix, rerun the failing row and attach "after" evidence. With Claude in Chrome available, `claude --chrome` plus the `browser-verification` Skill covers the same list.

---

## 0. Setup

| Field | Value |
|---|---|
| App URL | `__________` |
| Backend running (command) | `__________` |
| Commit under test | `__________` |
| Browser and version | `__________` |
| Evidence folder | `__________` |

Open DevTools (F12, or Cmd+Option+J on macOS) and keep the **Console** and **Network** tabs visible. Enable **Preserve log**.

## 1. Core flows

| # | Flow / step | Expected | Result (Pass / Fail) | Evidence file |
|---|---|---|---|---|
| F1 | `__________` | `__________` | | |
| F2 | `__________` | `__________` | | |
| F3 | Form validation with empty or invalid input | Inline error; no request sent, or a 400 is handled | | |
| F4 | Backend stopped, then reload | Error state with retry; no blank page | | |

## 2. Console and network

| Check | Expected | Result | Evidence |
|---|---|---|---|
| Console errors during F1 to F4 | none | | |
| Unhandled promise rejections | none | | |
| Failed requests (4xx/5xx) in Network | only the deliberate ones (F3, F4) | | |
| Responses contain no stack traces or secrets | none | | |

## 3. Responsive breakpoints

Use the DevTools device toolbar (Ctrl+Shift+M, or Cmd+Shift+M on macOS).

| Width | No horizontal scroll | Navigation usable | Content readable | Evidence |
|---|---|---|---|---|
| 375 px (mobile) | | | | |
| 768 px (tablet) | | | | |
| 1280 px (desktop) | | | | |

## 4. Basic accessibility

| Check | Result |
|---|---|
| All actions reachable with Tab; focus is visible | |
| Buttons and inputs have labels | |
| Status changes are announced (`aria-live`) or visible | |

## 5. Evidence capture rules
- Name files `<row>-<before|after>-<width>.png`, for example `F2-before-1280.png`.
- For console evidence, save a screenshot of the Console panel, or right-click and choose "Save as..." to export the log.
- For network evidence, open the request and copy the status code and response body into the issue log.
- Write down the commit hash for every "after" capture.
- Never capture tokens, cookies, or personal data. Crop or redact them before saving.

## 6. Issue log

| ID | Row | Severity | Expected | Actual (before) | Before evidence | Fix (commit) | After evidence | Status |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | open / fixed / won't fix |

---

## Example: Shipyard, Project 7 (release dashboard)

**Setup.**
- App: `http://localhost:8080`, started with `python3 -m http.server 8080 -d dashboard`.
- Backend: `python3 -m notes_api.server` on port 8000.
- Commit under test: `5e8a1c3`. Browser: Chrome 130. Evidence folder: `evidence/`.

| # | Flow | Expected | Result | Evidence |
|---|---|---|---|---|
| F1 | Load the dashboard | Task summary cards and the pending task list render | Pass | `F1-before-1280.png` |
| F2 | Mark task #3 done | Row moves to Done; the pending count drops by 1 | Fail | `F2-before-1280.png` |
| F3 | Submit "Add note" with an empty title | Inline "Title is required"; no POST is sent | Pass | `F3-before-1280.png` |
| F4 | Stop the API, then reload | "Cannot reach API" message with a Retry button | Fail | `F4-before-console.png` |

| ID | Row | Severity | Expected | Actual (before) | Before | Fix | After | Status |
|---|---|---|---|---|---|---|---|---|
| UI-1 | F2 | Medium | The pending count updates | The count stays at 5 until a page reload | `F2-before-1280.png` | `9b2d4e0`: re-render the summary after the status change | `F2-after-1280.png` | fixed |
| UI-2 | F4 | High | Error state | Blank list; console shows `TypeError: Cannot read properties of undefined (reading 'length')` | `F4-before-console.png` | `c17f0a8`: handle fetch failure in `api.js` and render the error state | `F4-after-console.png` (console clean) | fixed |
| UI-3 | 375 px | Low | No horizontal scroll | The task table overflows by about 120 px | `R375-before.png` | not fixed in this sprint | n/a | won't fix (handed off) |
