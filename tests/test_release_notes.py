"""Release notes: grouping rules, Markdown export and the HTTP endpoint."""

import sys
import unittest
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from notes_api.releases import build_release_notes, to_markdown  # noqa: E402
from notes_api.repository import NoteRepository  # noqa: E402
from notes_api.service import NoteService, ValidationError  # noqa: E402
from test_notes_api import NotesApiCase  # noqa: E402


class ReleaseNotesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = NoteService(NoteRepository(":memory:"))
        add = lambda title, tags, body="": self.service.create({"title": title, "body": body, "tags": tags})  # noqa: E731
        add("Search endpoint", ["release:v1.4", "backend"], "GET /api/notes?q=\nmore detail")
        add("Overdue badge", ["release:v1.4", "dashboard"])
        add("Rollback plan", ["release:v1.4", "ops", "backend"])
        add("Typo fixes", ["release:v1.4"])
        add("Next release idea", ["release:v1.5", "backend"])

    def test_groups_by_first_matching_section_in_fixed_order(self) -> None:
        release = build_release_notes(self.service, "v1.4")
        self.assertEqual(release["count"], 4)
        layout = [(s["key"], [n["title"] for n in s["notes"]]) for s in release["sections"]]
        self.assertEqual(layout, [
            ("backend", ["Search endpoint", "Rollback plan"]),
            ("dashboard", ["Overdue badge"]),
            ("other", ["Typo fixes"]),
        ])

    def test_other_versions_are_excluded(self) -> None:
        self.assertEqual(build_release_notes(self.service, "v1.5")["count"], 1)

    def test_unknown_version_is_empty(self) -> None:
        self.assertEqual(build_release_notes(self.service, "v2.0"), {"version": "v2.0", "count": 0, "sections": []})

    def test_invalid_version_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            build_release_notes(self.service, "latest")

    def test_markdown_uses_first_body_line(self) -> None:
        md = to_markdown(build_release_notes(self.service, "v1.4"))
        self.assertTrue(md.startswith("# Release v1.4\n"))
        self.assertIn("- **Search endpoint**: GET /api/notes?q=\n", md)
        self.assertNotIn("more detail", md)

    def test_markdown_for_empty_release(self) -> None:
        self.assertIn("No notes tagged", to_markdown(build_release_notes(self.service, "v3.0")))


class ReleaseNotesHttpTests(NotesApiCase):
    def test_json_and_markdown_endpoints(self) -> None:
        self.call("POST", "/api/notes", {"title": "Search", "tags": ["release:v1.4", "backend"]})
        status, release = self.call("GET", "/api/releases/v1.4/notes")
        self.assertEqual((status, release["count"]), (200, 1))
        with urllib.request.urlopen(self.base + "/api/releases/v1.4/notes?format=markdown") as resp:
            self.assertEqual(resp.headers["Content-Type"], "text/markdown; charset=utf-8")
            self.assertIn("## Backend", resp.read().decode())

    def test_invalid_version_is_400(self) -> None:
        self.assertEqual(self.call("GET", "/api/releases/latest/notes")[0], 400)


if __name__ == "__main__":
    unittest.main()
