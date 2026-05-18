#!/usr/bin/env python3
"""Reproduce a quantitative claim from the paper.

Each claim Cn in REPRODUCTION.md maps to a handler here. Run:

    .venv/bin/python scripts/reproduce.py C3
    .venv/bin/python scripts/reproduce.py all

Tier-1 reproduction: recomputes the number from the existing
figures/*_ANALYSIS.csv files (produced by scripts/workload_analysis.py)
and the store.*.jsonl files. See REPRODUCTION.md for Tier-2 (regenerating
the stores from scratch).
"""

import csv
import itertools
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workload_config import ROOT  # noqa: E402

try:
    from scipy.stats import friedmanchisquare, rankdata, wilcoxon
except ImportError:
    friedmanchisquare = rankdata = wilcoxon = None

WORKLOADS = ["bst", "rbt", "stlc", "fsub"]
VANILLA = ["Quick", "Hedgehog", "Falsify"]
QBE = ["QuickGbE", "HedgehogGbE", "FalsifyGbE"]


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def cbc_libs(wl):
    return ["QuickCBC", "HedgehogCBC", "FalsifyCBC"] if wl in ("bst", "rbt") \
        else ["Correct", "HedgehogCBC", "FalsifyCBC"]


def load_csv(wl, mode="default", status="Failed"):
    p = ROOT / "figures" / f"{wl.upper()}_ANALYSIS.csv"
    if not p.exists():
        raise SystemExit(f"missing {p.name}; run: "
                         f".venv/bin/python scripts/workload_analysis.py --workload {wl}")
    out = []
    for r in csv.DictReader(p.open()):
        if mode and r["mode"] != mode:
            continue
        if status and r["status"] != status:
            continue
        out.append(r)
    return out


def med(xs):
    return statistics.median(xs) if xs else float("nan")


def per_task_medians(rows, libs, valuefn):
    """{lib: [per-task median]} over tasks common to all libs."""
    vals = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["strategy"] not in libs:
            continue
        v = valuefn(r)
        if v is not None:
            vals[r["strategy"]][(r["property"], r["mutation"])].append(v)
    if not all(vals[s] for s in libs):
        return [], {}
    common = sorted(set.intersection(*[set(vals[s]) for s in libs]))
    return common, {s: [statistics.median(vals[s][t]) for t in common] for s in libs}


