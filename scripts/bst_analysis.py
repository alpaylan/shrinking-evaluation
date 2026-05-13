#!/usr/bin/env python3
"""
Full BST analysis aligned to the paper's metrics.

Outputs `figures/BST_ANALYSIS.md` (paper-ready tables) plus CSVs.

Paper metrics (from ShrinkingEval/paper.tex §Evaluation):
  1. Minimal counterexample discovery (ground truth from Lean)
  2. Effectiveness of shrinking (TED to ground truth)
  3. Performance of shrinking (time / TED reduced)
  4. Cost of shrinking (search overhead from enabling it)
  5. Stability across generators (vanilla / CBC / CBC2 / GbE)
"""

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from zss import simple_distance, Node

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# ----------------------------------------------------------------------
# File mapping
# ----------------------------------------------------------------------

STORES = {
    ("Quick",    "none"):      "store.bst.quick.shrink-0.jsonl",
    ("Quick",    "fixed-100"): "store.bst.quick.shrink-100.jsonl",
    ("Quick",    "default"):   "store.bst.quick.shrink-default.jsonl",
    ("Hedgehog", "none"):      "store.bst.hedgehog.shrink-0.jsonl",
    ("Hedgehog", "fixed-100"): "store.bst.hedgehog.shrink-100.jsonl",
    ("Hedgehog", "default"):   "store.bst.hedgehog.shrink-default.jsonl",
    ("Falsify",  "none"):      "store.bst.falsify.shrink-0.jsonl",
    ("Falsify",  "fixed-100"): "store.bst.falsify.shrink-100.jsonl",
    ("Falsify",  "default"):   "store.bst.falsify.shrink-default.jsonl",
}

# Display order (also defines "generator type" grouping).
GROUPS = [
    ("vanilla", [("Quick","Quick"),    ("Hedgehog","Hedgehog"),     ("Falsify","Falsify")]),
    ("CBC",     [("Quick","QuickCBC"), ("Hedgehog","HedgehogCBC"),  ("Falsify","FalsifyCBC")]),
    ("CBC2",    [                      ("Hedgehog","HedgehogCBC2"), ("Falsify","FalsifyCBC2")]),
    ("GbE",     [("Quick","QuickGbE"), ("Hedgehog","HedgehogGbE"),  ("Falsify","FalsifyGbE")]),
]
ALL_STRATEGIES = [s for _, members in GROUPS for _, s in members]

MODES = ["none", "fixed-100", "default"]


# ----------------------------------------------------------------------
# Parsing & TED
# ----------------------------------------------------------------------

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
    """Parse the parenthesised structure from tokens starting at index i.

    Returns (zss.Node, next_index). Each '(...)' group becomes a Node
    labeled '*' with children for everything inside. Atoms become leaf
    Nodes labeled by the atom string. Lists of atoms (like 'T E 2 1 E'
    inside a group) become siblings.
    """
    if i >= len(tokens):
        return None, i
    if tokens[i] == "(":
        node = Node("*")
        j = i + 1
        while j < len(tokens) and tokens[j] != ")":
            child, j = parse_tree(tokens, j)
            if child is not None:
                node.addkid(child)
        return node, j + 1  # skip ')'
    elif tokens[i] == ")":
        return None, i  # shouldn't happen at top level
    else:
        return Node(tokens[i]), i + 1


def cex_to_tree(s: str):
    if not s:
        return None
    toks = tokenize(s)
    if not toks:
        return None
    if toks[0] != "(":
        # Wrap bare atom strings so we still have a Node.
        return Node("ROOT", children=[Node(t) for t in toks])
    tree, _ = parse_tree(toks)
    return tree


def cex_size(s: str) -> int:
    """Cheap proxy: count tokens (open-paren + atom)."""
    if not s:
        return 0
    return sum(1 for t in tokenize(s) if t != ")")


def ted(a: str, b: str) -> int | None:
    """Tree edit distance between two counterexample strings."""
    if not a or not b:
        return None
    ta = cex_to_tree(a)
    tb = cex_to_tree(b)
    if ta is None or tb is None:
        return None
    return simple_distance(ta, tb)


# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------

def load(path: Path):
    return [json.loads(line)["data"]
            for line in path.read_text().splitlines() if line.strip()]


def task_key(r):
    return (r["property"], ",".join(r.get("mutations", []) or []))


def load_lean_groundtruth():
    """Build a map (property_bare, mutation_str) -> ground-truth cex string.

    Lean ground truth lives in store.det.jsonl, strategy='Lean'. The
    property in this store is `prop_X`; we strip the prefix to match the
    bare names used in the new sweep stores.
    """
    rows = load(ROOT / "store.det.jsonl")
    out = {}
    for r in rows:
        if r["strategy"] != "Lean":
            continue
        if r["status"] != "Failed":
            continue
        cex = r.get("counterexample") or r.get("pre_counterexample") or ""
        if not cex:
            continue
        prop = r["property"]
        if prop.startswith("prop_"):
            prop = prop[len("prop_"):]
        muts = ",".join(r.get("mutations", []) or [])
        k = (prop, muts)
        # If multiple Lean rows for the same key, take the smallest cex
        if k not in out or cex_size(cex) < cex_size(out[k]):
            out[k] = cex
    return out


# ----------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------

def annotate(rows, ground_truth, cache_ted=None, progress_prefix=""):
    """Add cex_size, gt_size, ted_to_gt fields to each row in-place.

    cache_ted is shared across all stores so we hit the same (cex, gt)
    pair only once globally.
    """
    if cache_ted is None:
        cache_ted = {}
    import sys
    n_total = len(rows)
    n_done = 0
    n_ted_computed = 0
    n_ted_hit = 0
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
                n_ted_computed += 1
            else:
                n_ted_hit += 1
            r["_ted_to_gt"] = cache_ted[key]
        else:
            r["_ted_to_gt"] = None
        if pre and gt:
            key2 = (pre, gt)
            if key2 not in cache_ted:
                cache_ted[key2] = ted(pre, gt)
                n_ted_computed += 1
            else:
                n_ted_hit += 1
            r["_pre_ted_to_gt"] = cache_ted[key2]
        else:
            r["_pre_ted_to_gt"] = None
        r["_gen_time"] = (r.get("time_pre_failure", 0) or 0) - (r.get("exec_time_pre", 0) or 0)
        n_done += 1
        if n_done % 100 == 0 or n_done == n_total:
            print(f"{progress_prefix}  {n_done}/{n_total} rows (TED: {n_ted_computed} computed, {n_ted_hit} cache hits)", flush=True)
    return rows


