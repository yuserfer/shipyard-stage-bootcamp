#!/usr/bin/env python3
"""Load realistic demo data: release tasks (tasks.json) and engineering notes (notes.db)."""

from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from notes_api.repository import NoteRepository
from notes_api.service import NoteService

TODAY = date.today()


def day(offset: int) -> str:
    return (TODAY + timedelta(days=offset)).isoformat()


TASKS = [
    ("Freeze public API for v1.4", "maya", day(-3), "done"),
    ("Write v1.4 release notes", "omar", day(2), "pending"),
    ("Run load test on Notes API", "li", day(-1), "pending"),
    ("Rotate staging credentials", "maya", day(-2), "pending"),
    ("Update onboarding guide", "omar", day(6), "pending"),
    ("Tag release candidate", "li", day(1), "pending"),
    ("Smoke test dashboard on mobile", None, None, "pending"),
    ("Close v1.3 retro actions", "maya", day(-6), "done"),
]

NOTES = [
    ("Rollback plan for v1.4", "Redeploy **v1.3.2** from the release branch; feature flag `notes-search` off.", ["release:v1.4", "ops"]),
    ("Search uses SQLite LIKE", "Wildcards are escaped, so `100%` matches literally. **No FTS yet.**", ["backend", "decision"]),
    ("Dashboard browser check", "Verified in Chrome at 1280px and 390px. Console clean.", ["qa", "release:v1.4"]),
    ("On-call handoff", "Pager rotation starts Monday. Runbook lives in docs/runbook.md.", ["ops"]),
    ("API freeze exception", "PATCH /api/notes accepts `tags` (approved by the tech lead).", ["backend", "release:v1.4"]),
]


def main() -> int:
    tasks_path = Path(os.environ.get("SHIPCTL_DB", "tasks.json"))
    db_path = os.environ.get("NOTES_DB", "notes.db")
    if "--force" not in sys.argv and (tasks_path.exists() or Path(db_path).exists()):
        print("tasks.json or notes.db already exists; pass --force to replace them")
        return 1
    tasks = [
        {"id": i, "title": t, "owner": o, "due": d, "status": s, "created": f"{day(-10)}T09:00:00+00:00"}
        for i, (t, o, d, s) in enumerate(TASKS, start=1)
    ]
    tasks_path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    Path(db_path).unlink(missing_ok=True)
    service = NoteService(NoteRepository(db_path))
    for title, body, tags in NOTES:
        service.create({"title": title, "body": body, "tags": tags})
    print(f"Seeded {len(TASKS)} tasks into {tasks_path} and {len(NOTES)} notes into {db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
