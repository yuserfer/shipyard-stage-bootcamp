"""Acceptance tests for shipctl, one class per acceptance criterion."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import shipctl  # noqa: E402


class ShipctlCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "tasks.json"
        os.environ["SHIPCTL_DB"] = str(self.db)

    def tearDown(self) -> None:
        os.environ.pop("SHIPCTL_DB", None)
        self.tmp.cleanup()

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = shipctl.main(list(argv))
        return code, out.getvalue().strip(), err.getvalue().strip()

    def tasks(self) -> list[dict]:
        return json.loads(self.db.read_text())


class AddTaskTests(ShipctlCase):
    def test_add_assigns_incrementing_ids(self) -> None:
        self.assertEqual(self.run_cli("add", "Freeze API")[0], 0)
        self.assertEqual(self.run_cli("add", "Write notes")[0], 0)
        self.assertEqual([t["id"] for t in self.tasks()], [1, 2])

    def test_empty_title_is_rejected(self) -> None:
        code, _, err = self.run_cli("add", "   ")
        self.assertEqual(code, 1)
        self.assertIn("title must not be empty", err)

    def test_new_id_follows_highest_existing_id(self) -> None:
        self.run_cli("add", "a")
        self.run_cli("add", "b")
        self.run_cli("add", "c")
        self.run_cli("delete", "1")
        self.run_cli("add", "d")
        self.assertEqual([t["id"] for t in self.tasks()], [2, 3, 4])


class OwnerAndDueTests(ShipctlCase):
    def test_assign_owner(self) -> None:
        self.run_cli("add", "Tag release")
        self.assertEqual(self.run_cli("assign", "1", "maya")[0], 0)
        self.assertEqual(self.tasks()[0]["owner"], "maya")

    def test_set_valid_due_date(self) -> None:
        self.run_cli("add", "Tag release")
        self.assertEqual(self.run_cli("due", "1", "2026-11-03")[0], 0)
        self.assertEqual(self.tasks()[0]["due"], "2026-11-03")

    def test_invalid_due_date_is_rejected(self) -> None:
        self.run_cli("add", "Tag release")
        code, _, err = self.run_cli("due", "1", "03/11/2026")
        self.assertEqual(code, 1)
        self.assertIn("YYYY-MM-DD", err)

    def test_unknown_id_exits_1(self) -> None:
        code, _, err = self.run_cli("assign", "99", "maya")
        self.assertEqual(code, 1)
        self.assertIn("#99 not found", err)


class ListAndFilterTests(ShipctlCase):
    def setUp(self) -> None:
        super().setUp()
        self.run_cli("add", "Freeze API", "--owner", "maya", "--due", "2026-11-05")
        self.run_cli("add", "Write notes", "--owner", "omar", "--due", "2026-11-02")
        self.run_cli("add", "Smoke test", "--owner", "maya")
        self.run_cli("done", "1")

    def test_list_defaults_to_pending_sorted_by_due(self) -> None:
        _, out, _ = self.run_cli("list")
        self.assertEqual([line.split()[2] for line in out.splitlines()], ["#2", "#3"])

    def test_filter_by_owner(self) -> None:
        _, out, _ = self.run_cli("list", "--owner", "maya")
        self.assertIn("Smoke test", out)
        self.assertNotIn("Write notes", out)

    def test_filter_by_status_done(self) -> None:
        _, out, _ = self.run_cli("list", "--status", "done")
        self.assertIn("Freeze API", out)
        self.assertEqual(len(out.splitlines()), 1)

    def test_owner_and_status_combine(self) -> None:
        _, out, _ = self.run_cli("list", "--owner", "maya", "--status", "all")
        self.assertEqual(len(out.splitlines()), 2)

    def test_empty_list_message(self) -> None:
        _, out, _ = self.run_cli("list", "--owner", "nobody")
        self.assertEqual(out, "(no tasks)")


class CompleteAndDeleteTests(ShipctlCase):
    def test_done_marks_completed(self) -> None:
        self.run_cli("add", "Ship it")
        self.assertEqual(self.run_cli("done", "1")[0], 0)
        self.assertEqual(self.tasks()[0]["status"], "done")

    def test_delete_removes_task(self) -> None:
        self.run_cli("add", "Ship it")
        self.assertEqual(self.run_cli("delete", "1")[0], 0)
        self.assertEqual(self.tasks(), [])


class StorageTests(ShipctlCase):
    def test_corrupt_database_exits_2(self) -> None:
        self.db.write_text("{not json")
        code, _, err = self.run_cli("list")
        self.assertEqual(code, 2)
        self.assertIn("cannot read", err)


if __name__ == "__main__":
    unittest.main()
