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

| # | line | Claim (anchor phrase) | Expected |
|---|---|---|---|
| C1 | ~550 | "Binary-Search Tree with 53 tasks…" | BST 53, RBT 58, STLC 20, F<: 36 — all ✓ |
| C2 | ~734–737 | "shrinking reduces the tree edit distance … by a median of only 3-8 edits … GbE (33-41) … CBC (18-102)" | type-based 4/3/8/8 (range 3–8); GbE 33.5/40.5; CBC 18/35.5/92/101.5 — all ✓ |
| C15 | ~736 | "we ran a Friedman test across all tasks (BST X²=39.5…)" | χ²=39.5/11.1, p<0.001/0.004; QC–Falsify p=0.18/0.09; Hedgehog worse |
| C16 | ~742 | "idiomatic BST generator in Hedgehog shows a median improvement of 2" | Hedgehog +2 (p<0.001); Falsify 0 (p=0.98) |
| C17 | ~741,748 | "RBT … slight win for QuickCheck … STLC … Falsify … ranking … in F<:" | CBC TED-to-GT: BST/RBT QuickCBC best; STLC Falsify best; F<: Correct<Falsify<Hedgehog |
| C18 | ~745 | "QuickCheck … almost identical across GbE and CBC … vary for Hedgehog and Falsify" | QuickCheck p=0.47/0.12 (n.s.); HH & Falsify differ |
| C19 | ~750 | "RBT tasks only have 34 tasks … remaining 24 … too deep" | 34 with GT, 24 too deep, 58 total ✓ |
| C3 | ~816 | "an order of magnitude slower results for Falsify" | Falsify/Quick 7×/6×/54×/5× (BST/RBT/STLC/F<:) |
| C4 | ~816 | "up to 4 orders of magnitude slower than the others" | peak per-task ratio ≈ 25700× |
| C5 | ~820 | "QuickCheck uses the budget to set the maximum amount of executions…" | QC=all execs, HH=accepted, Falsify=shrink steps |
| C6 | ~823 | "observed no notable overhead" | budget=0 vs default failure rates equal within ~1–2 pp |
| C7 | ~825 | "did not find any notable results in the (budget = 100) case" | fixed-100 ≈ default execs (88/22/638 vs 88/23/658) |
| C8 | ~828 | "CBC generators for BST/RBT show QuickCheck and Hedgehog tied against a slower Falsify" | Friedman p≪0.05, order Quick<Hedgehog<Falsify |
| C9 | ~829 | "for STLC/F<: … QuickCheck < Hedgehog < Falsify" | order Correct<Hedgehog<Falsify, p≪0.05 |
| C10 | ~889 | "per-edit results are largely consistent … for QuickCheck and Hedgehog" | same vanilla order on both metrics (STLC: one swap) |
| C11 | ~890 | "median pre-shrink TED = 150 vs = 15-20 for the others" | Falsify 156/146, others 13–19 |
| C12 | ~893 | "collapses Falsify's gap to QuickCheck from 31x/96x … to 3.7x/2.4x" | exactly 31.1×/95.9× → 3.7×/2.4× |
| C13 | ~990 | "Hedgehog preserves a 30-60% failure rate … 3-10% for QuickCheck and 2% for Falsify" | Hedgehog 28.6–55.8%, QC 3.2–10.3%, Falsify 1.7–2.3% |
| C14 | ~992 | "discarded cases … up to 70% in QuickCheck's structural shrinking" | peak **82.5%** (paper says 70% — see notes) |

### Figures

The three ECDF figures and the bug-finding bucket charts:

```sh
for w in bst rbt stlc fsub; do
  .venv/bin/python scripts/workload_ecdf.py    --workload "$w"  # fig:ecdf_ted_to_gt,
                                                                # fig:ecdf_time_shrinking,
                                                                # fig:ecdf_ms_per_edit
  .venv/bin/python scripts/workload_buckets.py --workload "$w"  # bug-finding bucket charts
done
```

### Supporting analysis tables

Underpin the orderings in C3/C8–C18:

```sh
.venv/bin/python scripts/workload_shrink_effort.py   # figures/SHRINK_EFFORT.md
.venv/bin/python scripts/workload_friedman.py        # figures/STATS_FRIEDMAN.md
```

## Discrepancies found during reproduction

These do **not** match the paper text as written — flag for revision:

- **C3** — "order of magnitude" is loose: Falsify/Quick is ~5–7× on
  BST/RBT/F<: and ~54× only on STLC.
- **C6 (F<: only) — stale store, comparison invalid.** The F<:
  `shrink-default` stores were regenerated 2026-05-18 with the fixed
  small-index generators; the F<: `shrink-0` stores are still 2026-05-15/16
  (old ±1000-index generators). So `reproduce.py C6` compares old-gen
  budget=0 (rate 0.857) against new-gen budget=default (0.964) and shows a
  spurious 11pp "overhead". Regenerate `store.fsub.*.shrink-0.jsonl` with
  `ETNA_SHRINKS=none` before trusting C6 on F<:. BST/RBT/STLC C6 are fine.
- **C13** — with the updated F<: data the ranges spill slightly past the
  paper's brackets: Hedgehog failure rate **28.6–57%** (paper 30–60%),
  QuickCheck **3.2–11%** (paper 3–10%). Falsify ~2% ✓.
- **C14** — peak QuickCheck discard rate reproduces at **82.5%** (RBT GbE),
  not 70%. The paper undersells it.

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
ground-truth stores (`store.*.det.jsonl`, used by C19 and all TED-to-GT
claims) are produced by the `Lean` / `LeanRev` strategies. After
regenerating any store, re-run **Tier 0** before the Tier-1 commands.
