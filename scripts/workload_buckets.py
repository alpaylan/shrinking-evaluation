#!/usr/bin/env python3
"""Per-family bug-finding bucket charts for any workload.

Produces `figures/bucket_<workload>_family-<fam>.{json,png}` using the
ETNA `experiment visualize-json` renderer. Defaults to the workload's
'default' shrink mode; pass --mode to override.

Usage:
  scripts/workload_buckets.py --workload {bst,rbt,stlc,fsub} [--mode default]
"""

import argparse
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import median

from workload_config import ROOT, COLORS, HATCHED, display_name, get_config

# Time buckets (seconds), bottom-to-top of stack.
BUCKETS = [
    ("< 0.1s",  0.0,   0.1),
    ("< 1s",    0.1,   1.0),
    ("< 10s",   1.0,   10.0),
    ("< 60s",  10.0,   60.0),
    ("≥ 60s",  60.0, float("inf")),
]
NUM_BUCKETS = len(BUCKETS) + 1  # +1 for "Not Found"


def load(path: Path):
    if not path.exists():
        return []
    return [json.loads(l)["data"]
            for l in path.read_text().splitlines() if l.strip()]


def task_key(r):
    return (r["property"], ",".join(r.get("mutations", []) or []))


def task_bucket(trials):
    if any(r["status"] != "Failed" for r in trials):
        return NUM_BUCKETS - 1
    times = [r["time_pre_failure"] for r in trials
             if r.get("time_pre_failure") is not None]
    if not times:
        return NUM_BUCKETS - 1
    t = median(times)
    for i, (_, lo, hi) in enumerate(BUCKETS):
        if lo <= t < hi:
            return i
    return len(BUCKETS) - 1


def counts_for(rows, strategy):
    by_task = defaultdict(list)
    for r in rows:
        if r["strategy"] == strategy:
            by_task[task_key(r)].append(r)
    counts = [0] * NUM_BUCKETS
    for trials in by_task.values():
        counts[task_bucket(trials)] += 1
    return counts


def build_spec(rows, strategies):
    chart_names, chart_colors, bar_styles, bucket_values = [], [], [], []
    for s in strategies:
        counts = counts_for(rows, s)
        if sum(counts) == 0:
            continue
        chart_names.append(display_name(s))
        chart_colors.append(COLORS.get(s, "#000000"))
        bar_styles.append("hatched" if s in HATCHED else "solid")
        bucket_values.append([str(c) for c in counts])
    return {
        "numBuckets": NUM_BUCKETS,
        "chartNames": chart_names,
        "chartColors": chart_colors,
        "barStyles": bar_styles,
        "bucketValues": bucket_values,
    }


def render(spec, json_path, png_path):
    json_path.write_text(json.dumps(spec, indent=2))
    print(f"  wrote {json_path.name} ({len(spec['chartNames'])} strategies)")
    if not spec["chartNames"]:
        print(f"  skipping render — no data")
        return
    result = subprocess.run(
        ["etna", "experiment", "visualize-json",
         "--input", str(json_path), "--output", str(png_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ETNA ERROR: {result.stderr.strip()}")
    else:
        print(f"  rendered {png_path.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", required=True, choices=["bst", "rbt", "stlc", "fsub"])
    ap.add_argument("--mode", default="default",
                    help="Shrink mode to use (default: 'default'). Must be one of the workload's available modes.")
    args = ap.parse_args()

    cfg = get_config(args.workload)
    if args.mode not in cfg["modes"]:
        raise SystemExit(f"workload {args.workload!r} has no mode {args.mode!r}; available: {cfg['modes']}")

    # Merge rows across all three frameworks for the chosen mode.
    rows = []
    for fw in cfg["variants"]:
        fname = cfg["stores"][(fw, args.mode)]
        rows.extend(load(ROOT / fname))
    print(f"=== {args.workload} / {args.mode} ===  loaded {len(rows)} rows")

    out_dir = ROOT / "figures"
    out_dir.mkdir(exist_ok=True)
    for fam, strats in cfg["families"].items():
        spec = build_spec(rows, strats)
        base = out_dir / f"bucket_{args.workload}_family-{fam}"
        render(spec, base.with_suffix(".json"), base.with_suffix(".png"))


if __name__ == "__main__":
    main()
