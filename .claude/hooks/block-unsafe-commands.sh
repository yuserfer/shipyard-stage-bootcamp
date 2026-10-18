#!/usr/bin/env bash
# block-unsafe-commands.sh — PreToolUse hook for the Bash tool.
#
# Claude Code pipes a JSON event on stdin, for example:
#   {"hook_event_name":"PreToolUse","tool_name":"Bash",
#    "tool_input":{"command":"git push --force origin main"}, ...}
#
# Exit 2 + a reason on stderr  -> the tool call is BLOCKED and Claude sees the reason.
# Exit 0                       -> allowed (normal permission rules still apply).
#
# Blocked categories:
#   1. rm -r/-rf aimed at /, a top-level system dir, ~ / $HOME, ., *, or a ../ path
#   2. git push --force / -f / --force-with-lease / +refspec
#   3. git reset --hard
#   4. curl or wget piped (or substituted) into a shell
#   5. reading or printing secrets: .env files, *.pem, SSH private keys
#   6. chmod 777 (any form, including -R and 0777)
#   7. sudo
#
# Everything else is allowed. Parsing uses python3 (no jq needed).
# Fail-closed: if python3 is missing or the event can't be parsed, the call is blocked.
#
# Alternative (not used here): print
#   {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny",
#    "permissionDecisionReason":"..."}}
# on stdout and exit 0. Exit 2 is simpler to read and test.

set -u

if ! command -v python3 >/dev/null 2>&1; then
  echo "block-unsafe-commands: python3 is required to inspect Bash commands; install python3 or remove this hook." >&2
  exit 2
fi

read -r -d '' CHECKER <<'PY'
import json, re, shlex, sys

try:
    event = json.load(sys.stdin)
except Exception:
    print("could not parse the hook input as JSON")
    sys.exit(0)

command = ((event.get("tool_input") or {}).get("command") or "").strip()
if not command:
    sys.exit(0)

# --- helpers -----------------------------------------------------------------
def segments(cmd):
    """Split a command line into simple commands on ; && || | & and newlines."""
    for part in re.split(r"\|\||&&|[;|&\n]", cmd):
        part = part.strip()
        if not part:
            continue
        try:
            tokens = shlex.split(part, comments=False)
        except ValueError:
            tokens = part.split()
        # drop leading VAR=value assignments and grouping characters
        while tokens and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]) or tokens[0] in ("(", "{", "!")):
            tokens = tokens[1:]
        tokens = [t.lstrip("(").rstrip(")") for t in tokens]
        tokens = [t for t in tokens if t]
        if tokens:
            yield tokens

def program(tokens):
    return tokens[0].rsplit("/", 1)[-1]

def dangerous_rm_target(t):
    if t in ("/", "/*", "~", "~/", "~/*", ".", "./", "*", "./*", "..", "../"):
        return True
    if t.startswith(("~", "$HOME", "${HOME}", "..")):
        return True
    if re.fullmatch(r"/[^/]+/?\*?", t):          # /etc, /usr/, /home/*
        return True
    return False

SECRET_EXCEPTIONS = (".env.example", ".env.sample", ".env.template", ".env.dist")
def is_secret_path(t):
    base = t.rstrip("/").rsplit("/", 1)[-1]
    if base in SECRET_EXCEPTIONS:
        return False
    if base == ".env" or base.startswith(".env."):
        return True
    if base.endswith(".pem"):
        return True
    if base in ("id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"):
        return True
    return False

READERS = {
    "cat", "tac", "less", "more", "head", "tail", "bat", "batcat", "nl", "strings",
    "xxd", "hexdump", "od", "base64", "grep", "egrep", "fgrep", "rg", "ag", "awk",
    "sed", "cut", "sort", "uniq", "diff", "cp", "scp", "rsync", "source", ".",
    "vi", "vim", "nano", "view", "openssl", "curl", "wget", "nc",
}

def deny(reason):
    print(reason)
    sys.exit(0)

# --- whole-string checks -------------------------------------------------------
if re.search(r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(env\s+)?(ba|z|da|k|fi)?sh\b", command):
    deny("piping curl/wget output into a shell runs unreviewed remote code. Download the script, read it, then run it explicitly.")
if re.search(r"\b(ba|z|da|k)?sh\b[^;&|]*(<\(|\$\()\s*(curl|wget)\b", command):
    deny("executing curl/wget output in a shell runs unreviewed remote code. Download the script, read it, then run it explicitly.")
if re.search(r"<\s*[^\s;&|]*(\.env(\.[A-Za-z0-9_-]+)?|\.pem|id_rsa|id_ed25519)\b", command) and not re.search(r"\.env\.(example|sample|template|dist)\b", command):
    deny("reading a secrets file (.env, *.pem, SSH key) would put credentials into the transcript. Ask the user to check the value instead.")
if re.search(r"open\(\s*['\"][^'\"]*(\.env|\.pem|id_rsa|id_ed25519)['\"]", command):
    deny("reading a secrets file (.env, *.pem, SSH key) would put credentials into the transcript. Ask the user to check the value instead.")

# --- per-command checks ----------------------------------------------------------
for tokens in segments(command):
    prog = program(tokens)
    args = tokens[1:]

    if prog in ("sudo", "doas"):
        deny("sudo is not allowed from Claude Code. Ask the user to run privileged commands themselves.")

    if prog == "rm":
        flags = [a for a in args if a.startswith("-")]
        targets = [a for a in args if not a.startswith("-")]
        recursive = any(f in ("--recursive",) or (not f.startswith("--") and re.search(r"[rR]", f)) for f in flags)
        if recursive and any(dangerous_rm_target(t) for t in targets):
            deny("recursive rm on /, ~, $HOME, ., * or a ../ path is irreversible. Delete a specific project-relative path instead.")

    if prog == "git" and "push" in args:
        after = args[args.index("push") + 1:]
        forced = any(
            a.startswith("--force") or a == "-f"
            or (re.fullmatch(r"-[A-Za-z]+", a) and "f" in a)
            or (a.startswith("+") and len(a) > 1)
            for a in after
        )
        if forced:
            deny("force-pushing rewrites shared history. Push normally, or ask the user to force-push after review.")

    if prog == "git" and "reset" in args and "--hard" in args:
        deny("git reset --hard discards uncommitted work. Use git stash, git restore <file>, or /rewind instead.")

    if prog == "chmod" and any(re.fullmatch(r"0?777", a) or a in ("a+rwx", "ugo+rwx") for a in args):
        deny("chmod 777 makes files world-writable. Use the narrowest mode that works, e.g. chmod 755 or chmod +x.")

    if (prog in READERS or prog.startswith("python")) and any(is_secret_path(a) for a in args):
        deny("reading or printing a secrets file (.env, *.pem, SSH key) would put credentials into the transcript. Ask the user to check the value instead.")

sys.exit(0)
PY

reason="$(python3 -c "$CHECKER")"
status=$?

if [ "$status" -ne 0 ]; then
  echo "block-unsafe-commands: internal error while checking the command (python exit $status); blocking to be safe." >&2
  exit 2
fi

if [ -n "$reason" ]; then
  echo "Blocked by block-unsafe-commands hook: $reason" >&2
  exit 2
fi

exit 0
