#!/usr/bin/env python3
"""STLC / FSUB default-mode shrinking analysis.

Mirrors scripts/bst_analysis.py but for the smaller stlc / fsub workloads
(2 properties, no CBC2/GbE variants). Computes:

  1. Coverage
  2. TED to Lean ground truth (mean / median / p90 / max)
  3. % of trials at TED = 0
  4. ms / TED edit reduced
  5. Pre vs post counterexample size
  6. Shrink-attempt counts
  7. Time decomposition (execution / generation / shrinking)

Ground truth: store.{stlc,fsub}.det.jsonl (Lean + LeanRev rows).

Writes one Markdown report per workload to figures/.
"""

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from zss import simple_distance, Node

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

WORKLOADS = {
    "stlc": {
        "stores": {
            "quick":    ROOT / "store.stlc.quick.shrink-default.jsonl",
            "hedgehog": ROOT / "store.stlc.hedgehog.shrink-default.jsonl",
            "falsify":  ROOT / "store.stlc.falsify.shrink-default.jsonl",
        },
        "groundtruth": ROOT / "store.stlc.det.jsonl",
        # Strategy display order; CBC strategy paired beneath its vanilla peer.
        "strategies": ["Quick", "Correct", "Hedgehog", "HedgehogCBC", "Falsify", "FalsifyCBC"],
        "framework_of": {
            "Quick": "quick", "Correct": "quick",
            "Hedgehog": "hedgehog", "HedgehogCBC": "hedgehog",
            "Falsify": "falsify",  "FalsifyCBC":  "falsify",
        },
    },
    "fsub": {
        "stores": {
            "quick":    ROOT / "store.fsub.quick.shrink-default.jsonl",
            "hedgehog": ROOT / "store.fsub.hedgehog.shrink-default.jsonl",
            "falsify":  ROOT / "store.fsub.falsify.shrink-default.jsonl",
        },
        "groundtruth": ROOT / "store.fsub.det.jsonl",
        "strategies": ["Quick", "Correct", "Hedgehog", "HedgehogCBC", "Falsify", "FalsifyCBC"],
        "framework_of": {
            "Quick": "quick", "Correct": "quick",
            "Hedgehog": "hedgehog", "HedgehogCBC": "hedgehog",
            "Falsify": "falsify",  "FalsifyCBC":  "falsify",
        },
    },
}


# ---- TED -------------------------------------------------------------

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
    ta = cex_to_tree(a)
    tb = cex_to_tree(b)
    if ta is None or tb is None:
        return None
    return simple_distance(ta, tb)


# ---- Loading ---------------------------------------------------------

def load(path: Path):
    if not path.exists():
        return []
    return [json.loads(line)["data"]
            for line in path.read_text().splitlines() if line.strip()]


def task_key(r):
    prop = r["property"]
    if prop.startswith("prop_"):
        prop = prop[len("prop_"):]
    muts = ",".join(r.get("mutations", []) or [])
    return (prop, muts)


def load_groundtruth(path: Path):
    """Map (property_bare, mutations_str) -> smallest Lean/LeanRev cex string.

    Both Lean and LeanRev enumerate exhaustively; take whichever produced
    the smallest counterexample for that task.
    """
    out = {}
    for r in load(path):
        if r["strategy"] not in ("Lean", "LeanRev"):
            continue
        if r["status"] != "Failed":
            continue
        cex = r.get("counterexample") or r.get("pre_counterexample") or ""
        if not cex:
            continue
        k = task_key(r)
        if k not in out or cex_size(cex) < cex_size(out[k]):
            out[k] = cex
    return out


# ---- Annotation ------------------------------------------------------

def annotate(rows, ground_truth, cache_ted=None):
    if cache_ted is None:
        cache_ted = {}
    for r in rows:
        cex = r.get("counterexample") or ""
        pre = r.get("pre_counterexample") or ""
        r["_cex_size"] = cex_size(cex)
        r["_pre_size"] = cex_size(pre)
        gt = ground_truth.get(task_key(r))
        r["_gt_cex"] = gt
        r["_gt_size"] = cex_size(gt) if gt else None
        if cex and gt:
            key = (cex, gt)
            if key not in cache_ted:
                cache_ted[key] = ted(cex, gt)
            r["_ted_to_gt"] = cache_ted[key]
        else:
            r["_ted_to_gt"] = None
        if pre and gt:
            key2 = (pre, gt)
            if key2 not in cache_ted:
                cache_ted[key2] = ted(pre, gt)
            r["_pre_ted_to_gt"] = cache_ted[key2]
        else:
            r["_pre_ted_to_gt"] = None
        r["_gen_time"] = (r.get("time_pre_failure", 0) or 0) - (r.get("exec_time_pre", 0) or 0)
    return rows


