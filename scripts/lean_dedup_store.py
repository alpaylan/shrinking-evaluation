#!/usr/bin/env python3
"""
Dedupe a store.<workload>.det.jsonl in place by
(strategy, property, mutations, trial), keeping the last occurrence.

Matches etna's own per-trial dedup semantic so a master store grown
across many CI runs stays consistent.
"""

import json
import sys
from collections import OrderedDict
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: lean_dedup_store.py <path-to-store.jsonl>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"no such file: {path}", file=sys.stderr)
        return 1

    keep: "OrderedDict[tuple, str]" = OrderedDict()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        d = r["data"]
        k = (
            d["strategy"],
            d["property"],
            tuple(d.get("mutations", []) or []),
            d.get("trial"),
        )
        keep[k] = line

    path.write_text("\n".join(keep.values()) + "\n")
    print(f"kept {len(keep)} rows in {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