def holm(pvals):
    """Holm-Bonferroni adjusted p-values, aligned to input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def posthoc_wilcoxon(rows, libs, valuefn):
    """Holm-corrected pairwise Wilcoxon signed-rank on per-task medians.

    Returns [(a, b, median_diff, p_raw, p_holm), ...].
    """
    common, m = per_task_medians(rows, libs, valuefn)
    pairs = list(itertools.combinations(libs, 2))
    raw = []
    for a, b in pairs:
        try:
            _, p = wilcoxon(m[a], m[b])
        except ValueError:
            p = 1.0
        raw.append(p)
    adj = holm(raw)
    return [(a, b, statistics.median([x - y for x, y in zip(m[a], m[b])]), pr, pa)
            for (a, b), pr, pa in zip(pairs, raw, adj)]


def friedman(rows, libs, valuefn):
    common, m = per_task_medians(rows, libs, valuefn)
    if len(common) < 3:
        return None
    chi, p = friedmanchisquare(*[m[s] for s in libs])
    rs = {s: 0.0 for s in libs}
    for i in range(len(common)):
        for s, rk in zip(libs, rankdata([m[s][i] for s in libs])):
            rs[s] += rk
    avg = {s: rs[s] / len(common) for s in libs}
    order = sorted(libs, key=lambda s: avg[s])
    return len(common), chi, p, avg, order


# ---- metric value functions ----
def v_ted(r):       return fnum(r.get("ted_to_gt"))
def v_time(r):      t = fnum(r.get("time_shrinking")); return None if t is None else t * 1000
def v_pre(r):       return fnum(r.get("pre_ted_to_gt"))


def v_msedit(r):
    pre, post, t = fnum(r.get("pre_ted_to_gt")), fnum(r.get("ted_to_gt")), fnum(r.get("time_shrinking"))
    if None in (pre, post, t) or pre - post <= 0:
        return None
    return t * 1000 / (pre - post)


# ============================ CLAIM HANDLERS ============================

def C1():
    print("C1  Task counts per workload (paper: BST 53, RBT 58, STLC 20, F<: 36)")
    for wl in WORKLOADS:
        tasks = {(r["property"], r["mutation"]) for r in load_csv(wl, status=None)}
        print(f"  {wl:5s}: {len(tasks)} tasks")


def C2():
    print("C2  Shrinking reduction in TED-to-GT, per family (paper lines 734-737:")
    print("    type-based 3-8, GbE 33-41, CBC 18-102)")
    families = [("type-based", lambda wl: VANILLA, WORKLOADS),
                ("GbE", lambda wl: QBE, ["bst", "rbt"]),
                ("CBC", cbc_libs, WORKLOADS)]
    for label, libsfn, wls in families:
        per = []
        for wl in wls:
            libs = libsfn(wl)
            diffs = []
            for r in load_csv(wl):
                if r["strategy"] not in libs:
                    continue
                pre, post = fnum(r["pre_ted_to_gt"]), fnum(r["ted_to_gt"])
                if pre is not None and post is not None:
                    diffs.append(pre - post)
            if diffs:
                per.append((wl, statistics.median(diffs)))
        cells = "  ".join(f"{wl}={m:.1f}" for wl, m in per)
        lo, hi = min(m for _, m in per), max(m for _, m in per)
        print(f"  {label:11s}: {cells}   range {lo:.1f}-{hi:.1f}")


def C3():
    print("C3  Type-based shrink time: QC≈Hedgehog, Falsify ~order of magnitude slower")
    for wl in WORKLOADS:
        rows = load_csv(wl)
        m = {s: med([v_time(r) for r in rows if r["strategy"] == s and v_time(r) is not None])
             for s in VANILLA}
        if m["Quick"] != m["Quick"]:  # nan
            print(f"  {wl:5s}: insufficient data"); continue
        print(f"  {wl:5s}: Quick={m['Quick']:.3f}ms  Hedgehog={m['Hedgehog']:.3f}ms  "
              f"Falsify={m['Falsify']:.3f}ms  | Falsify/Quick={m['Falsify']/m['Quick']:.1f}x")


def C4():
    print("C4  Falsify long tail: up to ~4 orders of magnitude slower on some tasks")
    worst = 0.0
    for wl in WORKLOADS:
        common, m = per_task_medians(load_csv(wl), VANILLA, v_time)
        for i in range(len(common)):
            others = min(m["Quick"][i], m["Hedgehog"][i])
            if others > 0:
                ratio = m["Falsify"][i] / others
                worst = max(worst, ratio)
    print(f"  max per-task Falsify/(faster of QC,HH) time ratio = {worst:.0f}x "
          f"(~{len(str(int(worst)))-1} orders of magnitude)")


def C5():
    print("C5  Shrink-budget semantics (source/docs claim, not a measurement)")
    print("  QuickCheck  maxShrinks        -> caps ALL shrink executions")
    print("  Hedgehog    withShrinks       -> caps ACCEPTED (failing) shrinks")
    print("  Falsify     overrideMaxShrinks-> caps shrink STEPS (accepted shrink chain)")
    print("  verify in: workloads/bst-haskell/etna-lib/src/Etna/Lib/Strategy/"
          "{QuickCheck,Hedgehog,Falsify}.hs")


def C6():
    print("C6  budget=0 vs budget=default: bug-finding failure rate (no notable overhead)")
    for wl in WORKLOADS:
        for mode, label in [("none", "budget=0"), ("default", "budget=default")]:
            rows = load_csv(wl, mode=mode, status=None) if mode != "none" or wl != "fsub" else None
            if rows is None:
                # fsub has no shrink-0 in the CSV; read the store directly
                fr = tot = 0
                for fw in ("quick", "hedgehog", "falsify"):
                    p = ROOT / f"store.fsub.{fw}.shrink-0.jsonl"
                    if not p.exists():
                        continue
                    for ln in p.read_text().splitlines():
                        if not ln.strip():
                            continue
                        d = json.loads(ln)["data"]
                        if d["strategy"] in VANILLA:
                            tot += 1
                            fr += d["status"] == "Failed"
                rate = fr / tot if tot else float("nan")
            else:
                van = [r for r in rows if r["strategy"] in VANILLA]
                fr = sum(r["status"] == "Failed" for r in van)
                rate = fr / len(van) if van else float("nan")
            print(f"  {wl:5s} {label:16s}: failure rate = {rate:.3f}")


def C7():
    print("C7  budget=100 vs default: total shrinking executions (BST only; ~no change)")
    rows_all = {m: load_csv("bst", mode=m) for m in ("fixed-100", "default")}
    for s in VANILLA:
        line = f"  {s:9s}: "
        for m in ("fixed-100", "default"):
            tot = [fnum(r["shrinking_passed"]) + fnum(r["shrinking_failed"])
                   + fnum(r["shrinking_discarded"])
                   for r in rows_all[m] if r["strategy"] == s
                   and None not in (fnum(r["shrinking_passed"]), fnum(r["shrinking_failed"]),
                                    fnum(r["shrinking_discarded"]))]
            line += f"{m}: median execs={med(tot):.0f}   "
        print(line)


def _friedman_line(wl, fam_label, libs):
    res = friedman(load_csv(wl), libs, v_time)
    if res is None:
        print(f"  {wl:5s} {fam_label}: insufficient data"); return
    n, chi, p, avg, order = res
    ranks = "  ".join(f"{s}={avg[s]:.2f}" for s in libs)
    print(f"  {wl:5s} {fam_label}: Friedman p={p:.4g}  ranks[{ranks}]  "
          f"order: {' < '.join(order)}")


def C8():
    print("C8  CBC BST/RBT shrink time: QuickCheck & Hedgehog tied, Falsify slower")
    for wl in ("bst", "rbt"):
        _friedman_line(wl, "cbc", cbc_libs(wl))


def C9():
    print("C9  CBC STLC/F<: shrink time: QuickCheck < Hedgehog < Falsify")
    for wl in ("stlc", "fsub"):
        _friedman_line(wl, "cbc", cbc_libs(wl))


def C10():
    print("C10  ms-per-edit vs absolute time: consistent for QuickCheck & Hedgehog")
    for wl in WORKLOADS:
        rows = load_csv(wl)
        rt = friedman(rows, VANILLA, v_time)
        rm = friedman(rows, VANILLA, v_msedit)
        if rt is None or rm is None:
            print(f"  {wl:5s}: insufficient data"); continue
        ot = " < ".join(rt[4]); om = " < ".join(rm[4])
        print(f"  {wl:5s} vanilla: time order [{ot}]  ms/edit order [{om}]")


def C11():
    print("C11  Falsify GbE pre-shrink TED ≈ 150 vs 15-20 for QuickCheck/Hedgehog")
    for wl in ("bst", "rbt"):
        rows = load_csv(wl)
        for s in QBE:
            pre = [v_pre(r) for r in rows if r["strategy"] == s and v_pre(r) is not None]
            print(f"  {wl:5s} {s:13s}: median pre-shrink TED = {med(pre):.0f}")


def C12():
    print("C12  Per-edit collapses Falsify/Quick gap: 31x/96x (time) -> 3.7x/2.4x (ms/edit)")
    for wl in ("bst", "rbt"):
        rows = load_csv(wl)
        def m(s, fn): return med([fn(r) for r in rows if r["strategy"] == s and fn(r) is not None])
        t = m("FalsifyGbE", v_time) / m("QuickGbE", v_time)
        e = m("FalsifyGbE", v_msedit) / m("QuickGbE", v_msedit)
        print(f"  {wl:5s}: Falsify/Quick  absolute time={t:.1f}x   ms-per-edit={e:.1f}x")


def C13():
    print("C13  CBC shrink failure(=accepted) rate: Hedgehog 30-60%, QC 3-10%, Falsify 2%")
    for wl in WORKLOADS:
        rows = load_csv(wl)
        for s in cbc_libs(wl):
            P = F = D = 0.0
            for r in rows:
                if r["strategy"] != s:
                    continue
                sp, sf, sd = (fnum(r["shrinking_passed"]), fnum(r["shrinking_failed"]),
                              fnum(r["shrinking_discarded"]))
                if None in (sp, sf, sd):
                    continue
                P += sp; F += sf; D += sd
            tot = P + F + D
            if tot:
                print(f"  {wl:5s} {s:13s}: %fail = {100*F/tot:.1f}%   %disc = {100*D/tot:.1f}%")


def C14():
    print("C14  QuickCheck structural shrinking discards up to ~70% of candidates")
    worst = 0.0
    for wl in WORKLOADS:
        rows = load_csv(wl)
        qc = "QuickCBC" if wl in ("bst", "rbt") else "Correct"
        for s in (qc, "QuickGbE"):
            P = F = D = 0.0
            for r in rows:
                if r["strategy"] != s:
                    continue
                sp, sf, sd = (fnum(r["shrinking_passed"]), fnum(r["shrinking_failed"]),
                              fnum(r["shrinking_discarded"]))
                if None in (sp, sf, sd):
                    continue
                P += sp; F += sf; D += sd
            tot = P + F + D
            if tot:
                pct = 100 * D / tot
                worst = max(worst, pct)
                print(f"  {wl:5s} {s:13s}: %discarded = {pct:.1f}%")
    print(f"  -> peak QuickCheck discard rate = {worst:.1f}%")


def C15():
    print("C15  GbE pairwise: Friedman + post-hoc Holm-Wilcoxon on TED-to-GT (lines 723-726)")
    for wl in ("bst", "rbt"):
        rows = load_csv(wl)
        n, chi, p, avg, order = friedman(rows, QBE, v_ted)
        print(f"  {wl:5s}: Friedman chi2={chi:.1f}, p={p:.4g}  (N={n} tasks)")
        for a, b, mdiff, pr, pa in posthoc_wilcoxon(rows, QBE, v_ted):
            sig = "n.s." if pa >= 0.05 else "significant"
            print(f"    {a:13s} vs {b:13s}: median Δ={mdiff:+.1f}  p={pr:.4g}  p_Holm={pa:.4g}  {sig}")


def C16():
    print("C16  Idiomatic BST CBC generators: Falsify no change, Hedgehog +2 (lines 728-729)")
    rows = load_csv("bst")
    for base, idiom in [("HedgehogCBC", "HedgehogCBC2"), ("FalsifyCBC", "FalsifyCBC2")]:
        common, m = per_task_medians(rows, [base, idiom], v_ted)
        if len(common) < 3:
            print(f"  {base} -> {idiom}: insufficient data"); continue
        diffs = [b - i for b, i in zip(m[base], m[idiom])]
        try:
            _, p = wilcoxon(m[base], m[idiom])
        except ValueError:
            p = 1.0
        print(f"  {base} -> {idiom}: median improvement = {med(diffs):.1f} edit distance  "
              f"p={p:.4g}  (N={len(common)})")


def C17():
    print("C17  CBC shrinking effectiveness (TED-to-GT) ranking per workload (lines 730,734-735)")
    for wl in WORKLOADS:
        res = friedman(load_csv(wl), cbc_libs(wl), v_ted)
        if res is None:
            print(f"  {wl:5s}: insufficient data"); continue
        n, chi, p, avg, order = res
        ranks = "  ".join(f"{s}={avg[s]:.2f}" for s in cbc_libs(wl))
        print(f"  {wl:5s}: Friedman p={p:.4g}  order: {' < '.join(order)}  [{ranks}]")


def C18():
    print("C18  QuickCheck TED-to-GT ~identical across GbE/CBC; HH & Falsify vary (lines 730-732)")
    for wl in ("bst", "rbt"):
        rows = load_csv(wl)
        for lib, g, c in [("Quick", "QuickGbE", "QuickCBC"),
                          ("Hedgehog", "HedgehogGbE", "HedgehogCBC"),
                          ("Falsify", "FalsifyGbE", "FalsifyCBC")]:
            common, m = per_task_medians(rows, [g, c], v_ted)
            if len(common) < 3:
                print(f"  {wl:5s} {lib:9s}: insufficient data"); continue
            try:
                _, p = wilcoxon(m[g], m[c])
            except ValueError:
                p = 1.0
            verdict = "identical (n.s.)" if p >= 0.05 else "differ"
            print(f"  {wl:5s} {lib:9s}: GbE vs CBC TED-to-GT  p={p:.4g}  -> {verdict}")


def C19():
    print("C19  RBT ground-truth task split: 34 with ground truth, 24 too deep (lines 737-738)")
    gt = set()
    for ln in (ROOT / "store.rbt.det.jsonl").read_text().splitlines():
        if not ln.strip():
            continue
        d = json.loads(ln)["data"]
        if d["strategy"] in ("Lean", "LeanRev") and d["status"] == "Failed" \
                and (d.get("counterexample") or d.get("pre_counterexample")):
            prop = d["property"]
            prop = prop[5:] if prop.startswith("prop_") else prop
            gt.add((prop, ",".join(d.get("mutations", []) or [])))
    allt = {(r["property"], r["mutation"]) for r in load_csv("rbt", status=None)}
    print(f"  RBT total tasks = {len(allt)}  |  with ground truth = {len(allt & gt)}  "
          f"|  too deep = {len(allt - gt)}")


CLAIMS = {f"C{i}": fn for i, fn in enumerate(
    [None, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14,
     C15, C16, C17, C18, C19])
    if fn}


def main():
    if len(sys.argv) != 2 or (sys.argv[1] not in CLAIMS and sys.argv[1] != "all"):
        raise SystemExit(f"usage: reproduce.py <{'|'.join(CLAIMS)}|all>")
    targets = CLAIMS.values() if sys.argv[1] == "all" else [CLAIMS[sys.argv[1]]]
    for fn in targets:
        fn()
        print()


if __name__ == "__main__":
    main()
