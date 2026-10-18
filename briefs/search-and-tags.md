# Engineering brief: search and tags (isolated in a worktree)

## Outcome
Engineers can find notes by text and group them with tags, without destabilising `main` while the feature is built.

## Scope
- `tags`: optional list of strings on create and PATCH; normalised to lowercase, unique, sorted; `[a-z0-9][a-z0-9:._-]{0,29}`; max 10 per note. PATCH without `tags` keeps existing tags.
- `GET /api/notes?q=<text>`: case-insensitive substring match on title **or** body. `%` and `_` must match literally.
- `GET /api/notes?tag=<tag>`: notes with that tag. `q` and `tag` combine with AND.
- Invalid tag or query longer than 100 characters → `400`.

## Isolation rules
1. Start a worktree session: `claude --worktree search-tags` (branch `worktree-search-tags` under `.claude/worktrees/`).
2. All edits happen in the worktree. `main` stays untouched and runnable.
3. Before merging, the human reviews `git diff main...worktree-search-tags`, runs the full test suite in the worktree, and inspects any file outside `notes_api/` and `tests/`.
4. Merge with a focused commit message. Remove the worktree afterwards.

## Constraints
- Standard library only. Keep the layering: SQL only in `repository.py`, rules only in `service.py`.
- Existing tests must pass unchanged.
