#!/usr/bin/env python3
"""Shrinking sample-efficiency analysis, per (workload, family, library).

Decomposes shrinking cost into search volume and per-execution cost, and
breaks down what the shrinking executions are spent on.

Metrics (all per Failed trial, default shrink budget; "edit" = reduction
in tree-edit-distance to ground truth, d = pre_ted_to_gt - ted_to_gt):

  execs/edit   total shrinking executions per edit  -> sample efficiency
  ms/edit      shrink time (ms) per edit            -> ms/edit = execs/edit * ms/exec
  ms/exec      shrink time (ms) per execution       -> per-execution cost

  pass/fail/discard  of the shrinking executions, how many were
                     passed (valid candidate, bug not reproduced),
                     failed (accepted shrink, bug reproduced), or
                     discarded (candidate violates the precondition).

Trials with d <= 0 (no edit-distance improvement) are excluded from the
per-edit metrics since the ratio is undefined.

Usage: .venv/bin/python scripts/workload_shrink_effort.py
Output: figures/SHRINK_EFFORT.md
"""

import csv
import statistics
from collections import defaultdict

from workload_config import ROOT, WORKLOADS, display_name

# Three core libraries per family. CBC uses QuickCBC (bst/rbt) or
# Correct (stlc/fsub); idiomatic CBC2 variants are excluded.
CORE = {
    "vanilla": ["Quick", "Hedgehog", "Falsify"],
    "qbe":     ["QuickGbE", "HedgehogGbE", "FalsifyGbE"],
    "cbc-bstrbt":  ["QuickCBC", "HedgehogCBC", "FalsifyCBC"],
    "cbc-stlcfsub": ["Correct", "HedgehogCBC", "FalsifyCBC"],
}


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def family_groups(wl_name):
    """Yield (family_label, [3 library strategies]) for a workload."""
    fams = WORKLOADS[wl_name]["families"]
    for fam in ("vanilla", "qbe", "cbc"):
        if fam not in fams:
            continue
        if fam == "cbc":
            key = "cbc-bstrbt" if "QuickCBC" in fams["cbc"] else "cbc-stlcfsub"
            yield "cbc", CORE[key]
        else:
            yield fam, CORE[fam]


def median(xs):
    return statistics.median(xs) if xs else float("nan")


def main():
    out = ["# Shrinking sample-efficiency — per (workload, family, library)",
           "",
           "Failed trials, default shrink budget. edit = reduction in TED to",
           "ground truth (d = pre_ted_to_gt - ted_to_gt); trials with d <= 0",
           "excluded from per-edit metrics. ms/edit = execs/edit * ms/exec.",
           ""]

    for wl_name in ("bst", "rbt", "stlc", "fsub"):
        csv_path = ROOT / "figures" / f"{wl_name.upper()}_ANALYSIS.csv"
        if not csv_path.exists():
            out.append(f"## {wl_name.upper()} — MISSING {csv_path.name}\n")
            continue
        rows = [r for r in csv.DictReader(csv_path.open())
                if r["mode"] == "default" and r["status"] == "Failed"]

        for fam, libs in family_groups(wl_name):
            out.append(f"## {wl_name.upper()} / {fam}")
            out.append("")
            out.append("| library | execs/edit | ms/edit | ms/exec | "
                       "med pass/fail/disc | pooled %pass/%fail/%disc |")
            out.append("|---|--:|--:|--:|--:|--:|")
            for s in libs:
                epe, mpe, mpx = [], [], []
                P, F, D = [], [], []
                for r in rows:
                    if r["strategy"] != s:
                        continue
                    sp = fnum(r["shrinking_passed"])
                    sf = fnum(r["shrinking_failed"])
                    sd = fnum(r["shrinking_discarded"])
                    if None in (sp, sf, sd):
                        continue
                    P.append(sp); F.append(sf); D.append(sd)
                    pre = fnum(r["pre_ted_to_gt"])
                    post = fnum(r["ted_to_gt"])
                    t = fnum(r["time_shrinking"])
                    if None in (pre, post, t) or pre - post <= 0:
                        continue
                    d = pre - post
                    execs = sp + sf + sd
                    epe.append(execs / d)
                    mpe.append(t * 1000 / d)
                    if execs > 0:
                        mpx.append(t * 1000 / execs)
                if not P:
                    out.append(f"| {display_name(s)} | — | — | — | — | — |")
                    continue
                tot = sum(P) + sum(F) + sum(D)
                pct = (lambda v: 100 * v / tot if tot else 0.0)
                out.append(
                    f"| {display_name(s)} "
                    f"| {median(epe):.2f} | {median(mpe):.4f} | {median(mpx):.5f} "
                    f"| {median(P):.0f}/{median(F):.0f}/{median(D):.0f} "
                    f"| {pct(sum(P)):.1f}/{pct(sum(F)):.1f}/{pct(sum(D)):.1f} |")
            out.append("")

    dest = ROOT / "figures" / "SHRINK_EFFORT.md"
    dest.write_text("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
