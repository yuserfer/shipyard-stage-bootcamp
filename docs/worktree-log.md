# Worktree log: search and tags

```sh
claude --worktree search-tags            # isolated checkout + branch worktree-search-tags
# ... Claude implements the brief inside .claude/worktrees/search-tags/ ...
cd .claude/worktrees/search-tags
python3 -m unittest discover -s tests -q  # Ran 46 tests … OK
git diff --stat main...HEAD
#  notes_api/repository.py   | note_tags table, LIKE … ESCAPE, tag filter
#  notes_api/service.py      | tag normalisation, query validation
#  notes_api/server.py       | ?q= and ?tag= parsing
#  tests/test_search_tags.py | 14 new tests
cd ../../..
git merge --no-ff worktree-search-tags -m "feat(notes): search and tags"
git worktree remove .claude/worktrees/search-tags
git branch -d worktree-search-tags
```

## Review notes
- Unexpected-change check: no files outside `notes_api/` and `tests/` changed.
- `LIKE` wildcards are escaped (`100%` and `snake_case` match literally) — covered by `test_percent_is_literal` and `test_underscore_is_literal`.
- Tags table uses `ON DELETE CASCADE` with `PRAGMA foreign_keys = ON`; `test_delete_removes_tags` proves it.
- `main` was runnable throughout: the dashboard demo kept working on the old API during the build.
