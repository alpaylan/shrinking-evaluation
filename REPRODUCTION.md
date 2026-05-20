# Reproduction guide

Every quantitative claim in `ShrinkingEval/paper.tex` and the command that
reproduces it. Claim IDs (`C1`…`C19`) match the handlers in
`scripts/reproduce.py`.

Line numbers are approximate (the draft moves); the **quoted phrase** is the
stable anchor — search for it in `paper.tex`.

## Prerequisites

- Python deps in the project virtualenv: `.venv/bin/python` (provides
  `scipy`, `zss`, `matplotlib`).
- The raw experiment data: the `store.*.jsonl` files in the repo root
  (already present). To regenerate them see **Tier 2** below.

## Tier 0 — build the analysis tables (run once)

Every Tier-1 command reads `figures/<WORKLOAD>_ANALYSIS.csv`. Build them
from the stores first:

```sh
for w in bst rbt stlc fsub; do
  .venv/bin/python scripts/workload_analysis.py --workload "$w"
done
```

This annotates every trial with tree-edit distance to the LeanCheck
ground-truth minimum. Re-run it whenever a `store.*.jsonl` changes.

## Tier 1 — reproduce each claim from the existing data

One command per claim. `all` runs every handler.

```sh
.venv/bin/python scripts/reproduce.py C15     # one claim
.venv/bin/python scripts/reproduce.py all     # all claims
```

### Methodology / dataset

| # | §, ~line | Anchor phrase | Expected |
|---|---|---|---|
| C1 | §4.1, ~586 | "Binary-Search Tree with 53 tasks, Red-Black Tree with 58 tasks, Simply-Typed Lambda Calculus with 20 tasks, and System $F_{<:}$ with 36 tasks" | BST 53, RBT 58, STLC 20, F<: 36 |
| C9 | §4.2.2 footnote, ~909 | "LeanCheck found ground-truth minima for only 34 tasks in reasonable time. We exclude the remaining 24 tasks" | 34 / 24 / 58 |

### §4.2.1 — Bug-finding (Friedman + Holm-Wilcoxon on `time_pre_failure`)

| # | ~line | Anchor phrase | Expected |
|---|---|---|---|
| C3 | 702–713 | "the type-based and generation-by-execution comparisons are statistically significant ($p < 0.001$) ... the correct-by-construction generators are statistically indistinguishable" | BST: vanilla & GbE p<0.001; CBC Friedman p≈0.40 (n.s.) |
| C4 | 752–757 | "type-based, generation-by-execution, and correct-by-construction comparisons are all significant ... Hedgehog and Falsify comparison for generation-by-execution is not significant after Holm correction" | RBT: all 3 families p<0.001; HH vs Falsify GbE p_Holm≈0.06 (n.s.) |
| C5 | 780–787 | "type-based generation, the Friedman test does not find a significant difference in bug-finding time ... For correct-by-construction generation, the difference is significant ($p < 0.001$)" | STLC: vanilla p≈0.44 (n.s.); CBC p<0.001; HH vs Falsify CBC p_Holm≈0.11 (n.s.) |
| C6 | 817–821 | "In the type-based comparison, the Friedman test rejects ($p < 0.001$) ... In the correct-by-construction comparison, QuickCheck is significantly faster" | F<:: both families significant; QC < Falsify < HH everywhere |

### §4.2.2 — Shrinking effectiveness (TED-to-GT)

| # | ~line | Anchor phrase | Expected |
|---|---|---|---|
| C2 | 894–897 | "shrinking reduces the tree edit distance to the ground-truth minimum by a median of only 3-10 edits per workload (BST 4, RBT 3, STLC 7, $F_{<:}$ 10), substantially below the generation-by-execution (41-44) and correct-by-construction (18-106)" | type-based 3.0–8.5; GbE 41.0–41.8; CBC 17.8–98.2 (see Notes) |
| C7 | 900–906 | "QuickCheck's structural shrinker reports counterexamples closer to the LeanCheck minimum ... On STLC, Falsify reports smaller counterexamples ... On $F_{<:}$, QuickCheck reports the closest counterexamples, followed by Falsify and then Hedgehog" | BST/RBT QC closest; STLC FalsifyCBC closest; F<: Q < Falsify < HH |
| C8 | 902 | "the RBT generation-by-execution comparison is statistically indistinguishable" | RBT GbE Friedman χ²=1.8, p=0.415 (n.s.) |

### §4.2.3 — Shrinking time / per-edit cost

