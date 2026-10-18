# engineering-quality (Claude Code plugin)

The Part 10 deliverable of **Claude Code Bootcamp: Cohort 2**. This plugin packages
the Part 9 workflow into one installable unit: the Review Before Merge skill, the
security review skill and subagent, and the two quality-gate hooks.

## What it bundles

| Component | Path | How you use it |
|-----------|------|----------------|
| Skill: change-review | `skills/change-review/` (with `checklist.md`) | `/engineering-quality:change-review [scope]`: seven-point Review Before Merge checklist |
| Skill: security-review | `skills/security-review/` (with `checklist.md`) | `/engineering-quality:security-review [path or git range]`: read-only review in a forked `Explore` context |
| Subagent: security-reviewer | `agents/security-reviewer.md` | "Use the engineering-quality:security-reviewer agent on notes_api/" (or pick it from the @ mention menu) |
| Hook: block unsafe commands | `hooks/block-unsafe-commands.sh` | Automatic. `PreToolUse` on `Bash`: blocks `rm -rf` on `/`, `~`, or `..`; force pushes; `git reset --hard`; `curl \| sh`; reading `.env`, `*.pem`, or SSH keys; `chmod 777`; `sudo` |
| Hook: post-edit validation | `hooks/post-edit-validate.sh` | Automatic. `PostToolUse` on `Edit\|Write`: runs `python3 -m unittest discover -s tests -q` after `.py` edits and `node --test "dashboard/tests/*.mjs"` after `dashboard/*.js` or `*.mjs` edits. Failures go back to Claude (exit 2) |
| Manifest | `.claude-plugin/plugin.json` | Name, version, author, license |
| Hook wiring | `hooks/hooks.json` | Uses `"${CLAUDE_PLUGIN_ROOT}"/hooks/...` so the scripts resolve wherever the plugin is installed |

Requirements: `bash` and `python3`. `node` is optional; without it, dashboard tests are skipped. `jq` is not needed.

```
plugins/engineering-quality/
├── .claude-plugin/plugin.json
├── agents/security-reviewer.md
├── hooks/
│   ├── hooks.json
│   ├── block-unsafe-commands.sh
│   └── post-edit-validate.sh
├── skills/
│   ├── change-review/{SKILL.md,checklist.md}
│   └── security-review/{SKILL.md,checklist.md}
└── README.md
```

## 1. Validate

From the repository root:

```bash
claude plugin validate ./plugins/engineering-quality --strict   # the plugin
claude plugin validate . --strict                               # the marketplace in .claude-plugin/marketplace.json
```

`--strict` turns warnings (unknown fields, unquoted `${CLAUDE_PLUGIN_ROOT}`, missing
metadata) into failures. Use it in CI. The last recorded output is in
[evidence/plugin-validate.txt](../../evidence/plugin-validate.txt).

## 2. Test locally without installing

```bash
cd ~/src/shipyard            # your workshop project
claude --plugin-dir./path/to/shipyard/plugins/engineering-quality
```

Inside the session:

1. `/plugin`: the plugin shows as loaded; check the **Errors** tab is empty.
2. `/hooks`: you should see the `PreToolUse` (Bash) and `PostToolUse` (Edit|Write) entries from this plugin.
3. Ask Claude to run `git reset --hard`. The hook blocks it, and Claude reports the reason.
4. Ask for a small edit to `notes_api/service.py`. The tests run automatically.
5. Run `/engineering-quality:change-review`.

After you edit plugin files, run `/reload-plugins` instead of restarting.

## 3. Install through the marketplace

This repository is also a marketplace named **`shipyard-tools`**
(`.claude-plugin/marketplace.json` at the repo root).

Inside a Claude Code session:

```text
/plugin marketplace add <owner>/shipyard      # GitHub shorthand
/plugin marketplace add ./path/to/shipyard    # or a local clone
/plugin install engineering-quality@shipyard-tools
```

Or from your shell:

