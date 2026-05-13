"""
Counterexample-size analysis for the shrinking-evaluation experiment.

Reads store.jsonl, computes tree depth (max paren nesting) for every
Failed-status counterexample, and emits:
  - figures/shrinking_summary.md   — per-(workload, strategy) median/IQR table
  - figures/<workload>_heatmap.png — median depth per (mutation, property) x strategy
  - figures/<workload>_box.png     — depth distribution per strategy
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parent
STORE = REPO / "store.jsonl"
FIGURES = REPO / "figures"

# Strategies excluded from the shrinker comparison. Each entry needs a reason
# that survives in the output so future readers know why the cell is missing.
EXCLUDED_STRATEGIES = {
    "Size": (
        "Size is a parameterised input-size generator (reads BSTSIZE from the "
        "environment), not a shrinker. With BSTSIZE unset every trial crashes "
        "in `getEnv` and records the exception text as a fake counterexample. "
        "Belongs in a separate input-size sweep, not in this comparison."
    ),
}


def tree_depth(s: str) -> int:
    depth = max_d = 0
    for c in s:
        if c == "(":
            depth += 1
            if depth > max_d:
                max_d = depth
        elif c == ")":
            depth -= 1
    return max_d


def parse_time(s: str | None) -> float | None:
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    if s.endswith("s"):
        s = s[:-1]
    try:
        return float(s)
    except ValueError:
        return None


def audit_status(out_path: Path):
    # Count rows by (workload, strategy, shrinks, status) and summarise abort
    # rates. Aborted rows usually carry a runtime error in `error` — surface
    # the most common one per (workload, strategy) so generator crashes
    # (e.g. Falsify Range.withOrigin precondition) become visible instead of
    # being silently dropped by the Failed-only filter downstream.
    counts = defaultdict(lambda: defaultdict(int))   # (wl, strat, shr) -> {status: n}
    errors = defaultdict(lambda: defaultdict(int))   # (wl, strat) -> {error_head: n}
    with STORE.open() as f:
        for line in f:
            obj = json.loads(line)
            d = obj.get("data", {})
            wl = d.get("workload"); strat = d.get("strategy"); shr = d.get("shrinks")
            status = (d.get("status") or "").lower()
            counts[(wl, strat, shr)][status] += 1
            if status == "aborted":
                # Skip the generic "Process failed with status" wrapper and
                # surface the actual stderr / Haskell exception line so e.g.
                # "withOrigin: origin not within bounds" is visible instead of
                # being hidden behind exit status: 1.
                err_raw = d.get("error") or ""
                useful = next(
                    (
                        ln.strip().lstrip("stderr:").strip()
                        for ln in err_raw.splitlines()
                        if ln.strip() and not ln.startswith("Process failed")
                    ),
                    err_raw.splitlines()[0] if err_raw else "(no error msg)",
                )
                errors[(wl, strat)][useful[:140]] += 1

    lines = [
        "# Status audit\n",
        "Row counts per (workload, strategy, shrinks) split by status. "
        "**aborted** rows are runtime crashes that the Failed-only filter "
        "in the rest of the report drops; high abort rates often mean a "
        "broken generator. Top error lines per (workload, strategy) are "
        "listed below the table.\n",
        "| workload | strategy | shrinks | Failed | aborted | timed_out | other | abort% |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    def _key(k):
        wl, strat, shr = k
        return (wl or "", strat or "", -1 if shr is None else shr)
    for key in sorted(counts, key=_key):
        wl, strat, shr = key
        c = counts[key]
        f_ = c.get("failed", 0)
        a_ = c.get("aborted", 0)
        t_ = c.get("timed_out", 0)
        o_ = sum(c.values()) - f_ - a_ - t_
        total = f_ + a_ + t_ + o_
        pct = (100.0 * a_ / total) if total else 0
        shr_lbl = "—" if shr is None else str(shr)
        lines.append(f"| {wl} | {strat} | {shr_lbl} | {f_} | {a_} | {t_} | {o_} | {pct:.0f}% |")

    lines.append("\n## Top abort error per (workload, strategy)\n")
    for (wl, strat), errs in sorted(errors.items()):
        if not errs:
            continue
        top_err, top_n = max(errs.items(), key=lambda kv: kv[1])
        lines.append(f"- **{wl} × {strat}** ({top_n} aborted): `{top_err}`")

    out_path.write_text("\n".join(lines) + "\n")


def load_failed_with_counterexample():
    rows = []
    excluded = 0
    with STORE.open() as f:
        for line in f:
            obj = json.loads(line)
            d = obj.get("data", {})
            # Existing BST/RBT/STLC workloads emit "Failed"; the new
            # workloads (nonempty-containers, psqueues) emit "failed".
            # Accept both.
            if (d.get("status") or "").lower() != "failed":
                continue
            cex = d.get("counterexample") or ""
            if not cex:
                continue
            strategy = d.get("strategy")
            if strategy in EXCLUDED_STRATEGIES:
                excluded += 1
                continue
            pre = d.get("pre_counterexample") or ""
            rows.append(
                {
                    "workload": d.get("workload"),
                    "mutation": (d.get("mutations") or [None])[0],
                    "property": d.get("property"),
                    "strategy": strategy,
                    "depth": tree_depth(cex),
                    "len": len(cex),
                    # pre_depth/pre_len are None when the run pre-dates the
                    # pre_counterexample field; renders as "—" downstream.
                    "pre_depth": tree_depth(pre) if pre else None,
                    "pre_len": len(pre) if pre else None,
                    "time": parse_time(d.get("time")),
                    # Each entry self-identifies its ETNA_SHRINKS config so
                    # multi-config sweeps can be split into cohorts.
                    "shrinks": d.get("shrinks"),
                    # Phase timing fields (None for pre-instrumentation rows).
                    "exec_time_pre":    d.get("exec_time_pre"),
                    "exec_time_shrink": d.get("exec_time_shrink"),
                    "time_pre_failure": d.get("time_pre_failure"),
                    "time_shrinking":   d.get("time_shrinking"),
                }
            )
    return rows, excluded


def group(rows, keys, value_key="depth"):
    out = defaultdict(list)
    for r in rows:
        v = r.get(value_key)
        if v is None:
            continue
        out[tuple(r[k] for k in keys)].append(v)
    return out


def quartiles(xs):
    n = len(xs)
    if n == 0:
        return None
    s = sorted(xs)
    median = statistics.median(s)
    p25 = np.quantile(s, 0.25)
    p75 = np.quantile(s, 0.75)
    return median, p25, p75, n


def fmt_time(x: float) -> str:
    if x >= 1.0:
        return f"{x:.2f}s"
    if x >= 1e-3:
        return f"{x*1e3:.1f}ms"
    return f"{x*1e6:.0f}µs"


def write_summary_table(rows, out_path: Path):
    # Pivot by (workload, strategy, shrinks). A None shrinks value means the
    # row is from a pre-instrumentation run; we treat it as a separate cohort.
    by_wss = group(rows, ["workload", "strategy", "shrinks"], value_key="depth")
    by_wss_pre = group(rows, ["workload", "strategy", "shrinks"], value_key="pre_depth")
    by_wss_time = group(rows, ["workload", "strategy", "shrinks"], value_key="time")
    workloads = sorted({k[0] for k in by_wss})
    strategies = sorted({k[1] for k in by_wss})
    shrinks_vals = sorted(
        {k[2] for k in by_wss},
        key=lambda x: (-1 if x is None else x),
    )

    def shrinks_label(v):
        return "legacy" if v is None else f"shrinks={v}"

    lines = [
        "# Counterexample size + time summary\n",
        "Per (workload, strategy, ETNA_SHRINKS) cell across all (mutation, "
        "property, trial) trials. **Depth** = max paren nesting in the "
        "(post-shrink) counterexample (lower is better). **Pre depth** = depth "
        "of the *first* failing input before shrinking; **Δ** = pre − post "
        "(how much shrinking reduced the input). **Time** = wall-clock to find "
        "the counterexample. All reduced via median / p25–p75 IQR. Cohorts "
        "with no `shrinks` field (legacy runs) are shown as `legacy`.\n",
    ]
    for w in workloads:
        lines.append(f"\n## {w}\n")
        for sv in shrinks_vals:
            cells_for_sv = [(w_, s_, sv_) for (w_, s_, sv_) in by_wss if w_ == w and sv_ == sv]
            if not cells_for_sv:
                continue
            lines.append(f"\n### {shrinks_label(sv)}\n")
            lines.append("| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |")
            lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
            for s in strategies:
                d_stats = quartiles(by_wss.get((w, s, sv), []))
                t_stats = quartiles(by_wss_time.get((w, s, sv), []))
                pre_stats = quartiles(by_wss_pre.get((w, s, sv), []))
                if d_stats is None:
                    continue
                d_med, d_p25, d_p75, n = d_stats
                if pre_stats is None:
                    pre_cells = "— | —"
                else:
                    pre_med, _, _, _ = pre_stats
                    delta = pre_med - d_med
                    pre_cells = f"{pre_med:g} | {delta:+g}"
                if t_stats is None:
                    t_cells = "— | — | —"
                else:
                    t_med, t_p25, t_p75, _ = t_stats
                    t_cells = f"{fmt_time(t_med)} | {fmt_time(t_p25)} | {fmt_time(t_p75)}"
                lines.append(
                    f"| {s} | {n} | {d_med:g} | {d_p25:g} | {d_p75:g} | {pre_cells} | {t_cells} |"
                )

    # Footnotes: excluded strategies + zero-coverage cells.
    lines.append("\n## Notes\n")
    for name, reason in sorted(EXCLUDED_STRATEGIES.items()):
        lines.append(f"- **{name} excluded.** {reason}")
    seen_ws = {(w, s) for (w, s, _) in by_wss}
    zero_cells = [
        (w, s)
        for w in workloads
        for s in strategies
        if (w, s) not in seen_ws
    ]
    if zero_cells:
        lines.append(
            "- **Zero-data cells (timeout-only):** "
            + ", ".join(f"{w}/{s}" for w, s in zero_cells)
            + ". The strategy ran but never produced a Failed result within the "
            "configured timeout, so there's nothing to score. Treat as 'failed "
            "to find any counterexample,' not 'large counterexample.'"
        )

    # Shrinking-effect breakdown for the three strategies that go through a
    # framework shrinker (Quick/Correct via QuickCheck, Hedgehog, Falsify).
    # Surfaces length-level shrinking because depth alone misses value-level
    # reductions. Lean/LeanRev/Small/SmallRev are skipped — they enumerate
    # from small, so pre == post by construction.
    lines.append("\n## Shrinking effect (framework shrinkers only)\n")
    lines.append(
        "Per (workload, strategy, shrinks) cell. **Δdepth** = pre median depth − "
        "post median depth (positive means shrinking made the tree shallower). "
        "**Δlen** = pre median character length − post median length (positive "
        "means shrinking reduced the printed term). **% changed** = fraction of "
        "trials where pre ≠ post by character. *Note*: Quick/Correct currently "
        "ignore ETNA_SHRINKS — QuickCheck always shrinks until exhausted, so "
        "their pre/post is captured but the same across cohorts.\n"
    )
    lines.append("| workload | strategy | shrinks | n | depth med (pre→post) | Δdepth | len med (pre→post) | Δlen | % changed |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    framework_strategies = (
        # BST/RBT/STLC naming (mkMain-driven, capitalized).
        "Quick", "QuickCBC", "QuickGbE",
        "Hedgehog", "HedgehogCBC", "HedgehogGbE",
        "Falsify", "FalsifyCBC", "FalsifyGbE",
        # nonempty-containers / psqueues naming (etna-runner, lowercase).
        "quickcheck", "hedgehog", "falsify", "smallcheck",
    )
    for w in workloads:
        for s in framework_strategies:
            for sv in shrinks_vals:
                # Filter rows for this cell.
                sub = [
                    r for r in rows
                    if r["workload"] == w
                    and r["strategy"] == s
                    and r.get("shrinks") == sv
                    and r.get("pre_depth") is not None
                ]
                if not sub:
                    continue
                pre_d_med = statistics.median([r["pre_depth"] for r in sub])
                post_d_med = statistics.median([r["depth"] for r in sub])
                pre_l_med = statistics.median([r["pre_len"] for r in sub])
                post_l_med = statistics.median([r["len"] for r in sub])
                changed = sum(1 for r in sub if r["pre_len"] != r["len"])
                pct = 100 * changed / len(sub)
                lines.append(
                    f"| {w} | {s} | {shrinks_label(sv)} | {len(sub)} | "
                    f"{pre_d_med:g}→{post_d_med:g} | {pre_d_med - post_d_med:+g} | "
                    f"{pre_l_med:g}→{post_l_med:g} | {pre_l_med - post_l_med:+g} | "
                    f"{pct:.0f}% |"
                )

    # Phase timing breakdown. Decomposes total time into:
    #   exec_pre  + non-exec_pre  = time_pre_failure
    #   exec_shr  + non-exec_shr  = time_shrinking
    # plus a small harness overhead.
    lines.append("\n## Phase timing breakdown\n")
    lines.append(
        "Per (workload, strategy, shrinks) cell. **exec** = time inside the "
        "user's property body. **non-exec** = wall-clock minus exec — covers "
        "input generation, framework bookkeeping, and (for shrinking) the "
        "shrink-algorithm itself. **pre** = before first observed failure; "
        "**shrink** = from first failure to final reported counterexample. "
        "**total** = pre + shrink. **overhead** = `time` − total (small "
        "harness gap; should be near zero). Median across trials. Cells "
        "missing the timing fields render as `—`.\n"
    )
    for w in workloads:
        # Filter rows that have phase-timing fields populated.
        sub_w = [r for r in rows if r["workload"] == w and r.get("time_pre_failure") is not None]
        if not sub_w:
            continue
        lines.append(f"\n### {w}\n")
        lines.append("| strategy | shrinks | n | exec pre | non-exec pre | exec shrink | non-exec shrink | total | overhead |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for sv in shrinks_vals:
            for s in strategies:
                cell = [r for r in sub_w if r["strategy"] == s and r.get("shrinks") == sv]
                if not cell:
                    continue
                ep_med  = statistics.median([r["exec_time_pre"]    for r in cell])
                es_med  = statistics.median([r["exec_time_shrink"] for r in cell])
                tp_med  = statistics.median([r["time_pre_failure"] for r in cell])
                ts_med  = statistics.median([r["time_shrinking"]   for r in cell])
                t_med   = statistics.median([r["time"]             for r in cell])
                nep = max(0.0, tp_med - ep_med)
                nes = max(0.0, ts_med - es_med)
                total = tp_med + ts_med
                overhead = t_med - total
                lines.append(
                    f"| {s} | {shrinks_label(sv)} | {len(cell)} | "
                    f"{fmt_time(ep_med)} | {fmt_time(nep)} | "
                    f"{fmt_time(es_med)} | {fmt_time(nes)} | "
                    f"{fmt_time(total)} | {fmt_time(overhead)} |"
                )

    out_path.write_text("\n".join(lines) + "\n")


def heatmap_per_workload(rows, out_dir: Path, value_key: str, label: str, suffix: str, fmt_cell):
    by_full = group(
        rows, ["workload", "mutation", "property", "strategy"], value_key=value_key
    )
    workloads = sorted({k[0] for k in by_full})
    for w in workloads:
        cells = {k[1:]: v for k, v in by_full.items() if k[0] == w}
        bugs = sorted({(m, p) for (m, p, _) in cells})
        strategies = sorted({s for (_, _, s) in cells})
        if not bugs or not strategies:
            continue
        mat = np.full((len(bugs), len(strategies)), np.nan)
        for i, (m, p) in enumerate(bugs):
            for j, s in enumerate(strategies):
                vs = cells.get((m, p, s))
                if vs:
                    mat[i, j] = statistics.median(vs)

        # Time spans many orders of magnitude; log-scale the colorbar for time.
        norm = None
        if value_key == "time" and np.nanmin(mat) > 0:
            from matplotlib.colors import LogNorm

            norm = LogNorm(vmin=np.nanmin(mat), vmax=np.nanmax(mat))

        fig, ax = plt.subplots(
            figsize=(max(6, 0.6 * len(strategies) + 2), max(4, 0.3 * len(bugs) + 2))
        )
        im = ax.imshow(mat, aspect="auto", cmap="viridis", norm=norm)
        ax.set_xticks(range(len(strategies)))
        ax.set_xticklabels(strategies, rotation=45, ha="right")
        ax.set_yticks(range(len(bugs)))
        ax.set_yticklabels([f"{m} / {p}" for (m, p) in bugs], fontsize=8)
        ax.set_title(f"{w}: median counterexample {label}")
        nan_mean = np.nanmean(mat)
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                v = mat[i, j]
                if not np.isnan(v):
                    ax.text(
                        j,
                        i,
                        fmt_cell(v),
                        ha="center",
                        va="center",
                        color="white" if v > nan_mean else "black",
                        fontsize=7,
                    )
        plt.colorbar(im, ax=ax, label=f"median {label}")
        plt.tight_layout()
        plt.savefig(out_dir / f"{w}_{suffix}.png", dpi=120)
        plt.close(fig)


def box_per_workload(rows, out_dir: Path, value_key: str, ylabel: str, suffix: str, log: bool = False):
    by_ws = group(rows, ["workload", "strategy"], value_key=value_key)
    workloads = sorted({k[0] for k in by_ws})
    for w in workloads:
        strategies = sorted({k[1] for k in by_ws if k[0] == w})
        data = [by_ws[(w, s)] for s in strategies]
        fig, ax = plt.subplots(figsize=(max(6, 0.7 * len(strategies) + 2), 4))
        ax.boxplot(data, tick_labels=strategies, showfliers=False)
        ax.set_title(f"{w}: counterexample {ylabel} distribution")
        ax.set_ylabel(ylabel)
        if log:
            ax.set_yscale("log")
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()
        plt.savefig(out_dir / f"{w}_{suffix}.png", dpi=120)
        plt.close(fig)


def pareto_per_workload(rows, out_dir: Path):
    """Median time vs median depth per (workload, strategy, shrinks). One panel per workload, one marker per shrinks cohort."""
    by_d = group(rows, ["workload", "strategy", "shrinks"], value_key="depth")
    by_t = group(rows, ["workload", "strategy", "shrinks"], value_key="time")
    workloads = sorted({k[0] for k in by_d})
    shrinks_vals = sorted(
        {k[2] for k in by_d}, key=lambda x: (-1 if x is None else x)
    )
    cmap = plt.cm.tab10
    for w in workloads:
        fig, ax = plt.subplots(figsize=(8, 5.5))
        for i, sv in enumerate(shrinks_vals):
            xs, ys, labels = [], [], []
            for (w_, s_, sv_), ds in by_d.items():
                if w_ != w or sv_ != sv:
                    continue
                ts = by_t.get((w_, s_, sv_)) or []
                if not ds or not ts:
                    continue
                xs.append(statistics.median(ts))
                ys.append(statistics.median(ds))
                labels.append(s_)
            if not xs:
                continue
            label = "legacy" if sv is None else f"shrinks={sv}"
            ax.scatter(xs, ys, s=70, color=cmap(i), label=label, edgecolors="black", linewidths=0.4)
            for x, y, lab in zip(xs, ys, labels):
                ax.annotate(lab, (x, y), textcoords="offset points", xytext=(5, 4), fontsize=8)
        ax.set_xscale("log")
        ax.set_xlabel("median time (s, log scale)")
        ax.set_ylabel("median tree depth")
        ax.set_title(f"{w}: depth vs time, by shrinks config (lower-left is Pareto-best)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(title="ETNA_SHRINKS", loc="best")
        plt.tight_layout()
        plt.savefig(out_dir / f"{w}_pareto.png", dpi=120)
        plt.close(fig)


def pre_vs_post_per_workload(rows, out_dir: Path):
    """Bar chart: per (workload, strategy, shrinks) show pre and post median depth side-by-side."""
    by_post = group(rows, ["workload", "strategy", "shrinks"], value_key="depth")
    by_pre = group(rows, ["workload", "strategy", "shrinks"], value_key="pre_depth")
    workloads = sorted({k[0] for k in by_post})
    shrinks_vals = sorted(
        {k[2] for k in by_post}, key=lambda x: (-1 if x is None else x)
    )
    for w in workloads:
        strategies = sorted({k[1] for k in by_post if k[0] == w})
        if not strategies:
            continue
        n_groups = len(strategies)
        n_cohorts = len(shrinks_vals)
        bar_w = 0.8 / max(2 * n_cohorts, 1)  # 2 bars (pre, post) per cohort
        fig, ax = plt.subplots(figsize=(max(8, 0.7 * n_groups + 2), 5))
        x_centers = np.arange(n_groups)
        cmap = plt.cm.tab10
        for ci, sv in enumerate(shrinks_vals):
            pre_meds = []
            post_meds = []
            for s in strategies:
                pre_vals = by_pre.get((w, s, sv)) or []
                post_vals = by_post.get((w, s, sv)) or []
                pre_meds.append(statistics.median(pre_vals) if pre_vals else np.nan)
                post_meds.append(statistics.median(post_vals) if post_vals else np.nan)
            offset = (ci - (n_cohorts - 1) / 2) * 2 * bar_w
            color = cmap(ci)
            label_sv = "legacy" if sv is None else f"sh={sv}"
            ax.bar(x_centers + offset - bar_w / 2, pre_meds, bar_w, color=color, alpha=0.45,
                   edgecolor=color, label=f"{label_sv} pre")
            ax.bar(x_centers + offset + bar_w / 2, post_meds, bar_w, color=color,
                   edgecolor="black", linewidth=0.5, label=f"{label_sv} post")
        ax.set_xticks(x_centers)
        ax.set_xticklabels(strategies, rotation=30, ha="right")
        ax.set_ylabel("median tree depth")
        ax.set_title(f"{w}: pre vs post-shrink depth, by strategy and shrinks config")
        ax.legend(fontsize=7, ncol=max(1, n_cohorts), loc="upper right")
        ax.grid(True, axis="y", alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{w}_pre_vs_post.png", dpi=120)
        plt.close(fig)


def main():
    FIGURES.mkdir(exist_ok=True)
    audit_status(FIGURES / "abort_audit.md")
    rows, excluded = load_failed_with_counterexample()
    if not rows:
        raise SystemExit("no Failed-status entries with counterexample in store.jsonl")
    write_summary_table(rows, FIGURES / "shrinking_summary.md")
    heatmap_per_workload(rows, FIGURES, "depth", "tree depth", "heatmap_depth", lambda v: f"{v:g}")
    heatmap_per_workload(rows, FIGURES, "time", "time", "heatmap_time", fmt_time)
    box_per_workload(rows, FIGURES, "depth", "tree depth", "box_depth")
    box_per_workload(rows, FIGURES, "time", "time (s)", "box_time", log=True)
    pareto_per_workload(rows, FIGURES)
    pre_vs_post_per_workload(rows, FIGURES)
    print(f"analyzed {len(rows)} counterexamples (excluded {excluded} from {sorted(EXCLUDED_STRATEGIES)})")
    print(f"outputs in {FIGURES}/")


if __name__ == "__main__":
    main()
