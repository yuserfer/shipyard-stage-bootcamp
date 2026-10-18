# Cross-Device Continuation Checklist

> **How to use.** Run through this checklist before you leave your desk with work still running, and again when you pick it up on another device. Two mechanisms are easy to confuse:
>
> - **Remote Control** lets you watch and steer a **local** session from claude.ai/code or the mobile app's Code tab. The `claude` process keeps running on your machine, with your files and credentials.
> - **Cloud sessions** (`claude --cloud "task"`) run in Anthropic's cloud on a fresh clone of your GitHub remote. They cannot see anything you have not pushed.
>
> Decide which one you need, then check credentials, what must stay local, and the stop conditions. Finally, write the status update at the bottom.

---

## 1. Local or cloud?

| Question | If yes |
|---|---|
| Does the work need local files that are not pushed, a local database, `.env`, or a local server? | Remote Control (local) |
| Does the work need logged-in browser sessions (Claude in Chrome) on this machine? | Remote Control (local) |
| Is the work self-contained in the pushed repository, and can the laptop sleep? | Cloud session |
| Do you need to bring cloud work back to the terminal? | `claude --teleport [id]` or `/teleport`. This is one-way, cloud to terminal, and needs a clean git state, the same repository, and a pushed branch |

Choice: `Remote Control / cloud session` because `__________`

## 2. Prerequisites (Remote Control)

| Check | Done |
|---|---|
| Pro, Max, Team, or Enterprise plan; on Team or Enterprise, an Owner has enabled Remote Control | |
| Signed in with a claude.ai login (API keys do not work); not on Bedrock, Vertex, Foundry, or a custom `ANTHROPIC_BASE_URL` | |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is **not** set | |
| Started with `/remote-control` (or `/rc`) in the current session, or `claude --remote-control "Name"` for a new one | |
| Connected from the second device (session URL, QR code, or the session list in claude.ai/code or the mobile app) | |
| The machine will stay awake and online, with the `claude` process alive, for the whole task | |

## 3. Credentials and what stays local

| Item | Where it lives | Leaves the machine? |
|---|---|---|
| `.env`, API tokens, SSH keys | Local only | Never. Do not paste them into the remote chat |
| Local data (`*.db`, `tasks.json`) | Local only | No |
| Browser logins used by Claude in Chrome | Local browser | No |
| Unpushed commits | Local | Only if you push. Required for cloud sessions |
| Conversation and tool output | Visible on the remote device | Yes. Check for secrets in output |

Also note: `/plugin` and `/resume` only work locally. Set the permission mode and deny rules before you leave; do not plan to tighten them from the remote device.

## 4. Before leaving

| Check | Done |
|---|---|
| A recovery point exists (commit hash or branch): `______` | |
| The task has a written goal or `/goal` condition that can be shown in the transcript | |
| The permission mode and deny rules are appropriate for unattended work | |
| Stop conditions are written below and told to Claude | |

## 5. Stop conditions
Claude must stop and wait for you when: `__________`

You stop the session remotely when: `__________`

## 6. Remote verification status update

| Field | Value |
|---|---|
| Task | |
| Device used to monitor | |
| Status | running / waiting for approval / done / stopped |
| Evidence seen remotely (command and result) | |
| Interventions made | |
| Next action and owner | |

---

## Example: Shipyard, Project 10C

**1. Choice: Remote Control.** The verification runs the Notes API and dashboard locally against `notes.db`, which is not in git.

**2. Prerequisites.** Max plan, signed in with a claude.ai login. Started with `/rc` inside the existing session, named "Shipyard verify". Connected from a phone by scanning the QR code. The laptop is plugged in, with sleep disabled for 2 hours.

**3. Local only.** `.env`, `notes.db`, and the Chrome profile stay on the laptop. Nothing is pushed for this task.

**4. Before leaving.**
- Recovery point: `e41b7d2` on branch `verify/p10`.
- Goal: `/goal python3 -m unittest discover -s tests exits 0 and the curl health check returns {"status": "ok"}`.
- Mode: `acceptEdits`, with the Project 1 deny rules active.

**5. Stop conditions.**
- Claude stops and asks before editing any file outside `tests/`, before any git command other than `status`, `diff`, or `log`, and on any failing test it cannot explain.
- I stop the session remotely if it asks to read `.env` or to push.

**6. Status update.**

| Field | Value |
|---|---|
| Task | Post-fix verification of F1 to F3 |
| Device | Phone (mobile app, Code tab) |
| Status | done |
| Evidence | `Ran 54 tests in 1.545s` / `OK`; `curl localhost:8000/api/health` returned `{"status": "ok"}` |
| Interventions | One: told Claude not to modify `server.py` while it was diagnosing a slow test |
| Next | Dana reviews the diff at her desk, then completes Review Before Merge |
