#!/usr/bin/env python3
"""Reproduce a quantitative claim from the paper.

Each claim Cn in REPRODUCTION.md maps to a handler here. Run:

    .venv/bin/python scripts/reproduce.py C3
    .venv/bin/python scripts/reproduce.py all

Handlers re-compute the number from figures/*_ANALYSIS.csv (produced by
scripts/workload_analysis.py) and the store.*.jsonl files. See
REPRODUCTION.md for the anchor phrase, expected value, and paper line.
"""

import csv
import itertools
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workload_config import ROOT, display_name  # noqa: E402

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
def v_bug(r):       t = fnum(r.get("time_pre_failure")); return None if t is None else t * 1000
def v_pre(r):       return fnum(r.get("pre_ted_to_gt"))


def v_reduction(r):
    pre, post = fnum(r.get("pre_ted_to_gt")), fnum(r.get("ted_to_gt"))
    if pre is None or post is None:
        return None
    return pre - post


def v_msedit(r):
    pre, post, t = fnum(r.get("pre_ted_to_gt")), fnum(r.get("ted_to_gt")), fnum(r.get("time_shrinking"))
    if None in (pre, post, t) or pre - post <= 0:
        return None
    return t * 1000 / (pre - post)


def _bugfind_lines(wl, families):
    """Friedman + Holm-Wilcoxon on bug-finding time across families."""
    rows = load_csv(wl)
    for fname, libs in families:
        res = friedman(rows, libs, v_bug)
        if res is None:
            print(f"  {fname:8s}: insufficient data"); continue
        n, chi, p, avg, order = res
        ord_s = " < ".join(display_name(s) for s in order)
        sig = "significant" if p < 0.05 else "n.s."
        print(f"  {fname:8s}: Friedman N={n}  chi2={chi:.1f}  p={p:.3g}  ({sig})  order: {ord_s}")
        for a, b, mdiff, pr, pa in posthoc_wilcoxon(rows, libs, v_bug):
            tag = "n.s." if pa >= 0.05 else "significant"
            print(f"      {display_name(a):13s} vs {display_name(b):13s}: "
                  f"median Δ={mdiff:+8.2f}ms  p_Holm={pa:.4g}  {tag}")


# ============================ CLAIM HANDLERS ============================

def C1():
    print("C1  Task counts per workload (paper §4.1: BST 53, RBT 58, STLC 20, F<: 36)")
    for wl in WORKLOADS:
        tasks = {(r["property"], r["mutation"]) for r in load_csv(wl, status=None)}
        print(f"  {wl:5s}: {len(tasks)} tasks")


def C2():
    print("C2  Shrinking reduction in TED-to-GT (paper §4.2.2: type-based 3-10 per workload,")
    print("    GbE 41-44, CBC 18-106 -- median across per-(task,library) trial-medians)")
    families = [("type-based", lambda wl: VANILLA, WORKLOADS),
                ("GbE",        lambda wl: QBE,     ["bst", "rbt"]),
                ("CBC",        cbc_libs,           WORKLOADS)]
    for label, libsfn, wls in families:
        cells = []
        for wl in wls:
            libs = libsfn(wl)
            pertask = defaultdict(list)
            for r in load_csv(wl):
                if r["strategy"] not in libs:
                    continue
                v = v_reduction(r)
                if v is not None:
                    pertask[(r["strategy"], r["property"], r["mutation"])].append(v)
            meds = [statistics.median(v) for v in pertask.values() if v]
            if meds:
                cells.append((wl, statistics.median(meds), len(meds)))
        if cells:
            txt = "  ".join(f"{wl}={m:.1f} (N={n})" for wl, m, n in cells)
            lo, hi = min(m for _, m, _ in cells), max(m for _, m, _ in cells)
            print(f"  {label:11s}: {txt}   range {lo:.1f}-{hi:.1f}")


def C3():
    print("C3  BST bug-finding (paper §4.2.1: type-based & GbE significant p<0.001, CBC indistinguishable)")
    _bugfind_lines("bst", [("vanilla", VANILLA), ("GbE", QBE), ("CBC", cbc_libs("bst"))])


def C4():
    print("C4  RBT bug-finding (paper §4.2.1: all 3 families significant p<0.001;")
    print("    QC < HH/Falsify everywhere; Falsify vs HH GbE n.s. after Holm)")
    _bugfind_lines("rbt", [("vanilla", VANILLA), ("GbE", QBE), ("CBC", cbc_libs("rbt"))])


