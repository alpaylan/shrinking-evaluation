#!/usr/bin/env python3
"""Per-workload TED analysis + CSV export.

Produces `figures/<WORKLOAD>_ANALYSIS.csv` (one row per trial, annotated
with TED to the Lean ground-truth minimum). Consumed by both the bucket
chart and ECDF chart scripts.

Usage: scripts/workload_analysis.py --workload {bst,rbt,stlc,fsub}
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from zss import simple_distance, Node

from workload_config import ROOT, get_config

FIG = ROOT / "figures"


# ---- TED helpers (same convention as scripts/bst_analysis.py) ----

def tokenize(s: str):
    tokens, cur = [], ""
    for c in s:
        if c in "()":
            if cur:
                tokens.append(cur); cur = ""
            tokens.append(c)
        elif c in ", \t\n":
            if cur:
                tokens.append(cur); cur = ""
        else:
            cur += c
    if cur:
        tokens.append(cur)
    return tokens


def parse_tree(tokens, i=0):
    if i >= len(tokens):
        return None, i
    if tokens[i] == "(":
        node = Node("*")
        j = i + 1
        while j < len(tokens) and tokens[j] != ")":
            child, j = parse_tree(tokens, j)
            if child is not None:
                node.addkid(child)
        return node, j + 1
    elif tokens[i] == ")":
        return None, i
    else:
        return Node(tokens[i]), i + 1


def cex_to_tree(s: str):
    if not s:
        return None
    toks = tokenize(s)
    if not toks:
        return None
    if toks[0] != "(":
        return Node("ROOT", children=[Node(t) for t in toks])
    tree, _ = parse_tree(toks)
    return tree


def cex_size(s: str) -> int:
    if not s:
        return 0
    return sum(1 for t in tokenize(s) if t != ")")


def ted(a: str, b: str):
    if not a or not b:
        return None
    ta, tb = cex_to_tree(a), cex_to_tree(b)
    if ta is None or tb is None:
        return None
    return simple_distance(ta, tb)


# ---- Loading + annotation ----

def load(path: Path):
    if not path.exists():
        return []
    return [json.loads(l)["data"]
            for l in path.read_text().splitlines() if l.strip()]


def task_key(r):
    prop = r["property"]
    if prop.startswith("prop_"):
        prop = prop[len("prop_"):]
    muts = ",".join(r.get("mutations", []) or [])
    return (prop, muts)


def load_groundtruth(workload: str):
    """Map (property_bare, mutations_str) -> list of minimal-size cexes.

    The deterministic Lean / LeanRev searches can each surface a different
    counterexample of the *same* minimal size (there is not always a unique
    minimum). We keep the full set of minimal-size counterexamples per task;
    TED-to-GT is then the distance to the *nearest* one, so a strategy that
    finds any legitimate minimum scores TED = 0.

    The groundtruth for every workload lives in store.<workload>.det.jsonl.
    """
    path = ROOT / f"store.{workload}.det.jsonl"
    if not path.exists():
        print(f"  WARN: no ground truth store for {workload}", file=sys.stderr)
        return {}
    raw = defaultdict(set)
    for r in load(path):
        if r["strategy"] not in ("Lean", "LeanRev"):
            continue
        if r["status"] != "Failed":
            continue
        cex = r.get("counterexample") or r.get("pre_counterexample") or ""
        if not cex:
            continue
        raw[task_key(r)].add(cex)
    out = {}
    n_ties = 0
    for k, cexes in raw.items():
        m = min(cex_size(c) for c in cexes)
        minimal = sorted(c for c in cexes if cex_size(c) == m)
        out[k] = minimal
        if len(minimal) > 1:
            n_ties += 1
    print(f"  ground truth: {len(out)} pairs from {path.name} "
          f"({n_ties} with multiple equal-size minima)")
    return out


def ted_to_set(cex, gt_list, cache_ted):
    """TED from `cex` to the nearest counterexample in `gt_list`.

    `gt_list` is the set of equal-size minimal ground-truth counterexamples
    for the task; a strategy that finds any of them should score 0.
    """
    if not cex or not gt_list:
        return None
    dists = []
    for g in gt_list:
        key = (cex, g)
        if key not in cache_ted:
            cache_ted[key] = ted(cex, g)
        d = cache_ted[key]
        if d is not None:
            dists.append(d)
    return min(dists) if dists else None


def annotate(rows, ground_truth, cache_ted):
    for r in rows:
        cex = r.get("counterexample") or ""
        pre = r.get("pre_counterexample") or ""
        r["_cex_size"] = cex_size(cex)
        r["_pre_size"] = cex_size(pre)
        gt = ground_truth.get(task_key(r))  # list of minimal cexes, or None
        r["_gt_cex"]  = gt[0] if gt else None
        r["_gt_size"] = cex_size(gt[0]) if gt else None
        r["_ted_to_gt"]     = ted_to_set(cex, gt, cache_ted)
        r["_pre_ted_to_gt"] = ted_to_set(pre, gt, cache_ted)
        r["_gen_time"] = (r.get("time_pre_failure", 0) or 0) - (r.get("exec_time_pre", 0) or 0)


# ---- CSV export (BST_ANALYSIS.csv-compatible) ----

CSV_COLS = ["framework","strategy","mode","property","mutation","trial",
            "status","tests","discards","shrinking_passed","shrinking_failed","shrinking_discarded",
            "exec_time_pre","gen_time","time_shrinking","time_pre_failure",
            "pre_size","cex_size","gt_size","pre_ted_to_gt","ted_to_gt"]


def write_csv(all_data, csv_path: Path):
    with csv_path.open("w") as f:
        f.write(",".join(CSV_COLS) + "\n")
        for (fw, mode), rows in all_data.items():
            for r in rows:
                row = {
                    "framework": fw, "strategy": r["strategy"], "mode": mode,
                    "property": r["property"],
                    "mutation": ",".join(r.get("mutations", []) or []),
                    "trial": r.get("trial"), "status": r["status"],
                    "tests": r.get("tests"), "discards": r.get("discards"),
                    "shrinking_passed": r.get("shrinking_passed"),
                    "shrinking_failed": r.get("shrinking_failed"),
                    "shrinking_discarded": r.get("shrinking_discarded"),
                    "exec_time_pre": r.get("exec_time_pre"),
                    "gen_time": r["_gen_time"],
                    "time_shrinking": r.get("time_shrinking"),
                    "time_pre_failure": r.get("time_pre_failure"),
                    "pre_size": r["_pre_size"], "cex_size": r["_cex_size"],
                    "gt_size": r["_gt_size"],
                    "pre_ted_to_gt": r["_pre_ted_to_gt"],
                    "ted_to_gt": r["_ted_to_gt"],
                }
                f.write(",".join("" if v is None else str(v) for v in (row[c] for c in CSV_COLS)) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workload", required=True, choices=["bst", "rbt", "stlc", "fsub"])
    args = ap.parse_args()

    cfg = get_config(args.workload)
    print(f"=== {args.workload} ===")
    gt = load_groundtruth(args.workload)
    shared_cache = {}
    all_data = {}
    for (fw, mode), filename in cfg["stores"].items():
        path = ROOT / filename
        rows = load(path)
        print(f"  [{fw}/{mode}] {filename}: {len(rows)} rows")
        annotate(rows, gt, shared_cache)
        all_data[(fw, mode)] = rows

    out = FIG / f"{args.workload.upper()}_ANALYSIS.csv"
    write_csv(all_data, out)
    print(f"wrote {out} (cache size {len(shared_cache)})")


if __name__ == "__main__":
    main()
