#!/usr/bin/env python3
"""Paired statistical comparison of shrinking strategies, per workload.

Design (see discussion): trials of a strategy on one (property, mutation)
task are independent runs with different seeds, so within a task two
strategies are compared with the Mann-Whitney U test — the test the
fuzzing / randomized-testing literature recommends (Klees et al.;
Arcuri & Briand). Across tasks the design is paired, so we aggregate the
per-task verdicts rather than pooling trials.

Per strategy pair, per metric, we report:
  - # tasks where A is significantly better than B
  - # tasks where B is significantly better than A
  - # tasks not significant
  - mean Vargha-Delaney Â₁₂ (probability an A-trial beats a B-trial)

Per-task p-values are Holm-corrected within each (pair, metric) group.
All metrics are "lower is better" (TED, shrink time, ms/edit).

Usage: scripts/workload_stats.py --workload {bst,rbt,stlc,fsub}
Run with the project venv: .venv/bin/python scripts/workload_stats.py ...
"""

import argparse
import csv
import itertools
from collections import defaultdict
from pathlib import Path

from scipy.stats import mannwhitneyu

from workload_config import ROOT, display_name, get_config

ALPHA = 0.05


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---- metric value functions (lower is better) ----

def value_ted(r):
    return fnum(r.get("ted_to_gt"))


def value_time_shrinking_ms(r):
    t = fnum(r.get("time_shrinking"))
    return None if t is None else t * 1000


def value_ms_per_edit(r):
    pre, post = fnum(r.get("pre_ted_to_gt")), fnum(r.get("ted_to_gt"))
    t = fnum(r.get("time_shrinking"))
    if pre is None or post is None or t is None:
        return None
    d = pre - post
    if d <= 0:
        return None
    return t * 1000 / d


METRICS = {
    "ted-to-gt":      value_ted,
    "time-shrinking": value_time_shrinking_ms,
    "ms-per-edit":    value_ms_per_edit,
}


def a12_smaller(a, b):
    """Vargha-Delaney Â₁₂ for 'a tends to be smaller than b'.
    0.5 = no difference; >0.5 = a is better (lower values)."""
    less = greater = equal = 0
    for x in a:
        for y in b:
            if x < y:
                less += 1
            elif x > y:
                greater += 1
            else:
                equal += 1
    return (less + 0.5 * equal) / (len(a) * len(b))


def holm(pvals):
    """Holm-Bonferroni: return list of booleans (reject H0) aligned to pvals."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    reject = [False] * m
    for rank, i in enumerate(order):
        thresh = ALPHA / (m - rank)
        if pvals[i] <= thresh:
            reject[i] = True
        else:
            break  # once one fails, all larger p-values fail too
    return reject


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", required=True, choices=["bst", "rbt", "stlc", "fsub"])
    args = ap.parse_args()

    cfg = get_config(args.workload)
    csv_path = ROOT / "figures" / f"{args.workload.upper()}_ANALYSIS.csv"
    if not csv_path.exists():
        raise SystemExit(f"missing {csv_path}; run scripts/workload_analysis.py --workload {args.workload} first")

    # strategies in family order, deduped
    strategies = []
    for strats in cfg["families"].values():
        for s in strats:
            if s not in strategies:
                strategies.append(s)

    rows = [r for r in csv.DictReader(csv_path.open())
            if r["mode"] == "default" and r["status"] == "Failed"]

    # values[metric][strategy][(property,mutation)] -> list of trial values
    values = {m: defaultdict(lambda: defaultdict(list)) for m in METRICS}
    for r in rows:
        if r["strategy"] not in strategies:
            continue
        task = (r["property"], r["mutation"])
        for m, vfn in METRICS.items():
            v = vfn(r)
            if v is not None:
                values[m][r["strategy"]][task].append(v)

    out = [f"# {args.workload.upper()} — paired strategy comparison",
           "",
           "Within each (property, mutation) task: Mann-Whitney U (two-sided) on the",
           "two strategies' per-trial values. Per-task p-values Holm-corrected within",
           f"each (pair, metric). α = {ALPHA}. All metrics lower-is-better.",
           "",
           "**Â₁₂** = Vargha-Delaney effect size: probability a random A-trial beats",
           "a random B-trial. Â₁₂ > 0.5 ⇒ A better; reported as the mean over tasks.",
           ""]

    for m in METRICS:
        out.append(f"## Metric: {m}")
        out.append("")
        out.append("| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |")
        out.append("|---|---|---:|---:|---:|---:|---:|")
        for A, B in itertools.combinations(strategies, 2):
            tA, tB = values[m][A], values[m][B]
            common = sorted(set(tA) & set(tB))
            pvals, a12s, dirs = [], [], []
            for task in common:
                a, b = tA[task], tB[task]
                if len(a) < 2 or len(b) < 2:
                    continue
                try:
                    _, p = mannwhitneyu(a, b, alternative="two-sided")
                except ValueError:
                    p = 1.0  # all values identical
                e = a12_smaller(a, b)
                pvals.append(p)
                a12s.append(e)
                dirs.append(e)
            if not pvals:
                out.append(f"| {display_name(A)} | {display_name(B)} | — | — | — | — | 0 |")
                continue
            reject = holm(pvals)
            a_better = sum(1 for r_, e in zip(reject, dirs) if r_ and e > 0.5)
            b_better = sum(1 for r_, e in zip(reject, dirs) if r_ and e < 0.5)
            ns = len(pvals) - a_better - b_better
            mean_a12 = sum(a12s) / len(a12s)
            out.append(f"| {display_name(A)} | {display_name(B)} | {a_better} | "
                       f"{b_better} | {ns} | {mean_a12:.3f} | {len(pvals)} |")
        out.append("")

    dest = ROOT / "figures" / f"{args.workload.upper()}_STATS.md"
    dest.write_text("\n".join(out) + "\n")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
