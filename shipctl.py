#!/usr/bin/env python3
"""shipctl: a zero-dependency CLI for release tasks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

EXIT_OK, EXIT_USAGE, EXIT_IO = 0, 1, 2
STATUSES = ("pending", "done", "all")


class UserError(Exception):
    """Bad input from the user: exit code 1."""


def _db_path() -> Path:
    return Path(os.environ.get("SHIPCTL_DB", "tasks.json"))


def _load() -> list[dict[str, Any]]:
    path = _db_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "[]")
    except (OSError, json.JSONDecodeError) as exc:
        raise OSError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, list):
        raise OSError(f"{path} must contain a JSON list")
    return data


def _save(tasks: list[dict[str, Any]]) -> None:
    path = _db_path()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _next_id(tasks: list[dict[str, Any]]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1


def _find(tasks: list[dict[str, Any]], task_id: int) -> dict[str, Any]:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise UserError(f"task #{task_id} not found")


def _parse_due(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise UserError(f"invalid due date {value!r}: use YYYY-MM-DD") from exc


def _fmt(task: dict[str, Any]) -> str:
    mark = "x" if task["status"] == "done" else " "
    owner = task.get("owner") or "-"
    due = task.get("due") or "-"
    return f"[{mark}] #{task['id']:<3} {task['title']:<40} owner={owner:<10} due={due}"


def cmd_add(args: argparse.Namespace) -> str:
    title = args.title.strip()
    if not title:
        raise UserError("title must not be empty")
    tasks = _load()
    task = {
        "id": _next_id(tasks),
        "title": title,
        "owner": args.owner,
        "due": _parse_due(args.due),
        "status": "pending",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    tasks.append(task)
    _save(tasks)
    return f"Added #{task['id']}: {title}"


def cmd_assign(args: argparse.Namespace) -> str:
    tasks = _load()
    task = _find(tasks, args.id)
    task["owner"] = args.owner
    _save(tasks)
    return f"Assigned #{args.id} to {args.owner}"


def cmd_due(args: argparse.Namespace) -> str:
    tasks = _load()
    task = _find(tasks, args.id)
    task["due"] = _parse_due(args.date)
    _save(tasks)
    return f"Due date of #{args.id} set to {task['due']}"


def cmd_list(args: argparse.Namespace) -> str:
    tasks = _load()
    rows = [
        t
        for t in tasks
        if (args.status == "all" or t["status"] == args.status)
        and (args.owner is None or t.get("owner") == args.owner)
    ]
    rows.sort(key=lambda t: (t.get("due") or "9999-12-31", t["id"]))
    return "\n".join(_fmt(t) for t in rows) if rows else "(no tasks)"


def cmd_done(args: argparse.Namespace) -> str:
    tasks = _load()
    task = _find(tasks, args.id)
    task["status"] = "done"
    _save(tasks)
    return f"Completed #{args.id}"


def cmd_delete(args: argparse.Namespace) -> str:
    tasks = _load()
    task = _find(tasks, args.id)
    tasks.remove(task)
    _save(tasks)
    return f"Deleted #{args.id}"


def cmd_stats(args: argparse.Namespace) -> str:
    tasks = _load()
    if not tasks:
        return "(no tasks)"
    today = date.today().isoformat()
    owners: dict[str, dict[str, int]] = {}
    for task in tasks:
        row = owners.setdefault(task.get("owner") or "-", {"pending": 0, "done": 0, "overdue": 0})
        row[task["status"]] += 1
        if task["status"] == "pending" and task.get("due") and task["due"] < today:
            row["overdue"] += 1
    lines = [f"{'owner':<10} {'pending':>7} {'done':>5} {'overdue':>7}"]
    for owner in sorted(owners):
        r = owners[owner]
        lines.append(f"{owner:<10} {r['pending']:>7} {r['done']:>5} {r['overdue']:>7}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shipctl", description="Release task manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="add a release task")
    p.add_argument("title")
    p.add_argument("--owner")
    p.add_argument("--due", help="YYYY-MM-DD")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("assign", help="assign an owner")
    p.add_argument("id", type=int)
    p.add_argument("owner")
    p.set_defaults(func=cmd_assign)

    p = sub.add_parser("due", help="set a due date")
    p.add_argument("id", type=int)
    p.add_argument("date", help="YYYY-MM-DD")
    p.set_defaults(func=cmd_due)

    p = sub.add_parser("list", help="list tasks (pending by default)")
    p.add_argument("--owner")
    p.add_argument("--status", choices=STATUSES, default="pending")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("stats", help="pending, done and overdue counts per owner")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("done", help="mark a task as completed")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_done)

    p = sub.add_parser("delete", help="delete a task")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_delete)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_OK if exc.code == 0 else EXIT_USAGE
    try:
        print(args.func(args))
        return EXIT_OK
    except UserError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_IO


if __name__ == "__main__":
    sys.exit(main())
