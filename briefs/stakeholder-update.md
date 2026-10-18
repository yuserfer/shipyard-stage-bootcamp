# Request: one-page stakeholder update (Claude Cowork)

Audience: VP Engineering, Product lead, Support lead. They will read it on a phone between meetings.

Inputs (give Cowork access to the folder, or attach):
- `reports/production-readiness.md`
- `docs/HANDOFF.md`
- `docs/team-plan.md`, the task list (`python3 shipctl.py list --status all`)

Produce `reports/stakeholder-update.md` (and, if you use Cowork, a one-page `.docx`), containing exactly:
current release status · features completed · customer or business impact · major risks · decisions required · top three fixes · owners and deadlines · recommended next step.

Rules: keep technical accuracy (no softened severities, no invented dates); translate each risk into business impact; one page; review every connector or browser action Cowork proposes before approving.
Fallback without Cowork: run the `stakeholder-update` skill from the Skills Pack in Claude Code with the same inputs.
