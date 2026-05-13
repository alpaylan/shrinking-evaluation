#!/usr/bin/env python3
"""
BST analysis v2 — per-task aggregation with medians.

Reads figures/BST_ANALYSIS.csv (produced by bst_analysis.py) and rewrites
the tables using two-level aggregation:

1. **Within a task** (property, mutation): collapse the 10 trials with
   median (robust to one slow/fast outlier trial).
2. **Across tasks**: report mean AND median of the per-task medians.

This avoids the mean-skew where one expensive (insert_3 / union_8) task
dominates the average across the 52 tasks.

Format throughout: `task-median / cross-task-median / cross-task-mean / max`.
"""

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
CSV_PATH = FIG / "BST_ANALYSIS.csv"
OUT_MD = FIG / "BST_ANALYSIS_v2.md"

GROUPS = [
    ("vanilla", [("Quick","Quick"),    ("Hedgehog","Hedgehog"),     ("Falsify","Falsify")]),
    ("CBC",     [("Quick","QuickCBC"), ("Hedgehog","HedgehogCBC"),  ("Falsify","FalsifyCBC")]),
    ("CBC2",    [                      ("Hedgehog","HedgehogCBC2"), ("Falsify","FalsifyCBC2")]),
    ("GbE",     [("Quick","QuickGbE"), ("Hedgehog","HedgehogGbE"),  ("Falsify","FalsifyGbE")]),
]
ALL_STRATEGIES = [s for _, members in GROUPS for _, s in members]
MODES = ["none", "fixed-100", "default"]


def load_csv():
    rows = []
    with CSV_PATH.open() as f:
        for r in csv.DictReader(f):
            # cast numerics
            for k in ("tests","discards","shrinking_passed","shrinking_failed",
                      "shrinking_discarded","exec_time_pre","gen_time","time_shrinking",
                      "time_pre_failure","pre_size","cex_size","gt_size",
                      "pre_ted_to_gt","ted_to_gt","trial"):
                if r.get(k) == "":
                    r[k] = None
                elif r.get(k) is not None:
                    try:
                        r[k] = float(r[k]) if "." in r[k] or r[k].lower() == "nan" else int(r[k])
                    except ValueError:
                        pass
            rows.append(r)
    return rows


def task_medians(rows, val_fn, only_failed=True):
    """Group by (property, mutation), compute median of val_fn within
    each task. Drop tasks where val_fn returned None for every trial."""
    bytask = defaultdict(list)
    for r in rows:
        if only_failed and r["status"] != "Failed":
            continue
        v = val_fn(r)
        if v is None:
            continue
        bytask[(r["property"], r["mutation"])].append(v)
    return [median(vs) for vs in bytask.values() if vs]


