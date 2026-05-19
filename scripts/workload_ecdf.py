#!/usr/bin/env python3
"""ECDF charts for shrinking metrics, parameterised by workload.

Produces `figures/shrink_<workload>_<metric>_ecdf_family-<fam>.png` (per
generator family) plus a combined `shrink_<workload>_<metric>_ecdf.png`.

Reads `figures/<WORKLOAD>_ANALYSIS.csv` (produced by scripts/workload_analysis.py).
Default-mode Failed rows only. Per (property, mutation) task we take the
median across trials and plot the cross-task cumulative distribution
(y = number of tasks ≤ x).

Conventions:
  - Axes are fixed per (workload, metric): every family panel shares the
    same x- and y-range, so panels can be read side by side.
  - Lines are solid for all strategies. The single exception is the BST
    CBC panel, where the idiomatic variants are dashed (they share a
    framework colour with plain CBC).
  - A dotted reference line marks the total task count for the metric, so
    a curve that plateaus below it visibly "didn't reach" every task.

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


def task_median_map(rows, strategy, value_fn, drop_nonpositive):
    """(property, mutation) -> median metric value across that task's trials."""
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
    return {k: median(v) for k, v in bytask.items() if v}


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
    "cex-size": dict(
        value_fn=lambda r: r.get("cex_size"),
        xlabel="shrunk counterexample size (nodes)",
        xscale="linear", drop_nonpositive=False),
}


def line_style(workload, family, strategy):
    """Solid everywhere, except the BST CBC panel where the idiomatic
    (CBC2) variants are dashed so they read apart from plain CBC."""
    if workload == "bst" and family == "cbc" and strategy in HATCHED:
        return "--"
    return "-"


def draw_ecdf(median_maps, strategies, ax, *, workload, family, spec,
              xlim, n_tasks):
    """median_maps: {strategy: {task: median_value}}."""
    plotted = 0
    for s in strategies:
        xs = sorted(median_maps.get(s, {}).values())
        if not xs:
            continue
        ys = [i + 1 for i in range(len(xs))]
        ax.step(xs, ys, where="post", color=COLORS.get(s, "#444"),
                linewidth=2.0, linestyle=line_style(workload, family, s),
                label=f"{display_name(s)} (n={len(xs)})")
        plotted += 1
    if not plotted:
        return 0

    # Reference line at the total task count for this metric.
    ax.axhline(n_tasks, color="0.55", linestyle=(0, (2, 2)),
               linewidth=1.0, zorder=1)
    ax.text(0.015, n_tasks, f"{n_tasks} tasks",
            transform=ax.get_yaxis_transform(),
            ha="left", va="bottom", fontsize=7, color="0.4")

    ax.set_xscale(spec["xscale"])
    if xlim:
        ax.set_xlim(*xlim)
    ax.set_ylim(0, n_tasks * 1.08)
    ax.set_xlabel(spec["xlabel"])
    ax.set_ylabel("number of tasks ≤ x")
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    return plotted


def fixed_xlim(median_maps, xscale):
    """Shared x-range across every strategy's per-task values."""
    vals = [v for m in median_maps.values() for v in m.values()]
    if not vals:
        return None
    lo, hi = min(vals), max(vals)
    if xscale == "log":
        lo = min(v for v in vals if v > 0)
        return (lo * 0.8, hi * 1.25)
    span = hi - lo or 1.0
    return (lo - 0.02 * span, hi + 0.05 * span)


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

    all_strats = []
    for strats in families.values():
        for s in strats:
            if s not in all_strats:
                all_strats.append(s)

    for metric_id, spec in METRICS.items():
        # Precompute per-strategy task->median maps once per metric.
        maps = {s: task_median_map(rows, s, spec["value_fn"],
                                   spec["drop_nonpositive"])
                for s in all_strats}
        # Fixed scale per (workload, metric): shared x-range and a task
        # count that is the union of tasks measurable for this metric.
        xlim = fixed_xlim(maps, spec["xscale"])
        universe = set()
        for m in maps.values():
            universe |= set(m)
        n_tasks = len(universe)
        if n_tasks == 0:
            print(f"  skip {metric_id} (no data)")
            continue

        # Per-family panels.
        for fam, strats in families.items():
            fig, ax = plt.subplots(figsize=(6, 4))
            n = draw_ecdf(maps, strats, ax, workload=args.workload,
                          family=fam, spec=spec, xlim=xlim, n_tasks=n_tasks)
            out = out_dir / f"shrink_{args.workload}_{metric_id}_ecdf_family-{fam}.png"
            if n == 0:
                plt.close(fig)
                print(f"  skip {out.name} (no data)")
                continue
            plt.tight_layout()
            plt.savefig(out, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"  wrote {out.name}")

        # Combined panel: every strategy on one axes.
        fig, ax = plt.subplots(figsize=(7, 5))
        n = draw_ecdf(maps, all_strats, ax, workload=args.workload,
                      family="combined", spec=spec, xlim=xlim, n_tasks=n_tasks)
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
