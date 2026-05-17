#!/usr/bin/env python3
"""Median pre/post shrinking edit distance for type-based (vanilla) generators."""
import json, statistics
from pathlib import Path
from zss import simple_distance, Node

ROOT = Path(__file__).resolve().parent.parent

def tokenize(s):
    tokens, cur = [], ""
    for c in s:
        if c in "()":
            if cur: tokens.append(cur); cur = ""
            tokens.append(c)
        elif c in ", \t\n":
            if cur: tokens.append(cur); cur = ""
        else:
            cur += c
    if cur: tokens.append(cur)
    return tokens

def parse_tree(tokens, i=0):
    if i >= len(tokens): return None, i
    if tokens[i] == "(":
        node = Node("*"); j = i + 1
        while j < len(tokens) and tokens[j] != ")":
            child, j = parse_tree(tokens, j)
            if child is not None: node.addkid(child)
        return node, j + 1
    elif tokens[i] == ")":
        return None, i
    else:
        return Node(tokens[i]), i + 1

def cex_to_tree(s):
    if not s: return None
    toks = tokenize(s)
    if not toks: return None
    if toks[0] != "(":
        return Node("ROOT", children=[Node(t) for t in toks])
    tree, _ = parse_tree(toks)
    return tree

def ted(a, b):
    if not a or not b: return None
    ta, tb = cex_to_tree(a), cex_to_tree(b)
    if ta is None or tb is None: return None
    return simple_distance(ta, tb)

VANILLA = {"Quick", "Hedgehog", "Falsify"}
WORKLOADS = {
    "bst":  ["store.bst.quick.shrink-default.jsonl", "store.bst.hedgehog.shrink-default.jsonl", "store.bst.falsify.shrink-default.jsonl"],
    "rbt":  ["store.rbt.quick.shrink-default.jsonl", "store.rbt.hedgehog.shrink-default.jsonl", "store.rbt.falsify.shrink-default.jsonl"],
    "stlc": ["store.stlc.quick.shrink-default.jsonl", "store.stlc.hedgehog.shrink-default.jsonl", "store.stlc.falsify.shrink-default.jsonl"],
    "fsub": ["store.fsub.quick.shrink-default.jsonl", "store.fsub.hedgehog.shrink-default.jsonl", "store.fsub.falsify.shrink-default.jsonl"],
}

all_dists = []
for wl, files in WORKLOADS.items():
    wl_dists = []
    by_strat = {}
    for fn in files:
        path = ROOT / fn
        if not path.exists():
            print(f"  MISSING {fn}")
            continue
        for line in path.read_text().splitlines():
            if not line.strip(): continue
            r = json.loads(line)["data"]
            if r.get("strategy") not in VANILLA: continue
            if r.get("status") != "Failed": continue
            pre = r.get("pre_counterexample") or ""
            post = r.get("counterexample") or ""
            d = ted(pre, post)
            if d is None: continue
            wl_dists.append(d)
            by_strat.setdefault(r["strategy"], []).append(d)
    all_dists.extend(wl_dists)
    med = statistics.median(wl_dists) if wl_dists else None
    print(f"{wl:5s} n={len(wl_dists):5d}  median pre/post TED = {med}  "
          f"mean={statistics.mean(wl_dists):.2f}  max={max(wl_dists)}")
    for s, ds in sorted(by_strat.items()):
        print(f"    {s:10s} n={len(ds):5d}  median={statistics.median(ds)}  mean={statistics.mean(ds):.2f}")

print("-" * 60)
print(f"ALL   n={len(all_dists):5d}  median pre/post TED = {statistics.median(all_dists)}  "
      f"mean={statistics.mean(all_dists):.2f}")
nz = sum(1 for d in all_dists if d == 0)
print(f"zero-distance trials: {nz}/{len(all_dists)} = {100*nz/len(all_dists):.1f}%")
