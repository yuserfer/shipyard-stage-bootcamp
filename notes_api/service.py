"""Business rules for notes: validation, tags and partial updates. No HTTP, no SQL."""

from __future__ import annotations

import re
from typing import Any

from .repository import NoteRepository

MAX_TITLE = 120
MAX_BODY = 10_000
MAX_TAGS = 10
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9:._-]{0,29}$")


class ValidationError(ValueError):
    """Input violates a business rule (HTTP 400)."""


class NotFound(LookupError):
    """The note does not exist (HTTP 404)."""


def _title(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("title is required")
    value = value.strip()
    if len(value) > MAX_TITLE:
        raise ValidationError(f"title must be at most {MAX_TITLE} characters")
    return value


def _body(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValidationError("body must be a string")
    if len(value) > MAX_BODY:
        raise ValidationError(f"body must be at most {MAX_BODY} characters")
    return value


def normalize_tag(value: Any) -> str:
    if not isinstance(value, str):
        raise ValidationError("tags must be strings")
    tag = value.strip().lower()
    if not TAG_RE.match(tag):
        raise ValidationError(f"invalid tag {value!r}: use a-z, 0-9, ':', '.', '_', '-' (max 30)")
    return tag


def _tags(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValidationError("tags must be a list of strings")
    tags = sorted({normalize_tag(v) for v in value})
    if len(tags) > MAX_TAGS:
        raise ValidationError(f"at most {MAX_TAGS} tags per note")
    return tags


class NoteService:
    def __init__(self, repo: NoteRepository) -> None:
        self.repo = repo

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        return self.repo.create(_title(data.get("title")), _body(data.get("body")), _tags(data.get("tags")))

    def get(self, note_id: int) -> dict[str, Any]:
        note = self.repo.get(note_id)
        if note is None:
            raise NotFound(f"note {note_id} not found")
        return note

    def list(self, q: str | None = None, tag: str | None = None) -> list[dict[str, Any]]:
        q = q.strip() if q else None
        if q and len(q) > 100:
            raise ValidationError("search query must be at most 100 characters")
        return self.repo.list(q=q or None, tag=normalize_tag(tag) if tag else None)

    def update(self, note_id: int, data: dict[str, Any]) -> dict[str, Any]:
        current = self.get(note_id)
        if not {"title", "body", "tags"} & data.keys():
            raise ValidationError("provide title, body and/or tags")
        title = _title(data["title"]) if "title" in data else current["title"]
        body = _body(data["body"]) if "body" in data else current["body"]
        tags = _tags(data["tags"]) if "tags" in data else current["tags"]
        note = self.repo.update(note_id, title, body, tags)
        if note is None:
            raise NotFound(f"note {note_id} not found")
        return note

    def delete(self, note_id: int) -> None:
        if not self.repo.delete(note_id):
            raise NotFound(f"note {note_id} not found")
