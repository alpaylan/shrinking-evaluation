#!/usr/bin/env python3
"""
Emit a single-task test JSON suitable for `etna experiment run --tests`.

Picks the matching (mutation, property) group out of the canonical
`tests/<workload>-haskell-lean.json` and writes a minimal one-task,
one-trial variant to `tests/<out-name>.json`. The output filename is
what you pass to `etna experiment run --tests`.

Usage:
  python3 scripts/lean_compose_task.py \\
    --workload rbt \\
    --mutation swap_bc \\
    --property DeleteDelete \\
    --timeout 17400 \\
    --out-name lean-rbt-swap_bc-DeleteDelete
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", required=True)
    ap.add_argument("--mutation", required=True)
    ap.add_argument("--property", required=True)
    ap.add_argument("--timeout", type=float, default=14400.0)
    ap.add_argument("--out-name", required=True)
    args = ap.parse_args()

    src = ROOT / "tests" / f"{args.workload}-haskell-lean.json"
    groups = json.loads(src.read_text())

    match = None
    for grp in groups:
        if grp["mutations"] == [args.mutation]:
            for t in grp["tasks"]:
                if t["property"] == args.property:
                    match = (grp, t)
                    break
        if match:
            break
    if match is None:
        print(
            f"no task ({args.mutation}, {args.property}) in {src}", file=sys.stderr
        )
        return 1
    grp, task = match
    out = [
        {
            "workload": grp["workload"],
            "trials": 1,
            "timeout": args.timeout,
            "mutations": grp["mutations"],
            "mode": "Solve",
            "params": None,
            "tasks": [task],
        }
    ]
    dst = ROOT / "tests" / f"{args.out_name}.json"
    dst.write_text(json.dumps(out, indent=2))
    print(str(dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
