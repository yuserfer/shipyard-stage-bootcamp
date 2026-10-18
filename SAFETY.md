# Shipyard: permission and safety boundary

Engineer of record: the learner. Claude proposes changes; a human reviews and merges them.

## Permission mode

- Default for this workshop: **Manual** (`default`) while learning; switch to `acceptEdits` for focused edit loops.
- **Plan mode** (`Shift+Tab`) for anything touching more than two files or any new design.
- **Auto mode** only inside a staged copy (`~/shipyard-stage`) with a clean recovery commit.
- Never `bypassPermissions` outside a disposable container.

## Allowed without asking

| Action | Why it is safe |
|---|---|
| Read any file in the repo (except secrets) | Read-only |
| Edit source, tests and docs | Reversible with git |
| `python3 -m unittest …`, `node --test …` | Local, no side effects |
| `python3 shipctl.py …` with `SHIPCTL_DB` pointing at a scratch file | Local data only |
| `git status`, `git diff`, `git log` | Read-only |

## Ask first

| Action | Why |
|---|---|
| `git commit` | Creates history the human must own |
| Installing anything | Changes the environment |
| Starting a server on a public interface | Network exposure |

## Blocked

| Action | Why |
|---|---|
| `git push`, force push, `git reset --hard` | Irreversible or affects shared state |
| `rm -rf` | Irreversible |
| Reading `.env`, keys, credentials | Secrets never enter the context |
| `curl … \| sh`, network downloads | Untrusted code |
| Editing `.claude/settings.json` | Changes the guardrails themselves |

## Reversible vs irreversible

- Reversible: file edits (git, `/rewind`), local test runs, branches and worktrees.
- Irreversible: pushes, deletions outside git, sent messages, deployments, credential changes.
- Rule: autonomy is proportional to reversibility. Anything irreversible needs a human approval point.

## Recovery point

- Baseline commit created before any autonomous work: `git log --oneline -1` → `start of part 01`.
- Restore with `git restore .` (unstaged edits) or `git reset --hard <baseline>` — run by the human, never by Claude.
