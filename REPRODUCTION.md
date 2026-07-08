# Reproduction guide

Every quantitative claim in `ShrinkingEval/paper.tex` and the command that
reproduces it. Claim IDs (`C1`…`C19`) match the handlers in
`scripts/reproduce.py`.

Line numbers are approximate (the draft moves); the **quoted phrase** is the
stable anchor — search for it in `paper.tex`.

## Prerequisites

- Python 3.9+ and the three third-party packages the scripts use
  (`scipy`, `matplotlib`, `zss`). Create the virtualenv the commands below
  expect:

  ```sh
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
  ```

- The raw experiment data: the `store.*.jsonl` files in the repo root
  (already present). To regenerate them see **Tier 2** below (that tier
  additionally needs the ETNA harness and a Haskell toolchain).

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

> **Naming.** The paper's **API-based** generator family is the `*GbE`
> strategies in the data (`QuickGbE`, `HedgehogGbE`, `FalsifyGbE`); handlers
> print them either as `*GbE` or via the display name `*API` (`QuickAPI`, …).
> The paper's **type-based** family is `vanilla` in the code.

### Methodology / dataset

| #   | §, ~line              | Anchor phrase                                                                                                                                   | Expected                        |
| --- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| C1  | §3.1, ~769            | "Binary-Search Tree with 53 tasks, Red-Black Tree with 58 tasks, Simply-Typed Lambda Calculus with 20 tasks, and System $F_{<:}$ with 36 tasks" | BST 53, RBT 58, STLC 20, F<: 36 |
| C9  | §3.2.2 footnote, ~1104 | "LeanCheck found ground-truth minima for only 34 tasks in reasonable time. We exclude the remaining 24 tasks"                                   | 34 / 24 / 58                    |

### §3.2.1 — Bug-finding (Friedman + Holm-Wilcoxon on `time_pre_failure`)

| #   | ~line   | Anchor phrase                                                                                                                                                                                       | Expected                                                                          |
| --- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| C3  | ~900    | "For BST bug-finding time ... API-based comparisons are statistically significant ($p < 0.001$) ... the correct-by-construction generators are statistically indistinguishable"                   | BST: type-based & API-based p<0.001; CBC Friedman p≈0.40 (n.s.)                    |
| C4  | ~944    | "The type-based, API-based, and correct-by-construction comparisons are all significant ... the Hedgehog and Falsify comparison for API-based is not significant after Holm correction"            | RBT: all 3 families p<0.001; HH vs Falsify API-based p_Holm≈0.06 (n.s.)            |
| C5  | ~976    | "type-based generation, the Friedman test does not find a significant difference in bug-finding time ... For correct-by-construction generation, the difference is significant ($p < 0.001$)"     | STLC: type-based p≈0.44 (n.s.); CBC p<0.001; HH vs Falsify CBC p_Holm≈0.11 (n.s.)  |
| C6  | ~1013   | "the Friedman test rejects the null hypothesis of equal medians ($p < 0.001$) ... In the correct-by-construction comparison, QuickCheck is faster than both"                                        | F<:: both families significant; QC < Falsify < HH everywhere                       |

### §3.2.2 — Shrinking effectiveness (TED-to-GT)

| #   | ~line   | Anchor phrase                                                                                                                                                                                                                                          | Expected                                                            |
| --- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| C2  | ~1090   | "shrinking reduces the tree edit distance to the ground-truth minimum by a median of only $3$--$9$ edits per workload (BST $4$, RBT $3$, STLC $7$, $F_{<:}$ $9$), substantially below the API-based ($41$--$42$) and correct-by-construction ($18$--$98$)" | type-based 3.0–8.5; API-based 41.0–41.8; CBC 17.8–98.2 (see Notes)  |
| C7  | ~1096   | "QuickCheck's structural shrinker reports counterexamples closer to the LeanCheck minimum than the integrated shrinkers ... On STLC, Falsify reports smaller counterexamples ... On $F_{<:}$, QuickCheck reports the closest counterexamples, followed by Falsify and then Hedgehog" | BST/RBT QC closest; STLC FalsifyCBC closest; F<: Q < Falsify < HH   |
| C8  | ~1097   | "the RBT API-based comparison is statistically indistinguishable"                                                                                                                                                                                      | RBT API-based Friedman χ²=1.8, p=0.415 (n.s.)                       |

### §3.2.2 (cont.) — Shrinking time / per-edit cost

