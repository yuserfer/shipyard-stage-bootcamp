"""HTTP layer: routing and JSON translation only."""

from __future__ import annotations

import json
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .repository import NoteRepository
from .service import NoteService, NotFound, ValidationError
from .releases import build_release_notes, to_markdown
from .tasks_source import load_tasks

NOTE_PATH = re.compile(r"^/api/notes/(\d+)$")
RELEASE_PATH = re.compile(r"^/api/releases/([^/]+)/notes$")
DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"


def make_handler(service: NoteService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ShipyardNotes/1.0"

        def log_message(self, fmt: str, *args: Any) -> None:
            if os.environ.get("NOTES_API_LOG"):
                super().log_message(fmt, *args)

        def _send(self, status: int, payload: Any = None) -> None:
            body = b"" if payload is None else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _static(self, path: str) -> None:
            rel = "index.html" if path in ("", "/") else path.lstrip("/")
            target = (DASHBOARD_DIR / rel).resolve()
            if DASHBOARD_DIR not in target.parents or not target.is_file():
                return self._send(HTTPStatus.NOT_FOUND, {"error": f"no file {path}"})
            data = target.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _text(self, status: int, text: str, content_type: str) -> None:
            data = text.encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw or b"{}")
            except json.JSONDecodeError as exc:
                raise ValidationError("request body must be valid JSON") from exc
            if not isinstance(data, dict):
                raise ValidationError("request body must be a JSON object")
            return data

        def _dispatch(self, method: str) -> None:
            url = urlsplit(self.path)
            path = url.path
            query = {k: v[0] for k, v in parse_qs(url.query).items()}
            try:
                if path == "/api/health" and method == "GET":
                    return self._send(HTTPStatus.OK, {"status": "ok"})
                if path == "/api/tasks" and method == "GET":
                    return self._send(HTTPStatus.OK, load_tasks())
                release = RELEASE_PATH.match(path)
                if release and method == "GET":
                    notes = build_release_notes(service, release.group(1))
                    if query.get("format") == "markdown":
                        return self._text(HTTPStatus.OK, to_markdown(notes), "text/markdown; charset=utf-8")
                    return self._send(HTTPStatus.OK, notes)
                if path == "/api/notes":
                    if method == "GET":
                        return self._send(HTTPStatus.OK, service.list(q=query.get("q"), tag=query.get("tag")))
                    if method == "POST":
                        return self._send(HTTPStatus.CREATED, service.create(self._json_body()))
                match = NOTE_PATH.match(path)
                if match:
                    note_id = int(match.group(1))
                    if method == "GET":
                        return self._send(HTTPStatus.OK, service.get(note_id))
                    if method == "PATCH":
                        return self._send(HTTPStatus.OK, service.update(note_id, self._json_body()))
                    if method == "DELETE":
                        service.delete(note_id)
                        return self._send(HTTPStatus.NO_CONTENT)
                if method == "GET" and not path.startswith("/api/"):
                    return self._static(path)
                self._send(HTTPStatus.NOT_FOUND, {"error": f"no route for {method} {path}"})
            except ValidationError as exc:
                self._send(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            except NotFound as exc:
                self._send(HTTPStatus.NOT_FOUND, {"error": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._send(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": repr(exc)})

        def do_GET(self) -> None:
            self._dispatch("GET")

        def do_POST(self) -> None:
            self._dispatch("POST")

        def do_PATCH(self) -> None:
            self._dispatch("PATCH")

        def do_DELETE(self) -> None:
            self._dispatch("DELETE")

    return Handler


def create_server(host: str = "0.0.0.0", port: int = 8000, db_path: str = "notes.db") -> ThreadingHTTPServer:
    service = NoteService(NoteRepository(db_path))
    return ThreadingHTTPServer((host, port), make_handler(service))


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    server = create_server(port=port, db_path=os.environ.get("NOTES_DB", "notes.db"))
    print(f"Shipyard dashboard on http://localhost:{port}/  (API under /api/)")
    server.serve_forever()


if __name__ == "__main__":
    main()
