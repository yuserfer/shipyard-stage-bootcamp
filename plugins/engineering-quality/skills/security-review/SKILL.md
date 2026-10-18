---
name: security-review
description: Read-only security review of pending changes or a named path. Checks secrets, dependencies, input validation, authentication, authorization, permissions, and unsafe data flows, and returns severity-ranked findings, each with file:line, quoted evidence, impact, and a concrete fix, keeping verified findings apart from speculative concerns.
when_to_use: Use when the user asks for a "security review", "security check", "is this safe", "check for secrets", "audit the API", or before merging changes that touch request handling, file I/O, shell calls, auth, configuration, or dependencies.
argument-hint: "[optional: path, module, or git range; default is uncommitted changes]"
allowed-tools: Read Grep Glob Bash(git diff *) Bash(git status *) Bash(git log *)
context: fork
agent: Explore
background: false
---

# Security Review

> Plugin edition: invoke as `/engineering-quality:security-review`. The plugin
> namespace keeps it separate from Claude Code's built-in `/security-review`.

**Scope:** $ARGUMENTS

You are running in a forked, read-only context. You do **not** see the main
conversation, so work only from the scope above and the repository itself.

## Determine the scope

- If the scope is a path or module (e.g. `notes_api/`), review those files in full.
- If it is a git range (e.g. `main..HEAD`), review `git diff <range>`.
- If it is empty, review uncommitted work: `git status --short`, `git diff`,
  `git diff --staged`, plus untracked files. If there are no changes, review the
  whole project's entry points (CLI argument handling, HTTP handlers, file I/O).

State the resolved scope at the top of the report.

## Procedure

1. **Map the attack surface.** List every place untrusted data enters: CLI args,
   HTTP paths/query/body/headers, files read from disk, environment variables.
2. **Walk the checklist** in [checklist.md](checklist.md), section by section:
   secrets, dependencies, input validation, authentication, authorization,
   permissions, unsafe data flows, error handling and logging.
3. **Trace each input** from entry to sink (storage, file path, shell, HTML, log).
   Note whether it is validated, encoded, or bounded on the way.
4. **Classify each finding:**
   - **Verified:** you can point to the exact line and explain the exploit path.
   - **Speculative:** a plausible concern you could not confirm from the code
     (say what would confirm it).
5. **Rate severity** (Critical, High, Medium, Low) using the scale in the
   checklist. Rate by impact and likelihood, not by how easy the fix is.
6. **Write a fix** for each verified finding: the specific change, not "validate input".
7. **Report** in the format below, highest severity first.

## Output format

```markdown
# Security Review: <scope>

**Scope reviewed:** <paths or range>  **Files read:** <n>
**Summary:** <Critical n, High n, Medium n, Low n; one-sentence overall risk>

## Verified findings
### [High] SR-1: <title>
- **Location:** `notes_api/server.py:74`
- **Evidence:**
      <quoted code line(s), copied verbatim>
- **Impact:** <what an attacker or bad input can do>
- **Fix:** <specific change>
- **Verify with:** <test or command that would prove the fix>

## Speculative concerns
- SC-1: <concern> at `<path>`. Would be confirmed by: <check>.

## Checked with no issues found
- Secrets: grep for key/token/password patterns across <scope>: none
- ...

## Out of scope / not checked
- <e.g. deployment config not in repo>
```

## Rules

- Read-only. Never edit, create, or delete files. Never commit or push.
- **Never print a secret.** If you find one, report the file:line and the type
  (e.g. "AWS access key"), and show it redacted: `AKIA****************`.
- Do not open `.env`, `*.pem`, or private key files to "check" them. Report
  their presence (and whether `.gitignore` covers them) instead.
- Quote evidence exactly as it appears in the file. No invented line numbers.
- Do not run the application, install tools, or make network requests.
- Speculative concerns never go in the Verified section.

## Relationship to the plugin's subagent

This skill forks into the built-in read-only `Explore` agent so it works
everywhere. For a second opinion with a fixed output contract, ask the main
session to use the `engineering-quality:security-reviewer` subagent on the same
files. `/engineering-quality:change-review` does this automatically for its
security point.

## Worked example (Shipyard Notes API)

`/engineering-quality:security-review notes_api/`

- **[High] SR-1: Unbounded request body.** `notes_api/server.py:41`:
  `body = self.rfile.read(int(self.headers["Content-Length"]))`. A huge
  Content-Length makes the server allocate unbounded memory, and a missing header
  raises `TypeError` (500). Fix: reject a missing header with 411 and cap at
  64 KiB with 413. Verify with a unittest posting a 1 MB body and expecting 413.
- **[Medium] SR-2: Tag values unvalidated.** `notes_api/service.py:22` stores any
  string as a tag; the dashboard renders tags. Fix: allow only `[a-z0-9-]{1,32}`.
- **Speculative SC-1:** the dashboard may render note titles with `innerHTML`;
  confirm by grepping `dashboard/` for `innerHTML`.
