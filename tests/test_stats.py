"""`shipctl stats`: per-owner pending, done and overdue counts."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_shipctl import ShipctlCase  # noqa: E402


class StatsTests(ShipctlCase):
    def test_empty_database_message(self) -> None:
        self.assertEqual(self.run_cli("stats"), (0, "(no tasks)", ""))

    def test_counts_per_owner_with_overdue(self) -> None:
        self.run_cli("add", "Freeze API", "--owner", "maya", "--due", "2000-01-01")
        self.run_cli("add", "Tag build", "--owner", "maya")
        self.run_cli("add", "Write notes", "--owner", "omar", "--due", "2000-01-01")
        self.run_cli("add", "Smoke test")
        self.run_cli("done", "3")
        code, out, _ = self.run_cli("stats")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), [
            "owner      pending  done overdue",
            "-                1     0       0",
            "maya             2     0       1",
            "omar             0     1       0",
        ])


if __name__ == "__main__":
    unittest.main()
