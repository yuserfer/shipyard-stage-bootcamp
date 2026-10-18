"""SQLite persistence for notes and tags. The only module that writes SQL."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    body       TEXT    NOT NULL DEFAULT '',
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS note_tags (
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag     TEXT    NOT NULL,
    PRIMARY KEY (note_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_note_tags_tag ON note_tags(tag);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _like_pattern(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class NoteRepository:
    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock, self._conn:
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.executescript(SCHEMA)

    def _hydrate(self, rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
        notes = [dict(r) for r in rows]
        if not notes:
            return notes
        ids = [n["id"] for n in notes]
        marks = ",".join("?" * len(ids))
        tags: dict[int, list[str]] = {i: [] for i in ids}
        for row in self._conn.execute(
            f"SELECT note_id, tag FROM note_tags WHERE note_id IN ({marks}) ORDER BY tag", ids
        ):
            tags[row["note_id"]].append(row["tag"])
        for note in notes:
            note["tags"] = tags[note["id"]]
        return notes

    def _replace_tags(self, note_id: int, tags: list[str]) -> None:
        self._conn.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
        self._conn.executemany(
            "INSERT INTO note_tags (note_id, tag) VALUES (?, ?)", [(note_id, t) for t in tags]
        )

    def _fetch(self, note_id: int) -> dict[str, Any] | None:
        rows = self._conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchall()
        notes = self._hydrate(rows)
        return notes[0] if notes else None

    def create(self, title: str, body: str, tags: list[str]) -> dict[str, Any]:
        now = _now()
        with self._lock, self._conn:
            cur = self._conn.execute(
                "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (title, body, now, now),
            )
            self._replace_tags(cur.lastrowid, tags)
            return self._fetch(cur.lastrowid)

    def get(self, note_id: int) -> dict[str, Any] | None:
        with self._lock:
            return self._fetch(note_id)

    def list(self, q: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM notes WHERE 1 = 1"
        params: list[Any] = []
        if q:
            sql += " AND (title LIKE ? ESCAPE '\\' COLLATE NOCASE OR body LIKE ? ESCAPE '\\' COLLATE NOCASE)"
            params += [_like_pattern(q)] * 2
        if tag:
            sql += " AND id IN (SELECT note_id FROM note_tags WHERE tag = ?)"
            params.append(tag)
        sql += " ORDER BY updated_at DESC, id DESC"
        with self._lock:
            return self._hydrate(self._conn.execute(sql, params).fetchall())

    def update(self, note_id: int, title: str, body: str, tags: list[str]) -> dict[str, Any] | None:
        with self._lock, self._conn:
            cur = self._conn.execute(
                "UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
                (title, body, _now(), note_id),
            )
            if cur.rowcount == 0:
                return None
            self._replace_tags(note_id, tags)
            return self._fetch(note_id)

    def delete(self, note_id: int) -> bool:
        with self._lock, self._conn:
            cur = self._conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cur.rowcount > 0
