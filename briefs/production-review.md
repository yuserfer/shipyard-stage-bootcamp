# Request: production readiness review before the v1.4 internal rollout

Product asks to roll Shipyard (Notes API + dashboard) out to the whole engineering org next week, on a shared VM.

Run a structured production review and write `reports/production-readiness.md` using the template in `templates/production-readiness-report.md` (or the `release-readiness` skill):
- concise risk summary
- severity-ranked findings, each with evidence (code `file:line`, configuration, test or runtime output)
- top three fixes
- recommended next-step owner
- verification action for each top fix
- a Go / Conditional go / No-go recommendation

Rules: separate verified findings from speculative concerns. Do not fix anything in this step. Do not invent test results: every claim quotes a command and its output.
