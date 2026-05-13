#!/usr/bin/env python3
"""
Continuous-distribution plots for shrinking metrics (replaces the
discretised bucket charts for the shrink-time analysis).

Per metric and per family, produces:
  - Box plot, one box per strategy (log y).
  - ECDF, one line per strategy (log x), shaded under the curve.

Reads figures/BST_ANALYSIS.csv (TED already computed).

Output naming:
  figures/shrink_bst_<metric>_<plotkind>_family-<fam>.png
where <plotkind> ∈ {box, ecdf}, <fam> ∈ {vanilla, cbc, qbe},
<metric>  ∈ {time-shrinking, ms-per-edit}.
"""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/Users/akeles/Programming/projects/PbtBenchmark/shrinking-evaluation")
CSV_PATH = ROOT / "figures" / "BST_ANALYSIS.csv"

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


def load_default_rows():
    rows = []
    with CSV_PATH.open() as f:
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
    """Per (property, mutation) task: median of value_fn across trials."""
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


def draw_box(rows, strategies, value_fn, ax, ylabel, title):
    data = []
    labels = []
    colors = []
    hatches = []
    for s in strategies:
        xs = task_medians(rows, s, value_fn)
        if not xs:
            continue
        data.append(xs)
        labels.append(s)
        colors.append(COLORS.get(s, "#444"))
        hatches.append("//" if s in HATCHED else "")

    bp = ax.boxplot(
        data, tick_labels=labels, patch_artist=True, widths=0.6,
        showmeans=True,
        meanprops=dict(marker="D", markerfacecolor="white",
                       markeredgecolor="black", markersize=6),
        medianprops=dict(color="black", linewidth=1.5),
        whiskerprops=dict(color="#333"),
        capprops=dict(color="#333"),
    )
    for patch, c, h in zip(bp["boxes"], colors, hatches):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
        if h:
            patch.set_hatch(h)
            patch.set_edgecolor("white")
            patch.set_linewidth(0)

    ax.set_yscale("log")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3, which="both")
    ax.tick_params(axis="x", rotation=30)
    for lbl in ax.get_xticklabels():
        lbl.set_horizontalalignment("right")


def draw_ecdf(rows, strategies, value_fn, ax, xlabel, title):
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

    ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("fraction of tasks ≤ x")
    ax.set_title(title)
    ax.set_ylim(0, 1.02)
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(loc="lower right", fontsize=8, frameon=False)


def main():
    out_dir = ROOT / "figures"
    rows = load_default_rows()
    print(f"loaded {len(rows)} default-mode Failed rows")

    for metric_id, (vfn, ylabel, title) in METRICS.items():
        for fam, strats in FAMILIES.items():
            # Box plot
            fig, ax = plt.subplots(figsize=(max(6, 0.9 * len(strats) + 2), 4.5))
            draw_box(rows, strats, vfn, ax, ylabel,
                     f"{title} — {fam.upper()} (BST, default mode)")
            out = out_dir / f"shrink_bst_{metric_id}_box_family-{fam}.png"
            plt.tight_layout()
            plt.savefig(out, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"wrote {out}")

            # ECDF
            fig, ax = plt.subplots(figsize=(6, 4))
            draw_ecdf(rows, strats, vfn, ax, ylabel,
                      f"{title} — {fam.upper()} (BST, default mode)")
            out = out_dir / f"shrink_bst_{metric_id}_ecdf_family-{fam}.png"
            plt.tight_layout()
            plt.savefig(out, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
