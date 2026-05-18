#!/usr/bin/env python3
"""Emit the appendix ground-truth tables for the paper.

For every (property, mutation) task of every workload, list the minimal
counterexample found by the deterministic LeanCheck search (Lean /
LeanRev rows of store.<wl>.det.jsonl). Writes one longtable per workload
into ShrinkingEval/appendix_groundtruth.tex, which paper.tex \\input-s.

Run: .venv/bin/python scripts/gen_groundtruth_tables.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ShrinkingEval" / "appendix_groundtruth.tex"

# workload -> (display name, list of store files, det store)
WORKLOADS = [
    ("bst",  "BST",      [f"store.bst.{fw}.shrink-default.jsonl"  for fw in ("quick", "hedgehog", "falsify")], "store.bst.det.jsonl"),
    ("rbt",  "RBT",      [f"store.rbt.{fw}.shrink-default.jsonl"  for fw in ("quick", "hedgehog", "falsify")], "store.rbt.det.jsonl"),
    ("stlc", "STLC",     [f"store.stlc.{fw}.shrink-default.jsonl" for fw in ("quick", "hedgehog", "falsify")], "store.stlc.det.jsonl"),
    ("fsub", "$F_{<:}$", [f"store.fsub.{fw}.shrink-default.jsonl" for fw in ("quick", "hedgehog", "falsify")], "store.fsub.det.jsonl"),
]


def load(p):
    path = ROOT / p
    if not path.exists():
        return []
    return [json.loads(l)["data"] for l in path.read_text().splitlines() if l.strip()]


def bare(prop):
    return prop[len("prop_"):] if prop.startswith("prop_") else prop


def tex_escape(s):
    for a, b in [("\\", r"\textbackslash{}"), ("_", r"\_"), ("#", r"\#"),
                 ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def cex_tokens(s):
    out, cur = [], ""
    for c in s:
        if c in "()":
            if cur:
                out.append(cur); cur = ""
            out.append(c)
        elif c in ", \t\n":
            if cur:
                out.append(cur); cur = ""
        else:
            cur += c
    if cur:
        out.append(cur)
    return out


def cex_size(s):
    return sum(1 for t in cex_tokens(s) if t != ")")


def all_tasks(store_files):
    tasks = set()
    for f in store_files:
        for r in load(f):
            tasks.add((bare(r["property"]), r["mutations"][0]))
    return tasks


def mutation_order(short):
    """Canonical mutation order = order of the {-!! name -} markers in the
    workload's Impl.hs. Returns name -> index."""
    impl = ROOT / "workloads" / f"{short}-haskell" / "src" / "Impl.hs"
    names = re.findall(r"\{-!!\s*([A-Za-z0-9_]+)\s*-\}", impl.read_text())
    return {name: i for i, name in enumerate(names)}


def ground_truth(det_store):
    """task -> minimal counterexample (lexicographically first of the
    minimal-size set, matching scripts/workload_analysis.py)."""
    raw = {}
    for r in load(det_store):
        if r["strategy"] not in ("Lean", "LeanRev") or r["status"] != "Failed":
            continue
        cex = r.get("counterexample") or r.get("pre_counterexample") or ""
        if not cex:
            continue
        raw.setdefault((bare(r["property"]), r["mutations"][0]), set()).add(cex)
    out = {}
    for k, cexes in raw.items():
        m = min(cex_size(c) for c in cexes)
        out[k] = sorted(c for c in cexes if cex_size(c) == m)[0]
    return out


def longtable(short, disp, tasks, gt, mut_order):
    # Sort by canonical mutation order (Impl.hs marker order), then property.
    rows = sorted(tasks, key=lambda t: (mut_order.get(t[1], len(mut_order)), t[0]))
    n_gt = sum(1 for t in rows if t in gt)
    L = []
    L.append(r"\begin{longtable}{@{}l l >{\ttfamily\footnotesize}p{0.46\linewidth}@{}}")
    L.append(rf"\caption{{Ground-truth minimal counterexamples for {disp} "
             rf"({n_gt} of {len(rows)} tasks solved by the deterministic "
             rf"LeanCheck search).}}\label{{tab:gt-{short}}}\\")
    L.append(r"\toprule")
    L.append(r"\normalfont Property & \normalfont Mutation & "
             r"\normalfont Minimal counterexample \\")
    L.append(r"\midrule")
    L.append(r"\endfirsthead")
    L.append(rf"\multicolumn{{3}}{{@{{}}l}}{{\footnotesize\itshape "
             rf"Table~\ref{{tab:gt-{short}}}, {disp}, continued}}\\")
    L.append(r"\toprule")
    L.append(r"\normalfont Property & \normalfont Mutation & "
             r"\normalfont Minimal counterexample \\")
    L.append(r"\midrule")
    L.append(r"\endhead")
    L.append(r"\bottomrule")
    L.append(r"\endlastfoot")
    for prop, mut in rows:
        cex = gt.get((prop, mut))
        cell = tex_escape(cex) if cex else r"\normalfont ---"
        L.append(rf"{tex_escape(prop)} & {tex_escape(mut)} & {cell} \\")
    L.append(r"\end{longtable}")
    L.append("")
    return "\n".join(L)


def main():
    blocks = [
        r"\section{Ground-Truth Minimal Counterexamples}\label{app:groundtruth}",
        "",
        r"The tables below list, for every (property, mutation) task of each "
        r"workload, the minimal counterexample established by the exhaustive "
        r"deterministic LeanCheck search. These are the references against "
        r"which the tree-edit-distance metric in Section~\ref{sec:eval} is "
        r"computed. A dash (---) marks a task for which the deterministic "
        r"search did not establish a ground truth.",
        "",
    ]
    for short, disp, stores, det in WORKLOADS:
        tasks = all_tasks(stores)
        gt = ground_truth(det)
        blocks.append(longtable(short, disp, tasks, gt, mutation_order(short)))
        print(f"{short}: {len(tasks)} tasks, {sum(1 for t in tasks if t in gt)} with ground truth")
    OUT.write_text("\n".join(blocks) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
