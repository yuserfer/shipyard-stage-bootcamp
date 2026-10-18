# Brief: keep verification going away from the desk

1. **Remote Control.** Start the release verification locally:
   `claude --remote-control "Shipyard v1.4 verification"` (or `/remote-control` inside a running session).
   Ask it to run both test suites and the readiness probe, then continue from the claude.ai/code page or the Claude mobile app. Steer it once from the phone. The session keeps running on your machine: local files, local credentials, local tools.
2. **Status update.** From the phone, ask for a five-line verification status and save it to `ops/remote-verification-status.md`.
3. **Routine design.** Write `ops/post-release-routine.md` for a recurring post-release check with: trigger, repository or project scope, required permissions, expected output, human approval point, completion or stop condition. Decide what must stay local and what can run as a cloud routine (`/schedule`).
4. **Checklist.** Fill `ops/cross-device-checklist.md`.
