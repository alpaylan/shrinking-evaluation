#!/usr/bin/env python3
"""
ETNA-style bucket charts: bug-finding capability per (strategy, mode).

For each (property, mutation) task and each strategy, take the median
time_pre_failure across trials. If no trial found the bug (status !=
Failed), bucket as "Not Found". Stacked bars per mode.
"""

import json
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent

# Workload prefix used in the store filename. Currently only bst is
# complete; rbt sweeps are still running.
WORKLOAD = "bst"

# (framework, mode) -> store path
STORES = {
    ("Quick",    "none"):      f"store.{WORKLOAD}.quick.shrink-0.jsonl",
    ("Quick",    "fixed-100"): f"store.{WORKLOAD}.quick.shrink-100.jsonl",
    ("Quick",    "default"):   f"store.{WORKLOAD}.quick.shrink-default.jsonl",
    ("Hedgehog", "none"):      f"store.{WORKLOAD}.hedgehog.shrink-0.jsonl",
    ("Hedgehog", "fixed-100"): f"store.{WORKLOAD}.hedgehog.shrink-100.jsonl",
    ("Hedgehog", "default"):   f"store.{WORKLOAD}.hedgehog.shrink-default.jsonl",
    ("Falsify",  "none"):      f"store.{WORKLOAD}.falsify.shrink-0.jsonl",
    ("Falsify",  "fixed-100"): f"store.{WORKLOAD}.falsify.shrink-100.jsonl",
    ("Falsify",  "default"):   f"store.{WORKLOAD}.falsify.shrink-default.jsonl",
}

# Strategy variants per framework (used for loading + CSV).
VARIANTS = {
    "Quick":    ["Quick",    "QuickCBC",                   "QuickGbE"],
    "Hedgehog": ["Hedgehog", "HedgehogCBC", "HedgehogCBC2", "HedgehogGbE"],
    "Falsify":  ["Falsify",  "FalsifyCBC",  "FalsifyCBC2",  "FalsifyGbE"],
}

# x-axis layout: grouped by generator type. The CBC group includes the
# "Idiomatic" CBC2 variants alongside their plain CBC siblings (paired:
# Hedgehog + Hedgehog Idiomatic, Falsify + Falsify Idiomatic).
# Each tuple entry is (framework, strategy, label).
GROUPS = [
    ("vanilla", [
        ("Quick",    "Quick",    "Quick"),
        ("Hedgehog", "Hedgehog", "Hedgehog"),
        ("Falsify",  "Falsify",  "Falsify"),
    ]),
    ("CBC", [
        ("Quick",    "QuickCBC",     "Quick"),
        ("Hedgehog", "HedgehogCBC",  "Hedgehog"),
        ("Hedgehog", "HedgehogCBC2", "Hedgehog\nIdiomatic"),
        ("Falsify",  "FalsifyCBC",   "Falsify"),
        ("Falsify",  "FalsifyCBC2",  "Falsify\nIdiomatic"),
    ]),
    ("GbE", [
        ("Quick",    "QuickGbE",    "Quick"),
        ("Hedgehog", "HedgehogGbE", "Hedgehog"),
        ("Falsify",  "FalsifyGbE",  "Falsify"),
    ]),
]

# ETNA-style time buckets (seconds). Order = bottom-to-top of stack.
BUCKETS = [
    ("< 0.1s",   0.0,   0.1),
    ("< 1s",     0.1,   1.0),
    ("< 10s",    1.0,   10.0),
    ("< 60s",   10.0,   60.0),
    ("≥ 60s", 60.0, float("inf")),
]
BUCKET_LABELS = [b[0] for b in BUCKETS] + ["Not Found"]

# Solid colormap: greens for fast → yellow/orange → red, then gray for not found.
BUCKET_COLORS = [
    "#1a9850",  # < 0.1s   — dark green
    "#91cf60",  # < 1s
    "#fee08b",  # < 10s    — yellow
    "#fc8d59",  # < 60s    — orange
    "#d73027",  # >= 60s   — red
    "#bbbbbb",  # Not Found
]


def load(path: Path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line)["data"])
    return out


def task_key(r):
    return (r["property"], ",".join(r.get("mutations", []) or []))


def bucket_index(t: float) -> int:
    for i, (_, lo, hi) in enumerate(BUCKETS):
        if lo <= t < hi:
            return i
    return len(BUCKETS) - 1


