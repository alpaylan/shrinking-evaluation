#!/usr/bin/env python3
"""Emit the appendix statistical-comparison tables for the paper.

For every (workload, generator family), runs a Friedman omnibus test
across tasks plus post-hoc Holm-corrected pairwise Wilcoxon signed-rank
tests, for each of the three shrinking metrics. Writes one longtable per
workload into ShrinkingEval/appendix_stats.tex, which paper.tex \\input-s.

Reuses the analysis from scripts/workload_friedman.py.

Run: .venv/bin/python scripts/gen_stats_tables.py
"""

import csv
import itertools
import statistics
from collections import defaultdict

from scipy.stats import friedmanchisquare, rankdata, wilcoxon

from workload_config import ROOT, display_name
from workload_friedman import (CORE, METRICS, fnum, holm, rank_biserial,
                               family_groups)

OUT = ROOT / "ShrinkingEval" / "appendix_stats.tex"

WL_NAMES = {"bst": "BST", "rbt": "RBT", "stlc": "STLC", "fsub": "$F_{<:}$"}
FAM_NAMES = {
    "vanilla": "Type-based generators",
    "qbe": "Generation-by-execution generators",
    "cbc": "Correct-by-construction generators",
}
METRIC_NAMES = {
    "ted-to-gt": "TED to ground truth",
    "cex-size": "Counterexample size",
    "time-shrinking-ms": "Shrink time (ms)",
    "ms-per-edit": "Time per edit (ms)",
}


def fmt_p(p):
    if p < 1e-3:
        return r"$<\!0.001$"
    return f"${p:.3f}$"


def per_task_medians(rows, libs, vfn):
    vals = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["strategy"] not in libs:
            continue
        v = vfn(r)
        if v is not None:
            vals[r["strategy"]][(r["property"], r["mutation"])].append(v)
    if not all(vals[s] for s in libs):
        return [], {}
    common = sorted(set.intersection(*[set(vals[s]) for s in libs]))
    return common, {s: [statistics.median(vals[s][t]) for t in common]
                    for s in libs}


def metric_block(rows, libs, vfn):
    """Return (latex rows) for one metric, or None if too few tasks."""
    common, m = per_task_medians(rows, libs, vfn)
    if len(common) < 3:
        return None
    n = len(common)
    chi, p = friedmanchisquare(*[m[s] for s in libs])
    pairs = list(itertools.combinations(libs, 2))
    raw, info = [], []
    for a, b in pairs:
        try:
            _, pp = wilcoxon(m[a], m[b])
        except ValueError:
            pp = 1.0
        raw.append(pp)
        diffs = [x - y for x, y in zip(m[a], m[b])]
        r, _ = rank_biserial(diffs)
        info.append((a, b, statistics.median(diffs), r))
    adj = holm(raw)
    out = [(f"Friedman ($N\\!=\\!{n}$)",
            f"\\multicolumn{{2}}{{c}}{{$\\chi^2\\!=\\!{chi:.1f}$}}",
            fmt_p(p), "---")]
    for (a, b, mdiff, r), pr, pa in zip(info, raw, adj):
        out.append((f"{display_name(a)} vs.\\ {display_name(b)}",
                    f"${mdiff:+.1f}$ & ${r:+.2f}$", fmt_p(pr), fmt_p(pa)))
    return out


def main():
    fn_gt = (
        "Tree edit distance to ground truth, and time per edit, both require "
        "the minimal counterexample established by the exhaustive LeanCheck "
        "search. This exists for every task of BST, STLC, and $F_{<:}$, but "
        "for only 34 of RBT's 58 tasks---the remaining 24 are too deep for "
        "exhaustive search. Tasks without a ground truth are excluded from "
        "these two metrics, lowering their $N$ relative to shrink time.")
    fn_edit = (
        "Time per edit ($\\mathrm{ms}/\\Delta\\mathrm{TED}$) is undefined "
        "when shrinking produces no reduction in edit distance to the "
        "ground truth ($d \\le 0$); such tasks are excluded from this metric "
        "only, which can lower its $N$ slightly even where ground truth is "
        "complete.")
    lines = [
        r"\section{Full Statistical Comparison}\label{app:stats}",
        "",
        "The tables below give, for every (workload, generator family), the "
        "Friedman omnibus test across tasks and the post-hoc Holm-corrected "
        "pairwise Wilcoxon signed-rank tests, for three shrinking metrics: "
        "tree edit distance to the ground-truth minimum,\\footnote{" + fn_gt
        + "} shrink time, and time per edit.\\footnote{" + fn_edit + "} "
        "Per-task values are trial medians; all metrics are lower-is-better. "
        "$\\Delta$ is the median per-task difference (first minus second "
        "library) and $r$ the matched-pairs rank-biserial effect size "
        "(negative $\\Rightarrow$ first library better). The reported $N$ is "
        "the number of tasks on which all three libraries have a value for "
        "that metric.",
        "",
    ]

    for wl in ("bst", "rbt", "stlc", "fsub"):
        csv_path = ROOT / "figures" / f"{wl.upper()}_ANALYSIS.csv"
        if not csv_path.exists():
            continue
        rows = [r for r in csv.DictReader(csv_path.open())
                if r["mode"] == "default" and r["status"] == "Failed"]

        lines += [
            r"\begin{longtable}{@{}l l r r r@{}}",
            f"\\caption{{Statistical comparison of shrinking metrics for "
            f"{WL_NAMES[wl]}.}}\\label{{tab:stats-{wl}}}\\\\",
            r"\toprule",
            r"Comparison & median $\Delta$ & $r$ & $p$ & $p_{\text{Holm}}$ \\",
            r"\midrule",
            r"\endfirsthead",
            f"\\multicolumn{{5}}{{@{{}}l}}{{\\footnotesize\\itshape "
            f"Table~\\ref{{tab:stats-{wl}}}, {WL_NAMES[wl]}, continued}}\\\\",
            r"\toprule",
            r"Comparison & median $\Delta$ & $r$ & $p$ & $p_{\text{Holm}}$ \\",
            r"\midrule",
            r"\endhead",
            r"\bottomrule",
            r"\endlastfoot",
        ]
        fams = list(family_groups(wl))
        for fi, (fam, libs) in enumerate(fams):
            if fi > 0:
                lines.append(r"\midrule")
            lines.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\textit{{"
                         f"{FAM_NAMES[fam]}}}}}\\\\")
            lines.append(r"\midrule")
            for mkey, vfn in METRICS.items():
                block = metric_block(rows, libs, vfn)
                lines.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\quad "
                             f"\\footnotesize {METRIC_NAMES[mkey]}}}\\\\")
                if block is None:
                    lines.append(r"\multicolumn{5}{@{}l}{\quad\footnotesize "
                                 r"\textit{insufficient tasks}}\\")
                else:
                    for comp, mid, p, ph in block:
                        lines.append(f"\\quad {comp} & {mid} & {p} & {ph} \\\\")
                lines.append(r"\addlinespace")
        lines += [r"\end{longtable}", ""]

    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
