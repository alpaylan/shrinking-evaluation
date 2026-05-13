#!/usr/bin/env python3
"""
Build BucketChartJson for shrinking-time charts (A1) and ms-per-edit
charts (A2). Reads figures/BST_ANALYSIS.csv so TED is not recomputed.

Output naming convention matches scripts/etna_bucket_json.py:
  figures/shrink_bst_time-shrinking_family-{vanilla,cbc,qbe}.{json,png}
  figures/shrink_bst_ms-per-edit_family-{vanilla,cbc,qbe}.{json,png}
"""

import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from statistics import median

ROOT = Path("/Users/akeles/Programming/projects/PbtBenchmark/shrinking-evaluation")
CSV_PATH = ROOT / "figures" / "BST_ANALYSIS.csv"

# Match existing chart conventions.
FAMILIES = {
    "vanilla": ["Quick", "Hedgehog", "Falsify"],
    "cbc":     ["QuickCBC", "HedgehogCBC", "HedgehogCBC2", "FalsifyCBC", "FalsifyCBC2"],
    "qbe":     ["QuickGbE", "HedgehogGbE", "FalsifyGbE"],
}

QUICK_COLOR    = "#1b7837"
HEDGEHOG_COLOR = "#2166ac"
FALSIFY_COLOR  = "#b35806"
COLORS = {
    "Quick": QUICK_COLOR, "QuickCBC": QUICK_COLOR, "QuickGbE": QUICK_COLOR,
    "Hedgehog": HEDGEHOG_COLOR, "HedgehogCBC": HEDGEHOG_COLOR,
    "HedgehogCBC2": HEDGEHOG_COLOR, "HedgehogGbE": HEDGEHOG_COLOR,
    "Falsify": FALSIFY_COLOR, "FalsifyCBC": FALSIFY_COLOR,
    "FalsifyCBC2": FALSIFY_COLOR, "FalsifyGbE": FALSIFY_COLOR,
}
HATCHED = {"HedgehogCBC2", "FalsifyCBC2"}

# Bucket schemes per metric. Each is a list of upper bounds (exclusive)
# in the metric's unit; the last bucket is [last_bound, inf).
#
# A1: time_shrinking in MILLISECONDS. Falsify can hit hundreds of ms;
# Quick/Hedgehog usually <1 ms. Five buckets:
A1_BUCKETS = [
    ("< 1 ms",   1.0),
    ("< 10 ms",  10.0),
    ("< 100 ms", 100.0),
    ("< 1 s",    1000.0),
    ("≥ 1 s",    float("inf")),
]

# A2: ms per TED edit reduced. Quick ~0.1 ms/edit, Falsify ~10–100 ms/edit.
A2_BUCKETS = [
    ("< 0.01 ms",   0.01),
    ("< 0.1 ms",    0.1),
    ("< 1 ms",      1.0),
    ("< 10 ms",     10.0),
    ("≥ 10 ms",     float("inf")),
]

# Total = real-bucket count + Not Found slot
def num_buckets(scheme): return len(scheme) + 1


def load_csv():
    rows = []
    with CSV_PATH.open() as f:
        for r in csv.DictReader(f):
            for k in ("ted_to_gt","pre_ted_to_gt","time_shrinking"):
                if r.get(k) == "": r[k] = None
                elif r.get(k) is not None:
                    try: r[k] = float(r[k])
                    except ValueError: pass
            rows.append(r)
    return rows


def task_key(r): return (r["property"], r["mutation"])


def bucket_for(value, scheme):
    """Pick bucket index for value. Returns last index if None."""
    if value is None: return len(scheme)  # Not Found
    for i, (_, ub) in enumerate(scheme):
        if value < ub: return i
    return len(scheme) - 1


def counts_for(rows, strategy, scheme, value_fn):
    """Per-task: median of value_fn across trials, then bucket the median.
    Tasks with no eligible trials (or any timeout) go to Not Found."""
    bytask = defaultdict(list)
    for r in rows:
        if r["strategy"] != strategy: continue
        # Tasks with any non-Failed trial → Not Found (consistent with
        # the bug-finding convention).
        bytask[task_key(r)].append(r)
    counts = [0] * num_buckets(scheme)
    for trials in bytask.values():
        # any-trial-timeout → Not Found
        if any(t["status"] != "Failed" for t in trials):
            counts[-1] += 1
            continue
        vals = [v for v in (value_fn(t) for t in trials) if v is not None]
        if not vals:
            counts[-1] += 1
            continue
        counts[bucket_for(median(vals), scheme)] += 1
    return counts


def value_time_shrinking_ms(r):
    t = r.get("time_shrinking")
    return None if t is None else t * 1000


def value_ms_per_edit(r):
    """time_shrinking / (pre_TED - post_TED), in milliseconds per edit.
    None if no reduction happened (we don't want a divide-by-zero
    blowing up the bucket — those tasks fall through to Not Found)."""
    pre, post = r.get("pre_ted_to_gt"), r.get("ted_to_gt")
    if pre is None or post is None: return None
    d = pre - post
    if d <= 0: return None
    return (r.get("time_shrinking") or 0) * 1000 / d


def build_spec(rows, strategies, scheme, value_fn):
    chart_names, chart_colors, bar_styles, bucket_values = [], [], [], []
    for s in strategies:
        counts = counts_for(rows, s, scheme, value_fn)
        if sum(counts) == 0: continue
        chart_names.append(s)
        chart_colors.append(COLORS.get(s, "#000000"))
        bar_styles.append("hatched" if s in HATCHED else "solid")
        bucket_values.append([str(c) for c in counts])
    return {
        "numBuckets": num_buckets(scheme),
        "chartNames": chart_names,
        "chartColors": chart_colors,
        "barStyles": bar_styles,
        "bucketValues": bucket_values,
    }


def render(spec, json_path, png_path):
    json_path.write_text(json.dumps(spec, indent=2))
    print(f"wrote {json_path} ({len(spec['chartNames'])} strategies)")
    res = subprocess.run(
        ["etna", "experiment", "visualize-json",
         "--input", str(json_path), "--output", str(png_path)],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        print(f"  ETNA ERROR: {res.stderr}")
    else:
        print(f"  rendered {png_path}")


def main():
    out_dir = ROOT / "figures"
    rows = load_csv()
    rows = [r for r in rows if r["mode"] == "default"]
    print(f"loaded {len(rows)} default-mode rows")

    for label, scheme, value_fn in [
        ("time-shrinking", A1_BUCKETS, value_time_shrinking_ms),
        ("ms-per-edit",    A2_BUCKETS, value_ms_per_edit),
    ]:
        for fam, strats in FAMILIES.items():
            spec = build_spec(rows, strats, scheme, value_fn)
            base = out_dir / f"shrink_bst_{label}_family-{fam}"
            render(spec, base.with_suffix(".json"), base.with_suffix(".png"))


if __name__ == "__main__":
    main()