# ---- Stats helpers ---------------------------------------------------

def dist(values):
    if not values:
        return None
    xs = sorted(values)
    n = len(xs)
    return {
        "n": n,
        "mean":   mean(xs),
        "median": median(xs),
        "p90":    xs[min(n - 1, 9 * n // 10)],
        "max":    xs[-1],
    }


def fmt_dist(d, prec=2):
    if d is None:
        return "—"
    return f"{d['mean']:.{prec}f} / {d['median']:.{prec}f} / {d['p90']:.{prec}f} / {d['max']:.{prec}f}"


# ---- Render ----------------------------------------------------------

def render(workload: str, cfg: dict, all_rows: dict, gt: dict):
    L = []
    L.append(f"# {workload.upper()} analysis — default shrink mode")
    L.append("")
    L.append(f"Stores loaded:")
    for fw, p in cfg["stores"].items():
        n = len(all_rows.get(fw, []))
        L.append(f"  - `{p.name}` ({n} rows)")
    L.append(f"Ground truth: `{cfg['groundtruth'].name}` — {len(gt)} (property, mutation) pairs")
    L.append("")
    L.append("All stats restricted to `status == \"Failed\"` rows.")
    L.append("TED is Zhang-Shasha distance over the parens-structured cex.")
    L.append("")

    strategies = cfg["strategies"]
    framework_of = cfg["framework_of"]

    def fail_rows(s):
        fw = framework_of[s]
        return [r for r in all_rows.get(fw, [])
                if r["strategy"] == s and r["status"] == "Failed"]

    # 1. Coverage
    L.append("## 1. Coverage")
    L.append("")
    L.append("Failed rows per strategy. Expected = 10 (stlc) or 18 (fsub) mutations × 2 props × 10 trials.")
    L.append("")
    L.append("| Strategy | Failed | TimedOut | total | gt-coverage |")
    L.append("|---|---:|---:|---:|---:|")
    for s in strategies:
        fw = framework_of[s]
        all_s = [r for r in all_rows.get(fw, []) if r["strategy"] == s]
        failed = [r for r in all_s if r["status"] == "Failed"]
        timed  = [r for r in all_s if r["status"] == "timed_out"]
        with_gt = sum(1 for r in failed if r["_ted_to_gt"] is not None)
        L.append(f"| {s} | {len(failed)} | {len(timed)} | {len(all_s)} | {with_gt} |")
    L.append("")

    # 2. TED to ground truth
    L.append("## 2. Effectiveness — TED to ground-truth minimum")
    L.append("")
    L.append("Lower is better. Format: **mean / median / p90 / max**.")
    L.append("")
    L.append("| Strategy | TED | n |")
    L.append("|---|---|---:|")
    for s in strategies:
        teds = [r["_ted_to_gt"] for r in fail_rows(s) if r["_ted_to_gt"] is not None]
        L.append(f"| {s} | {fmt_dist(dist(teds), prec=1)} | {len(teds)} |")
    L.append("")

    # 2a. % at TED = 0
    L.append("### 2a. Fraction of trials reaching TED = 0")
    L.append("")
    L.append("| Strategy | TED=0 | n | % |")
    L.append("|---|---:|---:|---:|")
    for s in strategies:
        teds = [r["_ted_to_gt"] for r in fail_rows(s) if r["_ted_to_gt"] is not None]
        if not teds:
            L.append(f"| {s} | — | 0 | — |")
            continue
        z = sum(1 for t in teds if t == 0)
        L.append(f"| {s} | {z} | {len(teds)} | {100*z/len(teds):.1f}% |")
    L.append("")

    # 3. ms per TED edit reduced
    L.append("## 3. Performance — ms spent shrinking per unit of TED reduction")
    L.append("")
    L.append("`time_shrinking * 1000 / (TED(pre) − TED(post))`. Trials with no reduction excluded.")
    L.append("")
    L.append("| Strategy | ms/edit (mean / med / p90 / max) | n |")
    L.append("|---|---|---:|")
    for s in strategies:
        ratios = []
        for r in fail_rows(s):
            pre_t, post_t = r.get("_pre_ted_to_gt"), r.get("_ted_to_gt")
            if pre_t is None or post_t is None:
                continue
            reduced = pre_t - post_t
            if reduced <= 0:
                continue
            ts = (r.get("time_shrinking") or 0) * 1000
            ratios.append(ts / reduced)
        L.append(f"| {s} | {fmt_dist(dist(ratios), prec=2)} | {len(ratios)} |")
    L.append("")

    # 4. Pre vs post size
    L.append("## 4. Pre vs post-shrinking counterexample size")
    L.append("")
    L.append("Token count of `pre_counterexample` vs `counterexample` on Failed rows. Lower post is better.")
    L.append("")
    L.append("| Strategy | mean pre | mean post | mean Δ | mean Δ % |")
    L.append("|---|---:|---:|---:|---:|")
    for s in strategies:
        rows = fail_rows(s)
        if not rows:
            L.append(f"| {s} | — | — | — | — |")
            continue
        pre  = mean(r["_pre_size"] for r in rows)
        post = mean(r["_cex_size"] for r in rows)
        d    = pre - post
        pct  = 100 * d / pre if pre else 0
        L.append(f"| {s} | {pre:.1f} | {post:.1f} | {d:.1f} | {pct:.1f}% |")
    L.append("")

    # 5. Shrink attempts
    L.append("## 5. Shrink attempts (Failed rows only)")
    L.append("")
    L.append("`passed` = candidate where property still held (rejected), `failed` = property")
    L.append("broke again (accepted as new minimum), `discarded` = precondition rejected.")
    L.append("")
    L.append("| Strategy | passed | failed (accepted) | discarded | total |")
    L.append("|---|---:|---:|---:|---:|")
    for s in strategies:
        rows = fail_rows(s)
        if not rows:
            L.append(f"| {s} | — | — | — | — |")
            continue
        sp = mean(r.get("shrinking_passed", 0) or 0 for r in rows)
        sf = mean(r.get("shrinking_failed", 0) or 0 for r in rows)
        sd = mean(r.get("shrinking_discarded", 0) or 0 for r in rows)
        L.append(f"| {s} | {sp:.1f} | {sf:.1f} | {sd:.1f} | {sp+sf+sd:.1f} |")
    L.append("")

    # 6. Time decomposition (ms)
    L.append("## 6. Time decomposition (mean ms across Failed rows)")
    L.append("")
    L.append("- execution = `exec_time_pre`")
    L.append("- generation = `time_pre_failure − exec_time_pre`")
    L.append("- shrinking = `time_shrinking`")
    L.append("")
    L.append("| Strategy | execution | generation | shrinking | total |")
    L.append("|---|---:|---:|---:|---:|")
    for s in strategies:
        rows = fail_rows(s)
        if not rows:
            L.append(f"| {s} | — | — | — | — |")
            continue
        ex = mean((r.get("exec_time_pre", 0) or 0) for r in rows)
        ge = mean(r["_gen_time"] for r in rows)
        sh = mean((r.get("time_shrinking", 0) or 0) for r in rows)
        L.append(f"| {s} | {ex*1000:.2f} ms | {ge*1000:.2f} ms | {sh*1000:.2f} ms | {(ex+ge+sh)*1000:.2f} ms |")
    L.append("")

    return "\n".join(L) + "\n"


def main():
    for workload, cfg in WORKLOADS.items():
        print(f"=== {workload} ===")
        gt = load_groundtruth(cfg["groundtruth"])
        print(f"  ground truth: {len(gt)} (property, mutation) pairs")
        cache_ted = {}
        all_rows = {}
        for fw, path in cfg["stores"].items():
            rows = load(path)
            print(f"  loaded {path.name}: {len(rows)} rows")
            annotate(rows, gt, cache_ted)
            all_rows[fw] = rows
        md = render(workload, cfg, all_rows, gt)
        out = FIG / f"{workload.upper()}_ANALYSIS.md"
        out.write_text(md)
        print(f"  wrote {out}")


if __name__ == "__main__":
    main()
