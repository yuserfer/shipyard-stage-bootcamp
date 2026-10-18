"""End-to-end tests: a real server on an ephemeral port, real HTTP requests."""

import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from notes_api.server import create_server  # noqa: E402


class NotesApiCase(unittest.TestCase):
    def setUp(self) -> None:
        self.server = create_server(host="127.0.0.1", port=0, db_path=":memory:")
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def call(self, method: str, path: str, payload=None, raw: bytes | None = None):
        data = raw if raw is not None else (json.dumps(payload).encode() if payload is not None else None)
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read()
                return resp.status, json.loads(body) if body else None
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read() or b"null")

    def create(self, title="Release v1.4", body="Ship on Tuesday"):
        status, note = self.call("POST", "/api/notes", {"title": title, "body": body})
        self.assertEqual(status, 201)
        return note


class CrudTests(NotesApiCase):
    def test_health(self) -> None:
        self.assertEqual(self.call("GET", "/api/health"), (200, {"status": "ok"}))

    def test_create_returns_201_and_note(self) -> None:
        note = self.create()
        self.assertEqual(note["title"], "Release v1.4")
        self.assertEqual(note["body"], "Ship on Tuesday")
        self.assertIn("created_at", note)

    def test_get_and_list(self) -> None:
        first = self.create("one")
        second = self.create("two")
        self.assertEqual(self.call("GET", f"/api/notes/{first['id']}")[1]["title"], "one")
        titles = [n["title"] for n in self.call("GET", "/api/notes")[1]]
        self.assertEqual(titles, ["two", "one"])
        self.assertEqual(second["id"], first["id"] + 1)

    def test_patch_both_fields(self) -> None:
        note = self.create()
        status, updated = self.call("PATCH", f"/api/notes/{note['id']}", {"title": "v1.5", "body": "Moved"})
        self.assertEqual(status, 200)
        self.assertEqual((updated["title"], updated["body"]), ("v1.5", "Moved"))

    def test_delete_then_404(self) -> None:
        note = self.create()
        self.assertEqual(self.call("DELETE", f"/api/notes/{note['id']}"), (204, None))
        self.assertEqual(self.call("GET", f"/api/notes/{note['id']}")[0], 404)


class ValidationTests(NotesApiCase):
    def test_missing_title_is_400(self) -> None:
        status, err = self.call("POST", "/api/notes", {"body": "no title"})
        self.assertEqual(status, 400)
        self.assertIn("title", err["error"])

    def test_title_too_long_is_400(self) -> None:
        self.assertEqual(self.call("POST", "/api/notes", {"title": "x" * 121})[0], 400)

    def test_invalid_json_is_400(self) -> None:
        self.assertEqual(self.call("POST", "/api/notes", raw=b"{oops")[0], 400)

    def test_unknown_note_is_404(self) -> None:
        self.assertEqual(self.call("PATCH", "/api/notes/999", {"title": "x"})[0], 404)

    def test_unknown_route_is_404(self) -> None:
        self.assertEqual(self.call("GET", "/api/nope")[0], 404)


if __name__ == "__main__":
    unittest.main()
