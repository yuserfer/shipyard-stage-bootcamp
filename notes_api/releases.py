"""Release notes: notes tagged `release:<version>`, grouped into changelog sections."""

from __future__ import annotations

import re
from typing import Any

from .service import NoteService, ValidationError

VERSION_RE = re.compile(r"^v\d+\.\d+(\.\d+)?$")
SECTIONS = [
    ("backend", "Backend"),
    ("dashboard", "Dashboard"),
    ("ops", "Operations"),
    ("qa", "Quality"),
    ("decision", "Decisions"),
]
OTHER = ("other", "Other changes")


def build_release_notes(service: NoteService, version: str) -> dict[str, Any]:
    if not VERSION_RE.match(version):
        raise ValidationError(f"invalid version {version!r}: use v<major>.<minor>[.<patch>]")
    notes = sorted(service.list(tag=f"release:{version}"), key=lambda n: n["id"])
    sections = []
    used: set[int] = set()
    for key, title in SECTIONS:
        items = [n for n in notes if key in n["tags"] and n["id"] not in used]
        used.update(n["id"] for n in items)
        if items:
            sections.append({"key": key, "title": title, "notes": items})
    rest = [n for n in notes if n["id"] not in used]
    if rest:
        sections.append({"key": OTHER[0], "title": OTHER[1], "notes": rest})
    return {"version": version, "count": len(notes), "sections": sections}


def to_markdown(release: dict[str, Any]) -> str:
    lines = [f"# Release {release['version']}", ""]
    if not release["sections"]:
        lines.append("_No notes tagged for this release yet._")
    for section in release["sections"]:
        lines += [f"## {section['title']}", ""]
        lines += [f"- **{n['title']}**" + (f": {n['body'].splitlines()[0]}" if n["body"] else "") for n in section["notes"]]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
