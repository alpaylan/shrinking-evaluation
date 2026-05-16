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

from workload_config import ROOT, COLORS, HATCHED, display_name, get_config


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


def task_medians(rows, strategy, value_fn, drop_nonpositive=True):
    bytask = defaultdict(list)
    for r in rows:
        if r["strategy"] != strategy:
            continue
        v = value_fn(r)
        if v is None:
            continue
        if drop_nonpositive and v <= 0:
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


def value_ted_to_gt(r):
    """Absolute TED of the final (post-shrink) counterexample to the
    ground-truth minimum. 0 = reached the minimum."""
    return r.get("ted_to_gt")


# metric_id -> dict(value_fn, xlabel, xscale, drop_nonpositive)
METRICS = {
    "time-shrinking": dict(
        value_fn=value_time_shrinking_ms,
        xlabel="shrinking time per task (ms, log)",
        xscale="log", drop_nonpositive=True),
    "ms-per-edit": dict(
        value_fn=value_ms_per_edit,
        xlabel="ms per TED edit (log)",
        xscale="log", drop_nonpositive=True),
    "ted-to-gt": dict(
        value_fn=value_ted_to_gt,
        xlabel="TED to ground-truth minimum (post-shrink)",
        xscale="linear", drop_nonpositive=False),
}


def draw_ecdf(rows, strategies, spec, ax):
    plotted = 0
    max_n = 0
    for s in strategies:
        xs = sorted(task_medians(rows, s, spec["value_fn"],
                                 drop_nonpositive=spec["drop_nonpositive"]))
        if not xs:
            continue
        n = len(xs)
        max_n = max(max_n, n)
        # Cumulative *count* of tasks (not fraction).
        ys = [i + 1 for i in range(n)]
        c = COLORS.get(s, "#444")
        ls = ":" if s in HATCHED else "-"
        ax.step(xs, ys, where="post", color=c, linewidth=2.0,
                linestyle=ls, label=f"{display_name(s)} (n={n})")
        plotted += 1
    ax.set_xscale(spec["xscale"])
    ax.set_xlabel(spec["xlabel"])
    ax.set_ylabel("number of tasks ≤ x")
    if max_n:
        ax.set_ylim(0, max_n * 1.05)
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

    # All strategies, in family order, deduped — for the combined chart.
    all_strats = []
    for strats in families.values():
        for s in strats:
            if s not in all_strats:
                all_strats.append(s)

    for metric_id, spec in METRICS.items():
        # Per-family panels.
        for fam, strats in families.items():
            fig, ax = plt.subplots(figsize=(6, 4))
            n = draw_ecdf(rows, strats, spec, ax)
            out = out_dir / f"shrink_{args.workload}_{metric_id}_ecdf_family-{fam}.png"
            if n == 0:
                plt.close(fig)
                print(f"  skip {out.name} (no data)")
                continue
            plt.tight_layout()
            plt.savefig(out, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"  wrote {out.name}")

        # Combined panel: every strategy for this workload on one axes.
        fig, ax = plt.subplots(figsize=(7, 5))
        n = draw_ecdf(rows, all_strats, spec, ax)
        out = out_dir / f"shrink_{args.workload}_{metric_id}_ecdf.png"
        if n == 0:
            plt.close(fig)
            print(f"  skip {out.name} (no data)")
        else:
            plt.tight_layout()
            plt.savefig(out, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"  wrote {out.name}")


if __name__ == "__main__":
    main()
