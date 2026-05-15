#!/usr/bin/env python3
"""ECDF charts for shrinking metrics, parameterised by workload.

Produces `figures/shrink_<workload>_{time-shrinking,ms-per-edit}_ecdf_family-<fam>.png`.

Reads `figures/<WORKLOAD>_ANALYSIS.csv` (produced by scripts/workload_analysis.py).
Default-mode Failed rows only. Each family gets its own ECDF panel; within
a panel, one line per strategy. Per (property, mutation) task we take the
median across trials and plot the cross-task distribution.

Usage: scripts/workload_ecdf.py --workload {bst,rbt,stlc,fsub}
"""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt

from workload_config import ROOT, COLORS, HATCHED, get_config


def load_default_rows(csv_path: Path):
    rows = []
    with csv_path.open() as f:
        for r in csv.DictReader(f):
            if r["mode"] != "default" or r["status"] != "Failed":
                continue
            for k in ("ted_to_gt", "pre_ted_to_gt", "time_shrinking"):
                if r.get(k) == "":
                    r[k] = None
                elif r.get(k) is not None:
                    try:
                        r[k] = float(r[k])
                    except ValueError:
                        pass
            rows.append(r)
    return rows


def task_medians(rows, strategy, value_fn):
    bytask = defaultdict(list)
    for r in rows:
        if r["strategy"] != strategy:
            continue
        v = value_fn(r)
        if v is None or v <= 0:
            continue
        bytask[(r["property"], r["mutation"])].append(v)
    return [median(v) for v in bytask.values() if v]


def value_time_shrinking_ms(r):
    t = r.get("time_shrinking")
    return None if t is None else t * 1000


def value_ms_per_edit(r):
    pre, post = r.get("pre_ted_to_gt"), r.get("ted_to_gt")
    if pre is None or post is None:
        return None
    d = pre - post
    if d <= 0:
        return None
    return (r.get("time_shrinking") or 0) * 1000 / d


METRICS = {
    "time-shrinking": (value_time_shrinking_ms,
                       "shrinking time per task (ms, log)",
                       "Shrinking wall-clock time per task"),
    "ms-per-edit":    (value_ms_per_edit,
                       "ms per TED edit (log)",
                       "Time-per-edit: ms / (pre TED − post TED)"),
}


def draw_ecdf(rows, strategies, value_fn, ax, xlabel, title):
    plotted = 0
    for s in strategies:
        xs = sorted(task_medians(rows, s, value_fn))
        if not xs:
            continue
        n = len(xs)
        ys = [(i + 1) / n for i in range(n)]
        c = COLORS.get(s, "#444")
        ls = ":" if s in HATCHED else "-"
        ax.step(xs, ys, where="post", color=c, linewidth=2.0,
                linestyle=ls, label=s)
        plotted += 1
    ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("fraction of tasks ≤ x")
    ax.set_title(title)
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=0.3, which="both")
    if plotted:
        ax.legend(loc="lower right", fontsize=8, frameon=False)
    return plotted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", required=True, choices=["bst", "rbt", "stlc", "fsub"])
    args = ap.parse_args()

    cfg = get_config(args.workload)
    csv_path = ROOT / "figures" / f"{args.workload.upper()}_ANALYSIS.csv"
    if not csv_path.exists():
        raise SystemExit(f"missing {csv_path}; run scripts/workload_analysis.py --workload {args.workload} first")

    rows = load_default_rows(csv_path)
    print(f"=== {args.workload} ===  loaded {len(rows)} default-mode Failed rows")

    out_dir = ROOT / "figures"
    out_dir.mkdir(exist_ok=True)
    families = cfg["families"]

    for metric_id, (vfn, ylabel, title) in METRICS.items():
        for fam, strats in families.items():
            fig, ax = plt.subplots(figsize=(6, 4))
            n = draw_ecdf(rows, strats, vfn, ax, ylabel,
                          f"{title} — {fam.upper()} ({args.workload}, default mode)")
            out = out_dir / f"shrink_{args.workload}_{metric_id}_ecdf_family-{fam}.png"
            if n == 0:
                plt.close(fig)
                print(f"  skip {out.name} (no data)")
                continue
            plt.tight_layout()
            plt.savefig(out, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"  wrote {out.name}")


if __name__ == "__main__":
    main()
