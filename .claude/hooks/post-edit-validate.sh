#!/usr/bin/env bash
# post-edit-validate.sh — PostToolUse hook for Edit|Write.
#
# After Claude edits a file, run the test suite that covers it:
#   *.py anywhere in the project          -> python3 -m unittest discover -s tests -q
#   dashboard/**/*.js or *.mjs            -> node --test dashboard/tests/*.mjs  (only if node exists)
#   anything else (Markdown, JSON, ...)   -> nothing runs, exit 0
#
# Exit 0 -> tests passed or were not relevant.
# Exit 2 -> tests failed; the tail of the test output goes to stderr, which Claude reads
#           as feedback (the edit has already happened, so Claude is told to fix it).
#
# Parsing uses python3 (no jq needed). Project root: $CLAUDE_PROJECT_DIR, falling back
# to the "cwd" field of the hook input.

set -u

if ! command -v python3 >/dev/null 2>&1; then
  echo "post-edit-validate: python3 not found; skipping validation." >&2
  exit 0
fi

# Prints two lines: the project root and the edited file path relative to it
# (empty second line if the file is outside the project or missing from the input).
parsed="$(python3 -c '
import json, os, sys
try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)
root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
root = os.path.realpath(root)
path = (event.get("tool_input") or {}).get("file_path") or ""
rel = ""
if path:
    full = os.path.realpath(path if os.path.isabs(path) else os.path.join(root, path))
    if full == root or full.startswith(root + os.sep):
        rel = os.path.relpath(full, root)
print(root)
print(rel)
')"

root="$(printf '%s\n' "$parsed" | sed -n '1p')"
rel="$(printf '%s\n' "$parsed" | sed -n '2p')"

[ -n "$root" ] && [ -n "$rel" ] || exit 0
cd "$root" || exit 0

run_suite() {
  # $1 = label, rest = command. Captures output; on failure prints the tail and exits 2.
  local label="$1"; shift
  local output status
  output="$("$@" 2>&1)"
  status=$?
  if [ "$status" -ne 0 ]; then
    {
      echo "post-edit-validate: $label FAILED after editing $rel (exit $status)."
      echo "Command: $*"
      echo "----- last 60 lines of output -----"
      printf '%s\n' "$output" | tail -n 60
      echo "-----------------------------------"
      echo "Fix the failure (or revert the edit) before continuing. Do not weaken or delete tests to make them pass."
    } >&2
    exit 2
  fi
}

case "$rel" in
  *.py)
    if [ -d tests ]; then
      run_suite "Python unit tests" python3 -m unittest discover -s tests -q
    fi
    ;;
  dashboard/*.js|dashboard/*.mjs)
    if command -v node >/dev/null 2>&1 && [ -d dashboard/tests ]; then
      run_suite "Dashboard tests" node --test dashboard/tests/*.mjs
    fi
    ;;
  *)
    : # not a file we validate
    ;;
esac

exit 0