def C5():
    print("C5  STLC bug-finding (paper §4.2.1: type-based n.s., CBC p<0.001; HH≈Falsify after Holm)")
    _bugfind_lines("stlc", [("vanilla", VANILLA), ("CBC", cbc_libs("stlc"))])


def C6():
    print("C6  F<: bug-finding (paper §4.2.1: type-based p<0.001 with QC<Falsify<HH; CBC same shape)")
    _bugfind_lines("fsub", [("vanilla", VANILLA), ("CBC", cbc_libs("fsub"))])


def C7():
    print("C7  CBC shrinking effectiveness (TED-to-GT) ranking per workload (paper §4.2.2)")
    print("    expected: BST/RBT QuickCBC closest; STLC FalsifyCBC closest; F<: QuickCBC < FalsifyCBC < HedgehogCBC")
    for wl in WORKLOADS:
        res = friedman(load_csv(wl), cbc_libs(wl), v_ted)
        if res is None:
            print(f"  {wl:5s}: insufficient data"); continue
        n, chi, p, avg, order = res
        ord_s = " < ".join(display_name(s) for s in order)
        ranks = "  ".join(f"{display_name(s)}={avg[s]:.2f}" for s in cbc_libs(wl))
        print(f"  {wl:5s}: Friedman p={p:.3g}  order: {ord_s}  [{ranks}]")


def C8():
    print("C8  RBT GbE TED-to-GT statistically indistinguishable (paper §4.2.2: appendix χ²=1.8, p=0.415)")
    rows = load_csv("rbt")
    res = friedman(rows, QBE, v_ted)
    if res is None:
        print("  insufficient data"); return
    n, chi, p, avg, order = res
    print(f"  Friedman N={n}  chi2={chi:.1f}  p={p:.3g}  ({'n.s.' if p >= 0.05 else 'differ'})")
    for a, b, mdiff, pr, pa in posthoc_wilcoxon(rows, QBE, v_ted):
        tag = "n.s." if pa >= 0.05 else "significant"
        print(f"    {a:13s} vs {b:13s}: median Δ={mdiff:+.1f}  p_Holm={pa:.4g}  {tag}")


def C9():
    print("C9  RBT ground-truth task split (paper §4.2.2 footnote: 34 with GT, 24 too deep, 58 total)")
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


def C10():
    print("C10 Type-based shrink time (paper §4.2.3: QC≈Hedgehog, Falsify consistently slower with long tail)")
    for wl in WORKLOADS:
        rows = load_csv(wl)
        m = {s: med([v_time(r) for r in rows if r["strategy"] == s and v_time(r) is not None])
             for s in VANILLA}
        if m["Quick"] != m["Quick"]:
            print(f"  {wl:5s}: insufficient data"); continue
        print(f"  {wl:5s}: Quick={m['Quick']:.3f}ms  Hedgehog={m['Hedgehog']:.3f}ms  "
              f"Falsify={m['Falsify']:.3f}ms  | Falsify/Quick={m['Falsify']/m['Quick']:.1f}x")


def C11():
    print("C11 Falsify long tail: peak per-task slowdown -- paper §4.2.3 'several orders of magnitude'")
    worst = 0.0
    for wl in WORKLOADS:
        common, m = per_task_medians(load_csv(wl), VANILLA, v_time)
        for i in range(len(common)):
            others = min(m["Quick"][i], m["Hedgehog"][i])
            if others > 0:
                worst = max(worst, m["Falsify"][i] / others)
    print(f"  max per-task Falsify/(faster of QC,HH) time ratio = {worst:.0f}x "
          f"(~{len(str(int(worst)))-1} orders of magnitude)")


def C12():
    print("C12 Shrink-budget semantics (paper §4.2.3: QC=total executions, HH/Falsify=failing executions)")
    print("    QuickCheck  maxShrinks         -> caps ALL shrink executions (pass + fail + discard)")
    print("    Hedgehog    withShrinks        -> caps accepted (failing) shrinks")
    print("    Falsify     overrideMaxShrinks -> caps accepted shrink steps (failing chain)")
    print("    verify in: workloads/<wl>-haskell/etna-lib/src/Etna/Lib/Strategy/{QuickCheck,Hedgehog,Falsify}.hs")


