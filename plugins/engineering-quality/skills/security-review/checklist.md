# Security Review Checklist

Work through every section. For each, record either findings (with `path:line`)
or "checked, no issues" with what you checked.

## 1. Secrets

- [ ] No API keys, tokens, passwords, private keys, or connection strings in code,
      tests, fixtures, docs, or commit history in scope
- [ ] Grep patterns: `(?i)(api[_-]?key|secret|token|passw(or)?d|bearer)\s*[:=]`,
      `AKIA[0-9A-Z]{16}`, `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----`,
      `ghp_[A-Za-z0-9]{36}`, `sk-[A-Za-z0-9]{20,}`
- [ ] `.env`, `*.pem`, key files are listed in `.gitignore` (check `.gitignore`,
      do not open the secret files)
- [ ] Secrets come from environment variables or a secret store, with a clear error
      when missing (no hard-coded fallback value)
- [ ] Secrets are never logged, printed, or included in error messages

## 2. Dependencies

- [ ] Every new import or package is needed (Shipyard target: Python stdlib only,
      no npm runtime dependencies for the dashboard)
- [ ] Versions pinned in the manifest (`requirements.txt`, `package.json`,
      lockfile) when third-party packages exist
- [ ] Packages come from the official registry; names are not typo-squats
- [ ] No `curl | sh` style install steps in scripts or docs
- [ ] Note known-vulnerable versions only if you can cite the advisory; otherwise
      list as speculative

## 3. Input validation

- [ ] Every entry point identified: CLI args, HTTP path/query/body/headers, files,
      env vars
- [ ] Types, lengths, ranges, and formats checked at one boundary (service layer)
- [ ] Request size limits (`Content-Length` checked and capped)
- [ ] JSON parsing errors return 400, not 500 with a traceback
- [ ] IDs validated before lookup; missing records return 404
- [ ] Dates parsed strictly (e.g. `date.fromisoformat`) with clear errors

## 4. Authentication

- [ ] Does the feature need authentication? If the API is local-only, is it bound
      to `127.0.0.1` rather than `0.0.0.0`?
- [ ] If auth exists: credentials compared in constant time (`hmac.compare_digest`),
      tokens not in URLs or logs, sessions expire
- [ ] No "debug" bypass flags left enabled

## 5. Authorization

- [ ] Every mutating operation (create/update/delete) checks that the caller may do it
- [ ] Users can't read or change other users' records by changing an ID (IDOR)
- [ ] Admin-only actions are not reachable from normal paths

## 6. Permissions

- [ ] Files created with sensible modes (no `0o777`, no world-writable data files)
- [ ] No new `sudo`, privileged ports, or root-only paths
- [ ] Claude Code settings: no widened `permissions.allow` rules (e.g. `Bash(*)`),
      no disabled hooks, no `bypassPermissions` in project settings
- [ ] Hook scripts don't run untrusted input as code

## 7. Unsafe data flows

| Sink | Unsafe pattern | Safe pattern |
|------|----------------|--------------|
| Shell | `os.system(f"... {x}")`, `subprocess(..., shell=True)` with input | `subprocess.run([...], shell=False)` with an argument list |
| File path | `open(base + user_path)` | Resolve with `os.path.realpath`, check it stays under the base directory |
| HTML (dashboard) | `el.innerHTML = note.title` | `el.textContent = note.title` |
| Eval | `eval`, `exec`, `new Function`, `pickle.loads` on input | Parse with `json` |
| Logs | Logging full request bodies or headers | Log IDs and status codes only |
| Redirects / URLs | Fetching a user-supplied URL | Allow-list hosts |

## 8. Error handling and logging

- [ ] No stack traces or internal paths returned to clients
- [ ] Errors logged with enough context to debug, without secrets or personal data
- [ ] Failures don't leave partial writes (atomic write: temp file + `os.replace`)

## Severity scale

| Severity | Definition | Example |
|----------|------------|---------|
| Critical | Exploitable now; leads to credential exposure, RCE, or data loss | Hard-coded production key; `shell=True` with request data |
| High | Exploitable with plausible input; serious integrity or availability impact | Path traversal in file read; unbounded body read |
| Medium | Needs unusual conditions, or limited impact | Missing tag validation rendered as text; verbose 500 errors |
| Low | Hardening or defence in depth | Missing security headers on a local-only server |

Always separate **verified** findings (exact line, explained path) from
**speculative** concerns (plausible but unconfirmed).