```bash
claude plugin marketplace add ./shipyard
claude plugin install engineering-quality@shipyard-tools
claude plugin list            # shows engineering-quality@shipyard-tools, enabled
```

## 4. Namespaced invocation

Plugin components are namespaced by the plugin name, so they never collide with
your own or built-in names:

```text
/engineering-quality:change-review
/engineering-quality:change-review docs/briefs/search-and-tags.md
/engineering-quality:security-review notes_api/
/engineering-quality:security-review main..HEAD
Use the engineering-quality:security-reviewer agent to review notes_api/server.py
```

Claude Code also has a built-in `/security-review`, which reviews the branch diff
against `origin`. The namespace keeps the two apart. Claude can also pick
these skills automatically when your request matches their descriptions.

## 5. Behaviour notes

- **Hooks apply in every project where the plugin is enabled.** The post-edit hook
  only runs when the edited file is a `.py` file and a `tests/` folder exists,
  or a `dashboard/*.js` or `*.mjs` file and `dashboard/tests/` exists. Otherwise it
  does nothing. The block hook applies to every Bash call.
- **Blocking is fail-closed.** If `python3` is missing or the hook input can't be
  parsed, Bash calls are blocked with a message explaining why.
- **Plugin agents ignore `hooks`, `mcpServers`, and `permissionMode` frontmatter.**
  The security-reviewer relies on its `tools: Read, Grep, Glob` allowlist instead.
- The security-review skill forks into the built-in `Explore` agent with
  `background: false`, so its report comes back in the same turn. A forked skill
  does not see your conversation, so pass it a path or a git range.

## 6. Versioning, trust, and maintenance

- **Version pinning.** `plugin.json` sets `"version": "1.0.0"`. Users who install
  from a git-hosted marketplace stay on that version until you change the string,
  so **bump the version on every release** (semver: patch for wording fixes, minor
  for new checks or skills, major for removed components or changed hook behaviour).
  Don't also set `version` in the marketplace entry; `plugin.json` wins and
  `claude plugin validate` flags the mismatch. A marketplace added from a local
  path loads plugin files in place, so local edits apply without a bump.
- **Updates.** Users run `/plugin marketplace update shipyard-tools` or
  `claude plugin update engineering-quality@shipyard-tools`, or turn on
  auto-update for the marketplace under **Marketplaces** in `/plugin`.
- **Dependencies.** This plugin has none. If a future version needs another
  plugin, declare it in `plugin.json` `dependencies` (for example
  `{"name": "x", "version": "~1.2.0"}`) and tag releases with `claude plugin tag`.
- **Trust.** Hooks are shell scripts that run on your machine with your
  permissions every time Claude edits a file or runs a command. Before installing
  any plugin, read its `hooks/hooks.json` and the scripts it points to, check what
  its agents' `tools` allow, and prefer a pinned tag or commit for shared installs.
  Treat a plugin update like a dependency update: review the diff.
- **Maintenance.** The hook scripts are copies of `skills-pack/hooks/`. The test
  `test_plugin_copies_match_the_pack` fails if they drift, so edit the pack
  version, copy it here, and rerun the tests. Name an owner for the plugin and
  record changes in your release notes.

## 7. Distribute across teams and repositories

- **One repo, whole team:** in the project, run
  `claude plugin marketplace add <owner>/shipyard --scope project`
  once and commit the `.claude/settings.json` it writes. Teammates get the
  marketplace when they trust the folder, then install `engineering-quality@shipyard-tools`.
- **Many repos:** host the marketplace in its own git repository (it can be
  private; users need read access with stored git credentials). Every repo
  points at the same marketplace, so one version bump reaches all of them.
- **Organization-wide:** an administrator can register the marketplace and
  enable the plugin for everyone with `extraKnownMarketplaces` and
  `enabledPlugins` in managed settings, including an auto-update policy.
- **Customizing per repo:** keep repo-specific rules (protected files, extra
  checks) in each repo's `CLAUDE.md` rather than forking the plugin. Fork only
  when the workflow itself differs, and give the fork a different plugin `name`.