def C13():
    print("C13 budget=0 vs budget=default bug-finding rates (paper §4.2.3: 'no-shrinking lets us check the bug-finding overhead')")
    for wl in WORKLOADS:
        for mode, label in [("none", "budget=0"), ("default", "budget=default")]:
            rows = load_csv(wl, mode=mode, status=None) if mode != "none" or wl != "fsub" else None
            if rows is None:
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


def C14():
    print("C14 budget=100 fails to standardize effort across libraries (paper §4.2.3, BST illustration)")
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


def _shrink_time_friedman(wl, label, libs):
    rows = load_csv(wl)
    res = friedman(rows, libs, v_time)
    if res is None:
        print(f"  {wl:5s} {label}: insufficient data"); return
    n, chi, p, avg, order = res
    ord_s = " < ".join(display_name(s) for s in order)
    print(f"  {wl:5s} {label}: Friedman p={p:.3g}  order: {ord_s}")
    for a, b, mdiff, pr, pa in posthoc_wilcoxon(rows, libs, v_time):
        tag = "n.s." if pa >= 0.05 else "significant"
        print(f"      {display_name(a):13s} vs {display_name(b):13s}: median Δ={mdiff:+8.2f}ms  p_Holm={pa:.4g}  {tag}")


def C15():
    print("C15 CBC shrink time order (paper §4.2.3: BST QC fastest; RBT QC≈HH < Falsify; STLC/F<: QC<HH<Falsify)")
    for wl in WORKLOADS:
        _shrink_time_friedman(wl, "cbc", cbc_libs(wl))


def C16():
    print("C16 Per-edit ms order consistent w/ absolute time for QuickCheck & Hedgehog (paper §4.2.3)")
    for wl in WORKLOADS:
        rows = load_csv(wl)
        rt = friedman(rows, VANILLA, v_time)
        rm = friedman(rows, VANILLA, v_msedit)
        if rt is None or rm is None:
            print(f"  {wl:5s}: insufficient data"); continue
        print(f"  {wl:5s} vanilla: time order [{' < '.join(rt[4])}]  "
              f"ms/edit order [{' < '.join(rm[4])}]")


def C17():
    print("C17 Falsify GbE pre-shrink TED ≈ 150 vs 15-20 for QuickCheck/Hedgehog (paper §4.2.3)")
    for wl in ("bst", "rbt"):
        rows = load_csv(wl)
        for s in QBE:
            pre = [v_pre(r) for r in rows if r["strategy"] == s and v_pre(r) is not None]
            print(f"  {wl:5s} {s:13s}: median pre-shrink TED = {med(pre):.0f}")


def C18():
    print("C18 Per-edit collapses Falsify/Quick GbE gap: 49x/96x (time) -> 6.2x/2.4x (ms/edit) (paper §4.2.3)")
    for wl in ("bst", "rbt"):
        rows = load_csv(wl)
        def m(s, fn):
            _, by_strategy = per_task_medians(rows, [s], fn)
            return med(by_strategy[s])
        t = m("FalsifyGbE", v_time) / m("QuickGbE", v_time)
        e = m("FalsifyGbE", v_msedit) / m("QuickGbE", v_msedit)
        print(f"  {wl:5s}: Falsify/Quick  absolute time={t:.1f}x   ms-per-edit={e:.1f}x")


def C19():
    print("C19 CBC per-trial failure rate during shrinking (paper §4.3: HH 26-56%, QC 5-12%, Falsify 2-3%)")
    for wl in WORKLOADS:
        rows = load_csv(wl)
        for s in cbc_libs(wl):
            fail_rates, discard_rates = [], []
            for r in rows:
                if r["strategy"] != s:
                    continue
                sp, sf, sd = (fnum(r["shrinking_passed"]), fnum(r["shrinking_failed"]),
                              fnum(r["shrinking_discarded"]))
                if None in (sp, sf, sd):
                    continue
                tot = sp + sf + sd
                if tot:
                    fail_rates.append(100 * sf / tot)
                    discard_rates.append(100 * sd / tot)
            if fail_rates:
                print(f"  {wl:5s} {display_name(s):13s}: median %fail = {med(fail_rates):.1f}%   "
                      f"median %disc = {med(discard_rates):.1f}%")


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
