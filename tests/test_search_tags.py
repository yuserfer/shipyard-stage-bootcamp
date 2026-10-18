"""Search and tagging: service rules plus the HTTP query interface."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from notes_api.repository import NoteRepository  # noqa: E402
from notes_api.service import NoteService, ValidationError  # noqa: E402
from test_notes_api import NotesApiCase  # noqa: E402


class TagRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = NoteService(NoteRepository(":memory:"))

    def test_tags_are_normalized_sorted_and_deduplicated(self) -> None:
        note = self.service.create({"title": "t", "tags": ["Release:v1.4", "backend", "BACKEND "]})
        self.assertEqual(note["tags"], ["backend", "release:v1.4"])

    def test_invalid_tag_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create({"title": "t", "tags": ["has space"]})

    def test_too_many_tags_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create({"title": "t", "tags": [f"t{i}" for i in range(11)]})

    def test_patch_without_tags_keeps_tags(self) -> None:
        note = self.service.create({"title": "t", "tags": ["ops"]})
        self.assertEqual(self.service.update(note["id"], {"title": "u"})["tags"], ["ops"])

    def test_patch_tags_replaces_set(self) -> None:
        note = self.service.create({"title": "t", "tags": ["ops"]})
        self.assertEqual(self.service.update(note["id"], {"tags": ["qa"]})["tags"], ["qa"])

    def test_delete_removes_tags(self) -> None:
        note = self.service.create({"title": "t", "tags": ["ops"]})
        self.service.delete(note["id"])
        self.assertEqual(self.service.list(tag="ops"), [])


class SearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = NoteService(NoteRepository(":memory:"))
        self.service.create({"title": "Deploy checklist", "body": "Run smoke tests", "tags": ["ops"]})
        self.service.create({"title": "API freeze", "body": "No breaking DEPLOY changes", "tags": ["backend"]})
        self.service.create({"title": "Coverage at 100%", "body": "", "tags": ["qa"]})
        self.service.create({"title": "snake_case names", "body": "", "tags": []})

    def titles(self, **kw) -> list[str]:
        return sorted(n["title"] for n in self.service.list(**kw))

    def test_search_title_and_body_case_insensitive(self) -> None:
        self.assertEqual(self.titles(q="deploy"), ["API freeze", "Deploy checklist"])

    def test_percent_is_literal(self) -> None:
        self.assertEqual(self.titles(q="100%"), ["Coverage at 100%"])

    def test_underscore_is_literal(self) -> None:
        self.assertEqual(self.titles(q="e_c"), ["snake_case names"])

    def test_filter_by_tag_case_insensitive(self) -> None:
        self.assertEqual(self.titles(tag="OPS"), ["Deploy checklist"])

    def test_search_and_tag_combine(self) -> None:
        self.assertEqual(self.titles(q="deploy", tag="backend"), ["API freeze"])

    def test_query_too_long_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.list(q="x" * 101)


class SearchHttpTests(NotesApiCase):
    def test_query_parameters(self) -> None:
        self.call("POST", "/api/notes", {"title": "Deploy plan", "tags": ["ops"]})
        self.call("POST", "/api/notes", {"title": "Retro", "tags": ["team"]})
        status, notes = self.call("GET", "/api/notes?q=deploy%20plan&tag=ops")
        self.assertEqual(status, 200)
        self.assertEqual([n["title"] for n in notes], ["Deploy plan"])

    def test_invalid_tag_query_is_400(self) -> None:
        self.assertEqual(self.call("GET", "/api/notes?tag=bad%20tag")[0], 400)


if __name__ == "__main__":
    unittest.main()
