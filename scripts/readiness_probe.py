#!/usr/bin/env python3
"""Production readiness probe: starts its own Notes API on a free port and checks runtime behaviour.

Usage: python3 scripts/readiness_probe.py   (no arguments, finishes in a few seconds)
"""

import inspect
import json
import socket
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from notes_api.server import create_server  # noqa: E402


def main() -> int:
    server = create_server(host="127.0.0.1", port=0, db_path=":memory:")
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"

    def call(method, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, dict(resp.headers), resp.read().decode()
        except urllib.error.HTTPError as err:
            return err.code, dict(err.headers), err.read().decode()

    default_host = inspect.signature(create_server).parameters["host"].default
    print(f"bind address default: {default_host}")

    status, headers, _ = call("POST", "/api/notes", {"title": "probe", "body": "<img src=x onerror=alert(1)>"})
    _, _, listing = call("GET", "/api/notes")
    print(f"stored script payload: HTTP {status}; returned unescaped: {'<img src=x onerror=' in listing}")
    print(f"CORS header: {headers.get('Access-Control-Allow-Origin', '(none)')}")

    note_id = json.loads(listing)[0]["id"]
    status, _, _ = call("DELETE", f"/api/notes/{note_id}")
    print(f"unauthenticated DELETE: HTTP {status}")

    with socket.create_connection((host, port), timeout=5) as sock:
        sock.settimeout(2)
        sock.sendall(b"POST /api/notes HTTP/1.1\r\nHost: probe\r\nContent-Type: application/json\r\n"
                     b"Content-Length: 5000000\r\n\r\n{")
        try:
            first = sock.recv(64)
            print(f"oversized Content-Length (5 MB, 1 byte sent): server answered {first[:12]!r}")
        except socket.timeout:
            print("oversized Content-Length (5 MB, 1 byte sent): no answer after 2 s, a worker thread is stuck reading")
    server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
