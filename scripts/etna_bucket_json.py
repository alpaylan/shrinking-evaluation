#!/usr/bin/env python3
"""
Build a BucketChartJson for `etna experiment visualize-json`.

Produces a JSON per (workload, shrink-mode) with one row per strategy,
colored by generator family + framework, and labelled with the strategy
name. Counts task-level bug-finding buckets using the project's
established convention (any-trial-timeout → Not Found).
"""

import json
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import median

ROOT = Path("/Users/akeles/Programming/projects/PbtBenchmark/shrinking-evaluation")

# (workload, mode) -> list of store files to merge
SOURCES = {
    ("bst", "0"):       [f"store.bst.{fw}.shrink-0.jsonl"       for fw in ("quick","hedgehog","falsify")],
    ("bst", "100"):     [f"store.bst.{fw}.shrink-100.jsonl"     for fw in ("quick","hedgehog","falsify")],
    ("bst", "default"): [f"store.bst.{fw}.shrink-default.jsonl" for fw in ("quick","hedgehog","falsify")],
    ("rbt", "0"):       [f"store.rbt.{fw}.shrink-0.jsonl"       for fw in ("quick","hedgehog","falsify")],
}

# Generator-family groupings (used when --group is set).
FAMILIES = {
    "vanilla": ["Quick", "Hedgehog", "Falsify"],
    "cbc":     ["QuickCBC", "HedgehogCBC", "HedgehogCBC2", "FalsifyCBC", "FalsifyCBC2"],
    "qbe":     ["QuickGbE", "HedgehogGbE", "FalsifyGbE"],
}

# Row order (matches our paper-draft conventions).
STRATEGIES = [
    "Quick", "QuickCBC", "QuickGbE",
    "Hedgehog", "HedgehogCBC", "HedgehogCBC2", "HedgehogGbE",
    "Falsify", "FalsifyCBC", "FalsifyCBC2", "FalsifyGbE",
]

# One color per *framework* (not per strategy). All Quick*, Hedgehog*,
# Falsify* variants share the same darkest hex so the framework family
# is identifiable at a glance across all charts.
QUICK_COLOR    = "#1b7837"   # dark green
HEDGEHOG_COLOR = "#2166ac"   # dark blue
FALSIFY_COLOR  = "#b35806"   # dark orange

COLORS = {
    "Quick":         QUICK_COLOR,
    "QuickCBC":      QUICK_COLOR,
    "QuickGbE":      QUICK_COLOR,
    "Hedgehog":      HEDGEHOG_COLOR,
    "HedgehogCBC":   HEDGEHOG_COLOR,
    "HedgehogCBC2":  HEDGEHOG_COLOR,
    "HedgehogGbE":   HEDGEHOG_COLOR,
    "Falsify":       FALSIFY_COLOR,
    "FalsifyCBC":    FALSIFY_COLOR,
    "FalsifyCBC2":   FALSIFY_COLOR,
    "FalsifyGbE":    FALSIFY_COLOR,
}

# Strategies that should render with a hatched (pointed) pattern so the
# "idiomatic" CBC2 variants stand out visually from plain CBC.
HATCHED = {"HedgehogCBC2", "FalsifyCBC2"}

# Time buckets in seconds. ETNA expects bucket VALUES per row;
# we'll emit counts directly. Buckets implicitly: [0, 0.1), [0.1, 1),
# [1, 10), [10, 60), [60, inf) and an explicit "Not Found" last bucket.
BUCKETS = [
    ("< 0.1s",  0.0,   0.1),
    ("< 1s",    0.1,   1.0),
    ("< 10s",   1.0,   10.0),
    ("< 60s",  10.0,   60.0),
    ("≥ 60s",  60.0, float("inf")),
]
NUM_BUCKETS = len(BUCKETS) + 1  # +1 for "Not Found"


def load_rows(workload, mode):
    rows = []
    for fname in SOURCES[(workload, mode)]:
        p = ROOT / fname
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line)["data"])
    return rows


def task_key(r):
    return (r["property"], ",".join(r.get("mutations", []) or []))


def task_bucket(trials):
    # any-trial-timeout → Not Found
    if any(r["status"] != "Failed" for r in trials):
        return NUM_BUCKETS - 1  # Not Found slot
    times = [r["time_pre_failure"] for r in trials
             if r["status"] == "Failed" and r.get("time_pre_failure") is not None]
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


def build_json(workload, mode, strategies):
    rows = load_rows(workload, mode)
    chart_names = []
    chart_colors = []
    bar_styles = []
    bucket_values = []
    for s in strategies:
        counts = counts_for(rows, s)
        if sum(counts) == 0:
            continue
        chart_names.append(s)
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
    print(f"wrote {json_path} ({len(spec['chartNames'])} strategies)")
    result = subprocess.run(
        ["etna", "experiment", "visualize-json",
         "--input", str(json_path), "--output", str(png_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ETNA ERROR: {result.stderr}")
    else:
        print(f"  rendered {png_path}")


def main():
    out_dir = ROOT / "figures"
    out_dir.mkdir(exist_ok=True)

    # One chart per ETNA_SHRINKS mode (all 11 strategies, full sweep view).
    for (workload, mode), _ in SOURCES.items():
        spec = build_json(workload, mode, STRATEGIES)
        json_path = out_dir / f"bucket_{workload}_shrink-{mode}.json"
        png_path  = out_dir / f"bucket_{workload}_shrink-{mode}.png"
        render(spec, json_path, png_path)

    # One chart per generator family (default mode). 3 small charts that
    # make the within-family comparison easier to eyeball.
    for fam, strats in FAMILIES.items():
        spec = build_json("bst", "default", strats)
        json_path = out_dir / f"bucket_bst_family-{fam}.json"
        png_path  = out_dir / f"bucket_bst_family-{fam}.png"
        render(spec, json_path, png_path)

    # rbt has only shrinks=0 data right now; produce the same 3 family charts.
    for fam, strats in FAMILIES.items():
        if ("rbt", "0") not in SOURCES:
            continue
        spec = build_json("rbt", "0", strats)
        json_path = out_dir / f"bucket_rbt_shrink-0_family-{fam}.json"
        png_path  = out_dir / f"bucket_rbt_shrink-0_family-{fam}.png"
        render(spec, json_path, png_path)


if __name__ == "__main__":
    main()
