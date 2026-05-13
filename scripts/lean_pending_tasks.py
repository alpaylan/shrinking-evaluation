#!/usr/bin/env python3
"""
Emit a GitHub Actions matrix JSON listing (mutation, property) tasks
in `store.<workload>.det.jsonl` that have at least one `timed_out`
row and no `Failed` row — i.e. tasks Lean has not yet solved.

Usage:
  python3 scripts/lean_pending_tasks.py <workload>   # workload = rbt|bst|...

Output (stdout, single line):
  {"include": [{"mutation": "...", "property": "..."}, ...]}

Designed for consumption by `strategy.matrix: ${{ fromJson(...) }}` in
.github/workflows/lean-incremental.yml.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def pending(workload: str):
    store = ROOT / f"store.{workload}.det.jsonl"
    if not store.exists():
        return []
    state = defaultdict(lambda: {"failed": False, "timeout": False})
    for line in store.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)["data"]
        key = (r["property"], ",".join(r.get("mutations", []) or []))
        if r["status"] == "Failed":
            state[key]["failed"] = True
        elif r["status"] == "timed_out":
            state[key]["timeout"] = True
    return sorted(
        (
            {"property": p, "mutation": m}
            for (p, m), v in state.items()
            if v["timeout"] and not v["failed"]
        ),
        key=lambda t: (t["mutation"], t["property"]),
    )


if __name__ == "__main__":
    workload = sys.argv[1] if len(sys.argv) > 1 else "rbt"
    print(json.dumps({"include": pending(workload)}))
