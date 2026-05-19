#!/usr/bin/env python3
"""Friedman omnibus + post-hoc Holm-Wilcoxon comparison of the three
PBT libraries, per (workload, generator family, metric).

Design (Demšar 2006; García & Herrera 2008): each (property, mutation)
task is a "data set"; each library is an "algorithm". Trials within a
task are collapsed to a per-task median, then the three libraries are
compared with a Friedman omnibus test across tasks. On rejection, we
run Holm-corrected pairwise Wilcoxon signed-rank post-hoc tests.

All metrics are lower-is-better. Effect size for the post-hoc is the
matched-pairs rank-biserial correlation r (sign: negative ⇒ A better).

Usage: .venv/bin/python scripts/workload_friedman.py
"""

import csv
import itertools
import statistics
from collections import defaultdict

from scipy.stats import friedmanchisquare, wilcoxon, rankdata

from workload_config import ROOT, WORKLOADS, display_name

ALPHA = 0.05


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---- metric value functions (lower is better) ----

def value_ted(r):
    return fnum(r.get("ted_to_gt"))


def value_cex_size(r):
    return fnum(r.get("cex_size"))


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
    "ted-to-gt": value_ted,
    "cex-size": value_cex_size,
    "time-shrinking-ms": value_time_shrinking_ms,
    "ms-per-edit": value_ms_per_edit,
}

# The three core libraries per family. CBC uses QuickCBC/Correct;
# idiomatic CBC2 variants are excluded from the 3-way library test.
CORE = {
    "vanilla": ["Quick", "Hedgehog", "Falsify"],
    "qbe":     ["QuickGbE", "HedgehogGbE", "FalsifyGbE"],
    "cbc-bstrbt": ["QuickCBC", "HedgehogCBC", "FalsifyCBC"],
    "cbc-stlcfsub": ["Correct", "HedgehogCBC", "FalsifyCBC"],
}


def holm(pvals):
    """Holm-Bonferroni adjusted p-values, aligned to input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def rank_biserial(diffs):
    """Matched-pairs rank-biserial: (R+ - R-)/(R+ + R-) over nonzero diffs."""
    d = [x for x in diffs if x != 0]
    if not d:
        return 0.0, 0
    ranks = rankdata([abs(x) for x in d])
    rp = sum(rk for rk, x in zip(ranks, d) if x > 0)
    rn = sum(rk for rk, x in zip(ranks, d) if x < 0)
    return (rp - rn) / (rp + rn), len(d)


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


def main():
    out = ["# Friedman + post-hoc Holm-Wilcoxon — library comparison",
           "",
           "Per (workload, family, metric): Friedman omnibus across tasks on",
           "per-task medians; on rejection, Holm-corrected pairwise Wilcoxon",
           "signed-rank post-hoc. Lower is better. r = matched-pairs rank-biserial",
           "(negative ⇒ first library better).",
           ""]

    for wl_name in ("bst", "rbt", "stlc", "fsub"):
        csv_path = ROOT / "figures" / f"{wl_name.upper()}_ANALYSIS.csv"
        if not csv_path.exists():
            out.append(f"## {wl_name.upper()} — MISSING {csv_path.name}\n")
            continue
        rows = [r for r in csv.DictReader(csv_path.open())
                if r["mode"] == "default" and r["status"] == "Failed"]

        for fam, libs in family_groups(wl_name):
            out.append(f"## {wl_name.upper()} / {fam}  ({', '.join(display_name(s) for s in libs)})")
            out.append("")
            for m, vfn in METRICS.items():
                # values[strategy][task] -> list of trial values
                vals = defaultdict(lambda: defaultdict(list))
                for r in rows:
                    if r["strategy"] not in libs:
                        continue
                    v = vfn(r)
                    if v is not None:
                        vals[r["strategy"]][(r["property"], r["mutation"])].append(v)
                # tasks where all three libraries have data
                tasksets = [set(vals[s]) for s in libs]
                common = sorted(set.intersection(*tasksets)) if all(tasksets) else []
                if len(common) < 3:
                    out.append(f"- **{m}**: only {len(common)} common tasks — skipped")
                    continue
                med = {s: [statistics.median(vals[s][t]) for t in common] for s in libs}
                chi, p = friedmanchisquare(*[med[s] for s in libs])
                # average ranks (1 = best = smallest)
                rsum = {s: 0.0 for s in libs}
                for i in range(len(common)):
                    rk = rankdata([med[s][i] for s in libs])
                    for s, v in zip(libs, rk):
                        rsum[s] += v
                avg = {s: rsum[s] / len(common) for s in libs}
                ranks_str = " · ".join(f"{display_name(s)} {avg[s]:.2f}" for s in libs)
                verdict = "REJECT" if p < ALPHA else "n.s."
                out.append(f"- **{m}**  (N={len(common)} tasks)")
                out.append(f"  - Friedman χ²={chi:.2f}, p={p:.4g} → **{verdict}**  | avg ranks: {ranks_str}")
                if p < ALPHA:
                    raw, info = [], []
                    for A, B in itertools.combinations(libs, 2):
                        diffs = [x - y for x, y in zip(med[A], med[B])]
                        try:
                            _, pp = wilcoxon(med[A], med[B])
                        except ValueError:
                            pp = 1.0
                        r, nz = rank_biserial(diffs)
                        raw.append(pp)
                        info.append((A, B, statistics.median(diffs), nz, r))
                    adj = holm(raw)
                    for (A, B, mdiff, nz, r), pa, pr in zip(info, adj, raw):
                        star = ("***" if pa < 0.001 else "**" if pa < 0.01
                                else "*" if pa < 0.05 else "n.s.")
                        out.append(f"    - {display_name(A)} vs {display_name(B)}: "
                                   f"median Δ={mdiff:+.2f}, nonzero={nz}/{len(common)}, "
                                   f"r={r:+.3f}, p={pr:.4g}, p_Holm={pa:.4g} {star}")
            out.append("")

    dest = ROOT / "figures" / "STATS_FRIEDMAN.md"
    dest.write_text("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
