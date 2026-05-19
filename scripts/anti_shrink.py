#!/usr/bin/env python3
"""Gather anti-shrink cases: trials where shrinking moved the counterexample
FARTHER from the ground-truth minimum than where it started
(ted_to_gt > pre_ted_to_gt) -- i.e. shrinking made the result worse.

Controls for *false ground truth*: if some observed counterexample for a
task is smaller than the recorded LeanCheck "ground truth", then that
ground truth is not actually minimal and every ted_to_gt for the task is
unreliable. Such tasks are excluded from the genuine anti-shrink count;
pass --false-gt to inspect them directly.

Reads figures/<WL>_ANALYSIS.csv (produced by scripts/workload_analysis.py)
for the TED/size values, joins the matching store rows for the pre/post
counterexample strings, and store.<wl>.det.jsonl for the ground truth.

Usage:
  scripts/anti_shrink.py                          # all workloads
  scripts/anti_shrink.py --workload bst
  scripts/anti_shrink.py --strategy Hedgehog      # strategies starting with prefix
  scripts/anti_shrink.py --verbose                # print pre/post/gt counterexamples
  scripts/anti_shrink.py --false-gt               # inspect the false-ground-truth tasks
  scripts/anti_shrink.py --csv anti_shrink.csv    # also dump every case to CSV
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workload_config import ROOT, get_config

FIG = ROOT / "figures"
ANTI_COLS = ["workload", "strategy", "property", "mutation", "trial",
             "pre_ted_to_gt", "ted_to_gt", "delta",
             "pre_size", "cex_size", "gt_size", "false_gt",
             "pre_counterexample", "counterexample", "gt_counterexample"]
FGT_COLS = ["workload", "property", "mutation", "gt_size", "gt_counterexample",
            "strategy", "trial", "which", "obs_size", "obs_counterexample"]


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_store(rel_path):
    """(strategy, property, mutations, trial) -> store row."""
    p = ROOT / rel_path
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)["data"]
        key = (d["strategy"], d["property"],
               ",".join(d.get("mutations") or []), str(d["trial"]))
        out[key] = d
    return out


def load_gt_cex(workload):
    """(property, mutations) -> ' | '-joined ground-truth counterexample(s)."""
    p = ROOT / f"store.{workload}.det.jsonl"
    if not p.exists():
        return {}
    acc = defaultdict(set)
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)["data"]
        if d.get("strategy") not in ("Lean", "LeanRev") or d.get("status") != "Failed":
            continue
        prop = d["property"]
        if prop.startswith("prop_"):
            prop = prop[5:]
        cex = d.get("counterexample") or ""
        if cex:
            acc[(prop, ",".join(d.get("mutations") or []))].add(cex)
    return {k: " | ".join(sorted(v)) for k, v in acc.items()}


def read_csv(workload, mode):
    csv_path = FIG / f"{workload.upper()}_ANALYSIS.csv"
    if not csv_path.exists():
        print(f"  {workload}: missing {csv_path.name} "
              f"(run scripts/workload_analysis.py --workload {workload})",
              file=sys.stderr)
        return None
    return [r for r in csv.DictReader(csv_path.open())
            if r["mode"] == mode and r["status"] == "Failed"]


def false_gt_tasks(all_csv):
    """task -> gt_size, for tasks where an observed cex is smaller than the GT."""
    gt_size, min_obs = {}, {}
    for r in all_csv:
        task = (r["property"], r["mutation"])
        g = fnum(r["gt_size"])
        if g is not None:
            gt_size[task] = g
        for col in ("pre_size", "cex_size"):
            s = fnum(r[col])
            if s is not None and (task not in min_obs or s < min_obs[task]):
                min_obs[task] = s
    return {t: gt_size[t] for t, g in gt_size.items()
            if t in min_obs and min_obs[t] < g}


def store_for(stores, cfg, fw, mode):
    if fw not in stores:
        sf = cfg["stores"].get((fw, mode))
        stores[fw] = load_store(sf) if sf else {}
    return stores[fw]


# --------------------------------------------------------------------------
# anti-shrink mode
# --------------------------------------------------------------------------
def gather_anti(workload, strategy_prefix, mode):
    all_csv = read_csv(workload, mode)
    if all_csv is None:
        return [], 0
    cfg = get_config(workload)
    fgt = false_gt_tasks(all_csv)
    gt_cex = load_gt_cex(workload)
    stores = {}
    rows, considered = [], 0
    for r in all_csv:
        if strategy_prefix and not r["strategy"].startswith(strategy_prefix):
            continue
        pre, post = fnum(r["pre_ted_to_gt"]), fnum(r["ted_to_gt"])
        if pre is None or post is None:
            continue
        considered += 1
        if post <= pre:
            continue
        d = store_for(stores, cfg, r["framework"], mode).get(
            (r["strategy"], r["property"], r["mutation"], r["trial"]), {})
        rows.append({
            "workload": workload, "strategy": r["strategy"],
            "property": r["property"], "mutation": r["mutation"],
            "trial": r["trial"], "pre_ted_to_gt": pre, "ted_to_gt": post,
            "delta": post - pre,
            "pre_size": fnum(r["pre_size"]), "cex_size": fnum(r["cex_size"]),
            "gt_size": fnum(r["gt_size"]),
            "false_gt": (r["property"], r["mutation"]) in fgt,
            "pre_counterexample": d.get("pre_counterexample", ""),
            "counterexample": d.get("counterexample", ""),
            "gt_counterexample": gt_cex.get((r["property"], r["mutation"]), ""),
        })
    return rows, considered


def report_anti(workload, rows, considered, verbose):
    genuine = [r for r in rows if not r["false_gt"]]
    suspect = [r for r in rows if r["false_gt"]]
    g_tasks = {(r["strategy"], r["property"], r["mutation"]) for r in genuine}
    print(f"=== {workload} ===")
    print(f"  anti-shrink rows: {len(rows)} / {considered}")
    print(f"  excluded (false ground truth): {len(suspect)} rows")
    print(f"  genuine anti-shrink: {len(genuine)} rows  "
          f"({len(g_tasks)} distinct tasks)")
    if genuine:
        by_strat = Counter(r["strategy"] for r in genuine)
        print("  by strategy: "
              + ", ".join(f"{s} {n}" for s, n in sorted(by_strat.items())))
        shown = sorted(genuine, key=lambda r: -r["delta"])
        cap = len(shown) if verbose else 40
        for r in shown[:cap]:
            print(f"    +{r['delta']:<4.0f} {r['strategy']:14s} "
                  f"{r['property']}/{r['mutation']} t{r['trial']}  "
                  f"pre_ted={r['pre_ted_to_gt']:.0f} -> ted={r['ted_to_gt']:.0f}")
            if verbose:
                print(f"        pre : {r['pre_counterexample'] or '(missing)'}")
                print(f"        post: {r['counterexample'] or '(missing)'}")
                print(f"        gt  : {r['gt_counterexample'] or '(missing)'}")
        if not verbose and len(shown) > cap:
            print(f"    ... {len(shown) - cap} more (use --csv or --verbose)")
    if suspect:
        print("  false-GT tasks (see --false-gt for detail):")
        for p, m in sorted({(r["property"], r["mutation"]) for r in suspect}):
            print(f"    {p}/{m}")


# --------------------------------------------------------------------------
# false-ground-truth mode
# --------------------------------------------------------------------------
def gather_false_gt(workload, mode):
    all_csv = read_csv(workload, mode)
    if all_csv is None:
        return []
    cfg = get_config(workload)
    fgt = false_gt_tasks(all_csv)
    gt_cex = load_gt_cex(workload)
    stores = {}
    obs = defaultdict(list)  # task -> falsifying observations
    for r in all_csv:
        task = (r["property"], r["mutation"])
        if task not in fgt:
            continue
        g = fgt[task]
        for col, which in (("pre_size", "pre"), ("cex_size", "post")):
            s = fnum(r[col])
            if s is None or s >= g:
                continue
            d = store_for(stores, cfg, r["framework"], mode).get(
                (r["strategy"], r["property"], r["mutation"], r["trial"]), {})
            cex = d.get("pre_counterexample" if which == "pre"
                        else "counterexample", "")
            obs[task].append({
                "workload": workload, "property": r["property"],
                "mutation": r["mutation"], "gt_size": g,
                "gt_counterexample": gt_cex.get(task, ""),
                "strategy": r["strategy"], "trial": r["trial"],
                "which": which, "obs_size": s, "obs_counterexample": cex,
            })
    return [obs[t] for t in sorted(obs)]


def report_false_gt(workload, tasks, verbose):
    print(f"=== {workload} ===")
    print(f"  false-GT tasks: {len(tasks)}")
    for group in tasks:
        head = group[0]
        smallest = min(group, key=lambda o: o["obs_size"])
        sizes = sorted({o["obs_size"] for o in group})
        print(f"  {head['property']}/{head['mutation']}   "
              f"gt_size={head['gt_size']:.0f}")
        print(f"    gt       : {head['gt_counterexample'] or '(missing)'}")
        print(f"    smallest : size {smallest['obs_size']:.0f}  "
              f"{smallest['strategy']} t{smallest['trial']} ({smallest['which']})")
        print(f"               {smallest['obs_counterexample'] or '(missing)'}")
        print(f"    {len(group)} observation(s) below gt_size "
              f"(sizes {sizes[0]:.0f}-{sizes[-1]:.0f})")
        if verbose:
            seen = set()
            for o in sorted(group, key=lambda o: o["obs_size"]):
                cex = o["obs_counterexample"]
                if cex in seen:
                    continue
                seen.add(cex)
                print(f"      size {o['obs_size']:.0f}  {o['strategy']} "
                      f"t{o['trial']} ({o['which']})  {cex or '(missing)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", choices=["bst", "rbt", "stlc", "fsub"],
                    help="restrict to one workload (default: all)")
    ap.add_argument("--strategy", default="",
                    help="anti-shrink mode: only strategies starting with this prefix")
    ap.add_argument("--mode", default="default", help="shrink mode (default: default)")
    ap.add_argument("--verbose", action="store_true",
                    help="print the pre/post/ground-truth counterexamples")
    ap.add_argument("--false-gt", action="store_true",
                    help="inspect the false-ground-truth tasks instead of anti-shrink cases")
    ap.add_argument("--csv", help="also write the cases to this CSV")
    args = ap.parse_args()

    workloads = [args.workload] if args.workload else ["bst", "rbt", "stlc", "fsub"]

    if args.false_gt:
        all_rows = []
        for wl in workloads:
            tasks = gather_false_gt(wl, args.mode)
            report_false_gt(wl, tasks, args.verbose)
            for g in tasks:
                all_rows.extend(g)
        if args.csv:
            with open(args.csv, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FGT_COLS)
                w.writeheader()
                w.writerows(all_rows)
            print(f"\nwrote {len(all_rows)} falsifying observations to {args.csv}")
        return

    all_rows = []
    for wl in workloads:
        rows, considered = gather_anti(wl, args.strategy, args.mode)
        report_anti(wl, rows, considered, args.verbose)
        all_rows.extend(rows)
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=ANTI_COLS)
            w.writeheader()
            w.writerows(all_rows)
        print(f"\nwrote {len(all_rows)} cases to {args.csv} "
              f"(filter false_gt=False for genuine regressions)")


if __name__ == "__main__":
    main()