def dist(values):
    if not values: return None
    xs = sorted(values)
    n = len(xs)
    return {
        "n": n, "mean": mean(xs), "median": median(xs),
        "p10": xs[n//10], "p90": xs[min(n-1, 9*n//10)],
        "p99": xs[min(n-1, 99*n//100)], "max": xs[-1],
    }


def fmt_dist(d, w=7, prec=2):
    if d is None: return "  —  "
    return f"{d['mean']:>{w}.{prec}f}"


def fmt_d_with_max(d, prec=2):
    if d is None: return "—"
    return f"{d['mean']:.{prec}f} / {d['median']:.{prec}f} / {d['p90']:.{prec}f} / {d['max']:.{prec}f}"


# ----------------------------------------------------------------------
# Report rendering
# ----------------------------------------------------------------------

def render_markdown(all_data, ground_truth):
    """all_data: {(framework, mode): [annotated rows]}"""
    lines = []
    lines.append("# BST analysis — paper draft")
    lines.append("")
    lines.append("All stats restricted to `status == \"Failed\"` rows on BST.")
    lines.append("Ground-truth counterexamples come from `store.det.jsonl` (Lean strategy, exhaustive).")
    lines.append("TED is Zhang-Shasha tree edit distance using `zss.simple_distance`")
    lines.append("over a parens-structured representation of the counterexample.")
    lines.append("")
    lines.append(f"Ground-truth coverage: **{len(ground_truth)}** (property, mutation) pairs from Lean.")
    lines.append("")

    # ---- 1. Coverage --------------------------------------------------
    lines.append("## 1. Coverage")
    lines.append("")
    lines.append("Rows per (strategy, mode), `Failed` only. Expected = 52 combos × 10 trials = 520.")
    lines.append("")
    lines.append("| Strategy | none | fixed-100 | default |")
    lines.append("|---|---:|---:|---:|")
    for s in ALL_STRATEGIES:
        cells = []
        for m in MODES:
            fw = strat_to_framework(s)
            rows = [r for r in all_data[(fw, m)] if r["strategy"] == s and r["status"] == "Failed"]
            cells.append(str(len(rows)))
        lines.append(f"| {s} | {' | '.join(cells)} |")
    lines.append("")

    # ---- 2. Effectiveness (TED to ground truth) -----------------------
    lines.append("## 2. Effectiveness — TED to ground-truth minimum")
    lines.append("")
    lines.append("Lower is better. Distribution of TED(final-cex, lean-ground-truth) across Failed trials.")
    lines.append("Format: **mean / median / p90 / max**.")
    lines.append("")
    lines.append("| Strategy | none | fixed-100 | default |")
    lines.append("|---|---|---|---|")
    for s in ALL_STRATEGIES:
        cells = []
        for m in MODES:
            fw = strat_to_framework(s)
            teds = [r["_ted_to_gt"] for r in all_data[(fw, m)]
                    if r["strategy"] == s and r["status"] == "Failed"
                    and r["_ted_to_gt"] is not None]
            cells.append(fmt_d_with_max(dist(teds), prec=1))
        lines.append(f"| {s} | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.append("")

    # ---- 2b. % of trials at TED=0 -------------------------------------
    lines.append("### 2a. Fraction of trials reaching the ground-truth minimum (TED = 0)")
    lines.append("")
    lines.append("| Strategy | none | fixed-100 | default |")
    lines.append("|---|---:|---:|---:|")
    for s in ALL_STRATEGIES:
        cells = []
        for m in MODES:
            fw = strat_to_framework(s)
            teds = [r["_ted_to_gt"] for r in all_data[(fw, m)]
                    if r["strategy"] == s and r["status"] == "Failed"
                    and r["_ted_to_gt"] is not None]
            if not teds: cells.append("—"); continue
            z = sum(1 for t in teds if t == 0)
            cells.append(f"{100*z/len(teds):.1f}%")
        lines.append(f"| {s} | {' | '.join(cells)} |")
    lines.append("")

    # ---- 3. Performance: time-per-TED-reduced -------------------------
    lines.append("## 3. Performance — time spent shrinking per unit of TED progress")
    lines.append("")
    lines.append("`time_shrinking / max(1, TED(pre) - TED(post))`, in milliseconds per edit.")
    lines.append("Trials where shrinking didn't reduce TED are excluded.")
    lines.append("Format: **mean / median / p90 / max** ms/edit.")
    lines.append("")
    lines.append("| Strategy | fixed-100 | default |")
    lines.append("|---|---|---|")
    for s in ALL_STRATEGIES:
        cells = []
        for m in ["fixed-100", "default"]:
            fw = strat_to_framework(s)
            ratios = []
            for r in all_data[(fw, m)]:
                if r["strategy"] != s or r["status"] != "Failed": continue
                pre_t, post_t = r.get("_pre_ted_to_gt"), r.get("_ted_to_gt")
                if pre_t is None or post_t is None: continue
                reduced = pre_t - post_t
                if reduced <= 0: continue
                ts = (r.get("time_shrinking") or 0) * 1000  # ms
                ratios.append(ts / reduced)
            cells.append(fmt_d_with_max(dist(ratios), prec=2))
        lines.append(f"| {s} | {cells[0]} | {cells[1]} |")
    lines.append("")

    # ---- 4. Cost of enabling shrinking --------------------------------
    lines.append("## 4. Cost of enabling shrinking — search-phase overhead")
    lines.append("")
    lines.append("`time_pre_failure` (s) by mode. Pre-failure search shouldn't depend on shrinking budget — the")
    lines.append("`none` vs `default` gap measures the structural overhead of running with shrinking enabled.")
    lines.append("Per-group ratios (default / none) summarise the relative cost.")
    lines.append("")
    lines.append("| Strategy | none mean | 100 mean | default mean | default/none ratio (median per-task) |")
    lines.append("|---|---:|---:|---:|---:|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        m_none = [r["time_pre_failure"] for r in all_data[(fw,"none")]
                  if r["strategy"]==s and r["status"]=="Failed"]
        m_100 = [r["time_pre_failure"] for r in all_data[(fw,"fixed-100")]
                  if r["strategy"]==s and r["status"]=="Failed"]
        m_def = [r["time_pre_failure"] for r in all_data[(fw,"default")]
                  if r["strategy"]==s and r["status"]=="Failed"]
        # Per-(property,mutation) median time, paired across modes
        def per_task(mode):
            byk = defaultdict(list)
            for r in all_data[(fw,mode)]:
                if r["strategy"]==s and r["status"]=="Failed":
                    byk[task_key(r)].append(r["time_pre_failure"])
            return {k: median(v) for k,v in byk.items()}
        n = per_task("none"); d = per_task("default")
        common = set(n) & set(d)
        ratios = [d[k]/n[k] for k in common if n[k] > 0]
        ratio_label = f"{median(ratios):.2f}x" if ratios else "—"
        lines.append(f"| {s} | {(mean(m_none) if m_none else 0):.4f} | {(mean(m_100) if m_100 else 0):.4f} | {(mean(m_def) if m_def else 0):.4f} | {ratio_label} |")
    lines.append("")

    # ---- 5. Stability across generators -------------------------------
    lines.append("## 5. Stability across generators (default mode)")
    lines.append("")
    lines.append("Per generator family: how do the three frameworks compare on")
    lines.append("**TED to ground truth** and **time_pre_failure**?")
    lines.append("")
    for label, members in GROUPS:
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Framework | TED (mean / med / max) | time_pre (s, mean) | n |")
        lines.append("|---|---|---:|---:|")
        for fw, s in members:
            rows = [r for r in all_data[(fw, "default")]
                    if r["strategy"]==s and r["status"]=="Failed"]
            teds = [r["_ted_to_gt"] for r in rows if r["_ted_to_gt"] is not None]
            t_pre = [r["time_pre_failure"] for r in rows]
            lines.append(f"| {s} | {fmt_d_with_max(dist(teds), prec=1)} | "
                         f"{(mean(t_pre) if t_pre else 0):.4f} | {len(rows)} |")
        lines.append("")

    # ---- 6. Time decomposition (per-paper convention) -----------------
    lines.append("## 6. Time decomposition (default mode)")
    lines.append("")
    lines.append("Per the paper: ")
    lines.append("- **execution** = `exec_time_pre` (predicate force time before failure)")
    lines.append("- **generation** = `time_pre_failure - exec_time_pre` (gen + harness)")
    lines.append("- **shrinking** = `time_shrinking`")
    lines.append("")
    lines.append("Mean seconds across Failed trials.")
    lines.append("")
    lines.append("| Strategy | execution | generation | shrinking | total |")
    lines.append("|---|---:|---:|---:|---:|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        rows = [r for r in all_data[(fw,"default")]
                if r["strategy"]==s and r["status"]=="Failed"]
        if not rows:
            lines.append(f"| {s} | — | — | — | — |")
            continue
        ex = mean(r.get("exec_time_pre",0) or 0 for r in rows)
        ge = mean(r["_gen_time"] for r in rows)
        sh = mean(r.get("time_shrinking",0) or 0 for r in rows)
        lines.append(f"| {s} | {ex*1000:.2f} ms | {ge*1000:.2f} ms | {sh*1000:.2f} ms | {(ex+ge+sh)*1000:.2f} ms |")
    lines.append("")

    # ---- 7. Shrink-attempt counts ------------------------------------
    lines.append("## 7. Shrink-attempt counts (default mode)")
    lines.append("")
    lines.append("Per failed trial: how much work does the shrinker do? `passed` = candidate")
    lines.append("kept the property holding (rejected by shrinker), `failed` = property still broke")
    lines.append("(accepted as new minimum), `discarded` = precondition rejected.")
    lines.append("")
    lines.append("| Strategy | passed | failed (= accepted shrinks) | discarded | total |")
    lines.append("|---|---:|---:|---:|---:|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        rows = [r for r in all_data[(fw,"default")]
                if r["strategy"]==s and r["status"]=="Failed"]
        if not rows:
            lines.append(f"| {s} | — | — | — | — |")
            continue
        sp = mean(r.get("shrinking_passed",0) or 0 for r in rows)
        sf = mean(r.get("shrinking_failed",0) or 0 for r in rows)
        sd = mean(r.get("shrinking_discarded",0) or 0 for r in rows)
        lines.append(f"| {s} | {sp:.1f} | {sf:.1f} | {sd:.1f} | {sp+sf+sd:.1f} |")
    lines.append("")

    # ---- 8. Pre vs post counterexample size --------------------------
    lines.append("## 8. Pre vs post-shrinking counterexample size (default mode)")
    lines.append("")
    lines.append("Token count of `pre_counterexample` and `counterexample`. ")
    lines.append("`Δ` = how much the shrinker compressed the input.")
    lines.append("")
    lines.append("| Strategy | mean pre | mean post | mean Δ | mean Δ % |")
    lines.append("|---|---:|---:|---:|---:|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        rows = [r for r in all_data[(fw,"default")]
                if r["strategy"]==s and r["status"]=="Failed"]
        if not rows:
            lines.append(f"| {s} | — | — | — | — |")
            continue
        pre = mean(r["_pre_size"] for r in rows)
        post = mean(r["_cex_size"] for r in rows)
        delta = pre - post
        pct = 100 * delta / pre if pre else 0
        lines.append(f"| {s} | {pre:.1f} | {post:.1f} | {delta:.1f} | {pct:.1f}% |")
    lines.append("")

    return "\n".join(lines)


def strat_to_framework(s):
    if s.startswith("Quick"): return "Quick"
    if s.startswith("Hedgehog"): return "Hedgehog"
    if s.startswith("Falsify"): return "Falsify"
    raise ValueError(s)


def write_csv(all_data, ground_truth, csv_path: Path):
    """Wide CSV: one row per trial, with derived columns."""
    cols = ["framework","strategy","mode","property","mutation","trial",
            "status","tests","discards","shrinking_passed","shrinking_failed","shrinking_discarded",
            "exec_time_pre","gen_time","time_shrinking","time_pre_failure",
            "pre_size","cex_size","gt_size","pre_ted_to_gt","ted_to_gt"]
    with csv_path.open("w") as f:
        f.write(",".join(cols) + "\n")
        for (fw, mode), rows in all_data.items():
            for r in rows:
                row = {
                    "framework": fw, "strategy": r["strategy"], "mode": mode,
                    "property": r["property"], "mutation": ",".join(r.get("mutations",[]) or []),
                    "trial": r["trial"], "status": r["status"],
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
                f.write(",".join("" if v is None else str(v) for v in (row[c] for c in cols)) + "\n")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    print("loading Lean ground truth...")
    gt = load_lean_groundtruth()
    print(f"  {len(gt)} (property, mutation) pairs with ground truth")

    print("loading stores + computing TED (shared cache across stores)...")
    all_data = {}
    shared_cache = {}
    for (fw, mode), filename in STORES.items():
        rows = load(ROOT / filename)
        print(f"  [{fw}/{mode}] loading {filename}, {len(rows)} rows")
        annotate(rows, gt, cache_ted=shared_cache, progress_prefix=f"  [{fw}/{mode}]")
        all_data[(fw, mode)] = rows
        print(f"  [{fw}/{mode}] done. (cache size: {len(shared_cache)})", flush=True)

    print("rendering markdown report...")
    md = render_markdown(all_data, gt)
    md_path = FIG / "BST_ANALYSIS.md"
    md_path.write_text(md)
    print(f"  wrote {md_path}")

    print("writing CSV export...")
    csv_path = FIG / "BST_ANALYSIS.csv"
    write_csv(all_data, gt, csv_path)
    print(f"  wrote {csv_path}")


if __name__ == "__main__":
    main()
