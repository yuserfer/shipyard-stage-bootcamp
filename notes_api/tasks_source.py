"""Read-only access to shipctl's task file for the dashboard."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def load_tasks() -> list[dict[str, Any]]:
    path = Path(os.environ.get("SHIPCTL_DB", "tasks.json"))
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8") or "[]")
    return data if isinstance(data, list) else []