def summarize(xs):
    if not xs:
        return None
    xs_sorted = sorted(xs)
    n = len(xs_sorted)
    return {
        "n": n,
        "mean": mean(xs_sorted),
        "median": median(xs_sorted),
        "p90": xs_sorted[min(n-1, 9*n//10)],
        "max": xs_sorted[-1],
    }


def fmt(s, prec=2):
    if s is None: return "—"
    return f"{s['median']:.{prec}f} / {s['mean']:.{prec}f} / {s['p90']:.{prec}f} / {s['max']:.{prec}f}"


def fmt_med(s, prec=2):
    if s is None: return "—"
    return f"{s['median']:.{prec}f}"


def fmt_med_mean(s, prec=2):
    if s is None: return "—"
    return f"{s['median']:.{prec}f} / {s['mean']:.{prec}f}"


def filter_rows(all_rows, framework, strategy, mode):
    return [r for r in all_rows
            if r["framework"] == framework and r["strategy"] == strategy
            and r["mode"] == mode]


def strat_to_framework(s):
    if s.startswith("Quick"): return "Quick"
    if s.startswith("Hedgehog"): return "Hedgehog"
    if s.startswith("Falsify"): return "Falsify"
    raise ValueError(s)


def render(all_rows):
    L = []
    L.append("# BST analysis — v2 (per-task aggregation + medians)")
    L.append("")
    L.append("**Aggregation rule for every table:**")
    L.append("1. *Within each task* `(property, mutation)`, collapse the 10 trials with **median**.")
    L.append("2. *Across the 52 tasks*, report **median / mean / p90 / max** of the per-task medians.")
    L.append("")
    L.append("This drops the influence of outlier trials within a task AND prevents one")
    L.append("expensive task (insert_3 / union_8) from dominating the cross-task mean.")
    L.append("")
    L.append("Format: **task-median / cross-task-mean / p90 / max** for cross-task distribution columns,")
    L.append("or **task-median / cross-task-mean** where a single headline is enough.")
    L.append("")

    # ---- 2. Effectiveness (TED to ground truth) ---------------------
    L.append("## 2. Effectiveness — TED to ground-truth minimum")
    L.append("")
    L.append("Lower is better. Per task: median TED across trials. Then cross-task:")
    L.append("median / mean / p90 / max of those per-task medians.")
    L.append("")
    L.append("| Strategy | none | fixed-100 | default |")
    L.append("|---|---|---|---|")
    for s in ALL_STRATEGIES:
        cells = []
        for m in MODES:
            fw = strat_to_framework(s)
            rs = filter_rows(all_rows, fw, s, m)
            tms = task_medians(rs, lambda r: r["ted_to_gt"])
            cells.append(fmt(summarize(tms), prec=1))
        L.append(f"| {s} | {' | '.join(cells)} |")
    L.append("")

    # ---- 2a. % of tasks where the median trial reaches TED=0 --------
    L.append("### 2a. Fraction of *tasks* whose median trial reaches TED = 0")
    L.append("")
    L.append("Per task: take the median TED across its 10 trials. Count the task as 'solved'")
    L.append("if that per-task median is 0 — i.e., at least half the trials hit the optimum.")
    L.append("")
    L.append("| Strategy | none | fixed-100 | default |")
    L.append("|---|---:|---:|---:|")
    for s in ALL_STRATEGIES:
        cells = []
        for m in MODES:
            fw = strat_to_framework(s)
            rs = filter_rows(all_rows, fw, s, m)
            tms = task_medians(rs, lambda r: r["ted_to_gt"])
            if not tms: cells.append("—"); continue
            z = sum(1 for t in tms if t == 0)
            cells.append(f"{100*z/len(tms):.1f}%")
        L.append(f"| {s} | {' | '.join(cells)} |")
    L.append("")

    # ---- 3. Performance: ms per TED edit reduced --------------------
    L.append("## 3. Performance — milliseconds spent shrinking per unit of TED progress")
    L.append("")
    L.append("Per trial: `time_shrinking / (pre_TED − post_TED)` if reduction > 0, else excluded.")
    L.append("Per task: median ms/edit. Cross-task: median / mean / p90 / max.")
    L.append("")
    L.append("| Strategy | fixed-100 | default |")
    L.append("|---|---|---|")
    for s in ALL_STRATEGIES:
        cells = []
        for m in ["fixed-100","default"]:
            fw = strat_to_framework(s)
            rs = filter_rows(all_rows, fw, s, m)
            def rate(r):
                pre, post = r["pre_ted_to_gt"], r["ted_to_gt"]
                if pre is None or post is None: return None
                d = pre - post
                if d <= 0: return None
                return (r["time_shrinking"] or 0) * 1000 / d
            tms = task_medians(rs, rate)
            cells.append(fmt(summarize(tms), prec=2))
        L.append(f"| {s} | {' | '.join(cells)} |")
    L.append("")

    # ---- 4. Cost of enabling shrinking ------------------------------
    L.append("## 4. Cost of enabling shrinking — search-phase overhead")
    L.append("")
    L.append("`time_pre_failure` (s). Per task: median across 10 trials. Cross-task: median, mean.")
    L.append("`default/none` is the task-level paired ratio (geometric over tasks where both exist).")
    L.append("")
    L.append("| Strategy | none (med / mean) | 100 (med / mean) | default (med / mean) | default/none task-median ratio |")
    L.append("|---|---|---|---|---:|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        cells = []
        for m in MODES:
            tms = task_medians(filter_rows(all_rows, fw, s, m), lambda r: r["time_pre_failure"])
            cells.append(fmt_med_mean(summarize(tms), prec=4))
        # Per-task paired ratio: default_med(task) / none_med(task)
        def per_task_med(mode):
            byk = defaultdict(list)
            for r in filter_rows(all_rows, fw, s, mode):
                if r["status"] != "Failed": continue
                byk[(r["property"], r["mutation"])].append(r["time_pre_failure"])
            return {k: median(v) for k, v in byk.items()}
        n_md, d_md = per_task_med("none"), per_task_med("default")
        ratios = [d_md[k]/n_md[k] for k in (set(n_md) & set(d_md)) if n_md[k] > 0]
        ratio_label = f"{median(ratios):.2f}x" if ratios else "—"
        L.append(f"| {s} | {cells[0]} | {cells[1]} | {cells[2]} | {ratio_label} |")
    L.append("")

    # ---- 5. Stability across generators (default) -------------------
    L.append("## 5. Stability across generators (default mode)")
    L.append("")
    for label, members in GROUPS:
        L.append(f"### {label}")
        L.append("")
        L.append("| Framework | TED (med / mean / p90 / max) | time_pre s (med / mean) | n tasks |")
        L.append("|---|---|---|---:|")
        for fw, s in members:
            rs = filter_rows(all_rows, fw, s, "default")
            ted_tms = task_medians(rs, lambda r: r["ted_to_gt"])
            t_tms = task_medians(rs, lambda r: r["time_pre_failure"])
            L.append(f"| {s} | {fmt(summarize(ted_tms), prec=1)} | "
                     f"{fmt_med_mean(summarize(t_tms), prec=4)} | "
                     f"{len(ted_tms) if ted_tms else 0} |")
        L.append("")

    # ---- 6. Time decomposition (default) ----------------------------
    L.append("## 6. Time decomposition (default mode)")
    L.append("")
    L.append("Per-task medians (ms). Then cross-task **median / mean**.")
    L.append("")
    L.append("| Strategy | execution (med/mean) | generation (med/mean) | shrinking (med/mean) | total (med) |")
    L.append("|---|---|---|---|---:|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        rs = filter_rows(all_rows, fw, s, "default")
        ex_tms = task_medians(rs, lambda r: (r["exec_time_pre"] or 0)*1000)
        ge_tms = task_medians(rs, lambda r: (r["gen_time"] or 0)*1000)
        sh_tms = task_medians(rs, lambda r: (r["time_shrinking"] or 0)*1000)
        ex, ge, sh = summarize(ex_tms), summarize(ge_tms), summarize(sh_tms)
        total = (ex["median"] if ex else 0) + (ge["median"] if ge else 0) + (sh["median"] if sh else 0)
        L.append(f"| {s} | {fmt_med_mean(ex, prec=2)} | {fmt_med_mean(ge, prec=2)} | "
                 f"{fmt_med_mean(sh, prec=2)} | {total:.2f} ms |")
    L.append("")

    # ---- 7. Shrink-attempt counts (default) -------------------------
    L.append("## 7. Shrink-attempt counts (default mode)")
    L.append("")
    L.append("Per-task medians across 10 trials. Cross-task **median / mean**.")
    L.append("")
    L.append("| Strategy | passed (med/mean) | failed (med/mean) | discarded (med/mean) |")
    L.append("|---|---|---|---|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        rs = filter_rows(all_rows, fw, s, "default")
        sp = summarize(task_medians(rs, lambda r: r["shrinking_passed"] or 0))
        sf = summarize(task_medians(rs, lambda r: r["shrinking_failed"] or 0))
        sd = summarize(task_medians(rs, lambda r: r["shrinking_discarded"] or 0))
        L.append(f"| {s} | {fmt_med_mean(sp, prec=1)} | {fmt_med_mean(sf, prec=1)} | "
                 f"{fmt_med_mean(sd, prec=1)} |")
    L.append("")

    # ---- 8. Pre vs post counterexample size (default) ----------------
    L.append("## 8. Pre vs post-shrinking counterexample size (default mode)")
    L.append("")
    L.append("Per-task medians of token-count. Cross-task **median / mean**.")
    L.append("")
    L.append("| Strategy | mean pre (med/mean) | mean post (med/mean) | mean Δ (med/mean) | mean Δ % |")
    L.append("|---|---|---|---|---:|")
    for s in ALL_STRATEGIES:
        fw = strat_to_framework(s)
        rs = filter_rows(all_rows, fw, s, "default")
        pre = summarize(task_medians(rs, lambda r: r["pre_size"]))
        post = summarize(task_medians(rs, lambda r: r["cex_size"]))
        delta = summarize(task_medians(rs, lambda r: (r["pre_size"] or 0) - (r["cex_size"] or 0)))
        # %Δ per task
        def pct(r):
            if not r["pre_size"]: return None
            return 100 * ((r["pre_size"] or 0) - (r["cex_size"] or 0)) / (r["pre_size"] or 1)
        pct_tms = task_medians(rs, pct)
        pct_s = summarize(pct_tms)
        pct_str = f"{pct_s['median']:.1f}%" if pct_s else "—"
        L.append(f"| {s} | {fmt_med_mean(pre, prec=1)} | {fmt_med_mean(post, prec=1)} | "
                 f"{fmt_med_mean(delta, prec=1)} | {pct_str} |")
    L.append("")

    return "\n".join(L)


def main():
    print(f"loading {CSV_PATH}...")
    rows = load_csv()
    print(f"  {len(rows)} rows loaded")
    md = render(rows)
    OUT_MD.write_text(md)
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