| # | ~line | Anchor phrase | Expected |
|---|---|---|---|
| C10 | 978–981 | "QuickCheck and Hedgehog have similar shrinking times across the four workloads, while Falsify is consistently slower and has a longer tail" | Falsify/Quick medians 10.8×–148.0× across the four workloads |
| C11 | 980 | "Falsify's shrinking time is several orders of magnitude larger than the others" | peak per-task Falsify/min(QC,HH) ratio ≈ 37 554× (≈4 orders of magnitude) |
| C12 | 984 | "QuickCheck's budget bounds total executions, whereas Hedgehog and Falsify bound failing executions" | source-level claim; verify in `workloads/*/etna-lib/src/Etna/Lib/Strategy/{QuickCheck,Hedgehog,Falsify}.hs` |
| C13 | 987–989 | "no-shrinking runs let us check the bug-finding overhead of enabling shrinking" | budget=0 vs default failure rates equal within ~1–2 pp on BST/RBT/STLC; F<: differs (no notable shrink overhead where comparable) |
| C14 | 989–992 | "fixed-budget runs were intended to standardize effort ... did not achieve comparable effort across libraries" | BST default execs ≈ 84 (QC) / 20 (HH) / 622 (Falsify) — vary by ~30× at the same nominal budget |
| C15 | 994–997 | "RBT puts QuickCheck and Hedgehog close to each other against a slower Falsify. On BST, QuickCheck is significantly faster ... On STLC and $F_{<:}$, the ordering is clearer: QuickCheck is fastest, Hedgehog is next, and Falsify is slowest" | BST: QC<HH<Falsify all significant; RBT: Q vs HH p_Holm=0.52 (n.s.), both < Falsify; STLC/F<: QC<HH<Falsify all significant |
| C16 | 1001 | "The per-edit results are largely consistent with the absolute comparison for QuickCheck and Hedgehog" | same Q<HH<Falsify order under both metrics on all four workloads |
| C17 | 1003 | "median pre-shrink TED = 150 vs = 15-20 for the others" | Falsify GbE 154 (BST) / 146 (RBT); Quick/Hedgehog GbE 13–18 |
| C18 | 1004–1005 | "collapses Falsify's gap to QuickCheck from 49x/96x (BST/RBT) to 6.2x/2.4x" | absolute time 49.1× / 94.6×; ms-per-edit 6.2× / 2.4× |

### §4.3 — Sample-efficiency

| # | ~line | Anchor phrase | Expected |
|---|---|---|---|
| C19 | 1109–1112 | "Hedgehog preserves a 26-56% failure rate across shrinking steps, compared to 5-12% for QuickCheck and roughly 2-3% for Falsify" | HH 25.9–56.5%; QC 4.7–12.5%; Falsify 2.5–3.0% |

### Figures

The ECDF figures and the bug-finding bucket charts:

```sh
for w in bst rbt stlc fsub; do
  .venv/bin/python scripts/workload_ecdf.py    --workload "$w"  # fig:ecdf_ted_to_gt,
                                                                # fig:ecdf_time_shrinking,
                                                                # fig:ecdf_ms_per_edit
  .venv/bin/python scripts/workload_buckets.py --workload "$w"  # bug-finding bucket charts
done
```

### Supporting analysis tables

The full per-(workload, family, metric) Friedman + post-hoc tables that
underpin C3–C8 and C15 are in `ShrinkingEval/appendix_stats.tex`. To
regenerate them from the stores:

```sh
.venv/bin/python scripts/workload_shrink_effort.py   # figures/SHRINK_EFFORT.md
.venv/bin/python scripts/workload_friedman.py        # figures/STATS_FRIEDMAN.md
```

## Notes

- **C2 aggregation.** The handler computes the median of per-(task,
  library) trial medians — the closest match we found to the paper's "3-10
  per workload" figure. Numbers come out within 1–2 edits of the paper for
  vanilla and GbE; the CBC max is 98 vs the paper's 106, likely from a
  data refresh after the paper paragraph was written.
- **Friedman omnibus vs pairwise.** A few claims (C3 BST CBC, C4 RBT
  vanilla post-hoc) show a non-significant Friedman *and* significant
  pairwise Holm-Wilcoxon, or vice-versa, depending on how the median Δ
  distributes. The paper consistently leans on the Friedman omnibus for
  the "indistinguishable" verdict; the handlers print both.

  The clearest case is **BST CBC bug-finding time** (now in
  `appendix_stats.tex` Table~\ref{tab:stats-bst}): Friedman χ²=1.8,
  p=0.40 (n.s.), but pairwise Holm-Wilcoxon shows QuickCBC vs FalsifyCBC
  and HedgehogCBC vs FalsifyCBC both p_Holm<0.001 while QuickCBC vs
  HedgehogCBC is p_Holm=0.79. This is a known low-power failure mode of
  Friedman with k=3 algorithms: when two of the three are tied at the
  top rank (≈1.5) and one trails (≈3), the rank-spread vector
  (1.5, 1.5, 3) has less between-group variance than (1, 2, 3) and
  Friedman's χ² collapses, even though a real two-vs-one effect is
  present.

  We follow the conservative Demšar (2006) / García & Herrera (2008)
  closed-testing convention: when the omnibus does not reject, we report
  "statistically indistinguishable" in the body and do not draw
  conclusions from the pairwise post-hoc. The pairwise rows remain in
  the appendix for transparency. Readers preferring the post-hoc-first
  approach (Benavoli et al. 2017; García et al. 2010, *Information
  Sciences*) can re-interpret directly from the appendix: those tables
  contain everything needed under either convention.

## Tier 2 — regenerate the stores from scratch (hours)

The `store.*.jsonl` files are produced by ETNA experiment runs, named
`store.<workload>.<framework>.shrink-<label>.jsonl`. The sweep script
drives all of them:

```sh
./run_shrink_sweep.sh        # all workloads × frameworks × shrink modes
```

A single store is regenerated with:

```sh
ETNA_SHRINKS=<mode> etna experiment run \
  --tests <workload>-haskell-<framework> \
  --store store.<workload>.<framework>.shrink-<label>.jsonl \
  --short-circuit
```

where `<mode>` is `none` (budget=0), `100` (budget=100), or `default`,
and `<label>` is `0` / `100` / `default` respectively. The deterministic
ground-truth stores (`store.*.det.jsonl`, used by C9 and all TED-to-GT
claims) are produced by the `Lean` / `LeanRev` strategies. After
regenerating any store, re-run **Tier 0** before the Tier-1 commands.