| #   | ~line     | Anchor phrase                                                                                                                                                                                                                                  | Expected                                                                                                                          |
| --- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| C10 | ~1172     | "QuickCheck and Hedgehog have similar shrinking times across the four workloads, while Falsify is consistently slower and has a longer tail"                                                                                                   | Falsify/Quick medians 10.8×–148.0× across the four workloads                                                                      |
| C11 | ~1173     | "Falsify's shrinking time is several orders of magnitude larger than the others"                                                                                                                                                               | peak per-task Falsify/min(QC,HH) ratio ≈ 37 554× (≈4 orders of magnitude)                                                         |
| C12 | ~1177     | "QuickCheck's budget bounds total executions, whereas Hedgehog and Falsify bound failing executions"                                                                                                                                           | source-level claim; verify in `workloads/*/etna-lib/src/Etna/Lib/Strategy/{QuickCheck,Hedgehog,Falsify}.hs`                       |
| C13 | ~1182     | "no-shrinking runs let us check the bug-finding overhead of enabling shrinking"                                                                                                                                                                | budget=0 vs default failure rates equal within ~1–2 pp on BST/RBT/STLC; F<: differs (no notable shrink overhead where comparable) |
| C14 | ~1181     | "fixed-budget runs were intended to standardize effort ... did not achieve comparable effort across libraries"                                                                                                                                 | BST default execs ≈ 84 (QC) / 20 (HH) / 622 (Falsify) — vary by ~30× at the same nominal budget                                   |
| C15 | ~1188     | "RBT puts QuickCheck and Hedgehog close to each other against a slower Falsify. On BST, QuickCheck is significantly faster ... On STLC and $F_{<:}$, the ordering is clearer: QuickCheck is fastest, Hedgehog is next, and Falsify is slowest" | BST: QC<HH<Falsify all significant; RBT: Q vs HH p_Holm=0.52 (n.s.), both < Falsify; STLC/F<: QC<HH<Falsify all significant       |
| C16 | ~1251     | "The per-edit results are largely consistent with the absolute comparison for QuickCheck and Hedgehog"                                                                                                                                         | same Q<HH<Falsify order under both metrics on all four workloads                                                                  |
| C17 | ~1253     | "median pre-shrink TED = 150 vs = 13-18 for the others"                                                                                                                                                                                        | Falsify API-based 154 (BST) / 146 (RBT); Quick/Hedgehog API-based 13–18                                                           |
| C18 | ~1255     | "collapses Falsify's gap to QuickCheck from 49x/95x (BST/RBT) to 6.2x/2.4x"                                                                                                                                                                    | absolute time 49.1× / 94.6×; ms-per-edit 6.2× / 2.4×                                                                              |

### §3.3 — Sample-efficiency (Discussion)

| #   | ~line     | Anchor phrase                                                                                                                    | Expected                                      |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| C19 | ~1308     | "Hedgehog preserves a 26-56% failure rate across shrinking steps, compared to 5-12% for QuickCheck and roughly 2-3% for Falsify" | HH 25.9–56.5%; QC 4.7–12.5%; Falsify 2.5–3.0% |

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

### Setup (one-time)

Tier 2 rebuilds the raw data by compiling and running the Haskell workloads
through the ETNA harness, so it needs two extra things beyond Tier 0–1:

1. **A Haskell toolchain (GHC + `stack`).** The workloads build with `stack`,
   which resolves the exact GHC version from each `workloads/*/stack.yaml`.
   The easiest way to get both is [ghcup](https://www.haskell.org/ghcup/):

   ```sh
   curl --proto '=https' --tlsv1.2 -sSf https://get-ghcup.haskell.org | sh
   ```

2. **The `etna` CLI**, installed with its one-line installer
   ([alpaylan/etna-cli](https://github.com/alpaylan/etna-cli)):

   ```sh
   curl --proto '=https' --tlsv1.2 -LsSf \
     https://github.com/alpaylan/etna-cli/releases/latest/download/etna-installer.sh | sh
   ```

This archive ships as a **git repository** (ETNA records each run against
git, so the experiment directory must be one — this is already set up for
you). From the repository root (the directory containing `etna.toml`), the
only remaining step is to register it in ETNA's experiment-tracking
metadata:

```sh
etna experiment register
```

(Without this, `etna experiment run` fails with "current dir is not an
experiment directory". If you obtained the sources some other way and they
are *not* a git repository, first run `git init && git add -A && git commit
-m snapshot`.)

Run the commands below from that same directory. The **first** run of any
workload compiles it and all of its dependencies (QuickCheck, Hedgehog,
Falsify, LeanCheck) with `stack`, which can take several minutes; subsequent
runs reuse the build.

### Running the experiments

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