def task_bucket(rows_for_strategy_and_task) -> int:
    """Median time across Failed trials, mapped to a bucket. Returns -1
    (Not Found) if ANY trial timed out — a strategy that intermittently
    misses a bug doesn't reliably find it. The same applies to tasks
    where all rows are non-Failed."""
    times = []
    for r in rows_for_strategy_and_task:
        if r["status"] != "Failed":
            return -1  # any timeout/aborted disqualifies the whole task
        t = r.get("time_pre_failure")
        if t is None:
            return -1
        times.append(t)
    if not times:
        return -1
    return bucket_index(median(times))


def collect(framework: str, mode: str):
    """Return {strategy: {bucket_index: count_of_tasks}}."""
    rows = load(ROOT / STORES[(framework, mode)])
    by_strat_task = defaultdict(lambda: defaultdict(list))
    all_tasks_per_strat = defaultdict(set)
    for r in rows:
        s = r["strategy"]
        k = task_key(r)
        by_strat_task[s][k].append(r)
        all_tasks_per_strat[s].add(k)
    out = {}
    for s, tasks in by_strat_task.items():
        counts = [0] * (len(BUCKETS) + 1)
        for k, trials in tasks.items():
            b = task_bucket(trials)
            counts[b if b >= 0 else len(BUCKETS)] += 1
        out[s] = counts
    return out


def normalize(counts):
    total = sum(counts)
    return [c / total * 100 if total else 0 for c in counts]


def draw_one_mode(mode: str, out_path: Path):
    # Width scales with bar count (CBC group now has 5 bars).
    n_bars = sum(len(members) for _, members in GROUPS)
    fig, ax = plt.subplots(figsize=(max(10, 0.9 * n_bars + 3), 5.5))

    # Pre-collect per-framework counts.
    fw_counts = {fw: collect(fw, mode) for fw in ["Quick", "Hedgehog", "Falsify"]}

    bar_data = []
    bar_labels = []
    bar_xs = []
    x_cursor = 0.0
    group_centers = []
    for gen_label, members in GROUPS:
        group_start = x_cursor
        for fw, strat, label in members:
            counts = fw_counts[fw].get(strat, [0] * (len(BUCKETS) + 1))
            bar_data.append(normalize(counts))
            bar_labels.append(label)
            bar_xs.append(x_cursor)
            x_cursor += 1.0
        group_centers.append((gen_label, (group_start + x_cursor - 1) / 2))
        x_cursor += 1.0  # gap between groups

    arr = np.array(bar_data)
    x = np.array(bar_xs)

    bottom = np.zeros(len(x))
    for b_idx, label in enumerate(BUCKET_LABELS):
        heights = arr[:, b_idx]
        ax.bar(x, heights, bottom=bottom, color=BUCKET_COLORS[b_idx],
               label=label, edgecolor="white", linewidth=0.4)
        bottom += heights

    ax.set_xticks(x)
    ax.set_xticklabels(bar_labels, rotation=0, fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of (property, mutation) tasks")
    ax.set_title(f"Bug-finding bucket chart [{WORKLOAD}] — ETNA_SHRINKS={mode}")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)

    # Generator-type group labels under the bar labels
    for gen_label, center_x in group_centers:
        ax.annotate(gen_label, xy=(center_x, -32), xycoords=("data", "axes points"),
                    ha="center", fontsize=11, fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def write_csv(out_csv: Path):
    """Wide CSV: one row per (framework, strategy, mode), columns per bucket %."""
    out_lines = ["framework,strategy,mode,n_tasks," + ",".join(BUCKET_LABELS)]
    for fw in ["Quick", "Hedgehog", "Falsify"]:
        for mode in ["none", "fixed-100", "default"]:
            strat_counts = collect(fw, mode)
            for s in VARIANTS[fw]:
                cnts = strat_counts.get(s, [0] * (len(BUCKETS) + 1))
                total = sum(cnts)
                pct = [f"{c/total*100:.1f}" if total else "0.0" for c in cnts]
                out_lines.append(",".join([fw, s, mode, str(total), *pct]))
    out_csv.write_text("\n".join(out_lines) + "\n")


def main():
    figs_dir = ROOT / "figures"
    figs_dir.mkdir(exist_ok=True)
    for mode in ["none", "fixed-100", "default"]:
        out = figs_dir / f"bucket_chart_{mode}.png"
        draw_one_mode(mode, out)
        print(f"wrote {out}")
    csv = figs_dir / "bucket_chart_data.csv"
    write_csv(csv)
    print(f"wrote {csv}")


if __name__ == "__main__":
    main()
