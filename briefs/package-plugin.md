# Engineering brief: package the Engineering Quality plugin

## Outcome
Any Shipyard repository (and any other team repo) can install the Part 9 review workflow with one command, instead of copying files.

## Package
`plugins/engineering-quality/` containing:
- `.claude-plugin/plugin.json` — name `engineering-quality`, version `1.0.0`, description, author, license.
- `skills/change-review/` and `skills/security-review/` (with their supporting files).
- `agents/security-reviewer.md`.
- `hooks/hooks.json` (top-level `"hooks"` key) wiring `post-edit-validate.sh` and `block-unsafe-commands.sh` via `${CLAUDE_PLUGIN_ROOT}`.
- `README.md` — what it bundles, install, invoke, versioning, trust.

And a marketplace at the repo root: `.claude-plugin/marketplace.json` named `shipyard-tools`, listing the plugin with source `./plugins/engineering-quality`.

## Acceptance
1. `claude plugin validate ./plugins/engineering-quality --strict` passes (save the output to `evidence/plugin-validate.txt`).
2. `claude plugin validate . --strict` passes for the marketplace.
3. Local test: `claude --plugin-dir ./plugins/engineering-quality`, then `/engineering-quality:change-review` appears and runs.
4. Marketplace install works: `/plugin marketplace add ./` then `/plugin install engineering-quality@shipyard-tools`.
5. No secrets, no absolute paths, scripts executable.
