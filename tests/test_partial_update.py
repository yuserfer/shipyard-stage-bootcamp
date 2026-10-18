"""Regression tests for BUG-101: PATCH with only a title erased the note body."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from notes_api.repository import NoteRepository  # noqa: E402
from notes_api.service import NoteService, ValidationError  # noqa: E402


class PartialUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = NoteService(NoteRepository(":memory:"))
        self.note = self.service.create({"title": "Release v1.4", "body": "Rollback plan: redeploy v1.3"})

    def test_title_only_patch_keeps_body(self) -> None:
        updated = self.service.update(self.note["id"], {"title": "Release v1.4.1"})
        self.assertEqual(updated["title"], "Release v1.4.1")
        self.assertEqual(updated["body"], "Rollback plan: redeploy v1.3")

    def test_body_only_patch_keeps_title(self) -> None:
        updated = self.service.update(self.note["id"], {"body": "Rollback plan: feature flag"})
        self.assertEqual(updated["title"], "Release v1.4")

    def test_explicit_empty_body_is_allowed(self) -> None:
        updated = self.service.update(self.note["id"], {"body": ""})
        self.assertEqual(updated["body"], "")

    def test_empty_patch_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.update(self.note["id"], {})

    def test_updated_at_changes(self) -> None:
        updated = self.service.update(self.note["id"], {"title": "Release v1.4.1"})
        self.assertGreater(updated["updated_at"], self.note["updated_at"])


if __name__ == "__main__":
    unittest.main()
