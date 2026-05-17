# Reproduction guide

Every quantitative claim in `ShrinkingEval/paper.tex` and the command that
reproduces it. Claim IDs (`C1`…`C14`) match the handlers in
`scripts/reproduce.py`.

## Prerequisites

- Python deps in the project virtualenv: `.venv/bin/python` (provides
  `scipy`, `zss`, `matplotlib`).
- The raw experiment data: the `store.*.jsonl` files in the repo root
  (already present). To regenerate them from scratch see **Tier 2** below.

## Tier 0 — build the analysis tables (run once)

Every Tier-1 command reads `figures/<WORKLOAD>_ANALYSIS.csv`. Build them
from the stores first:

```sh
for w in bst rbt stlc fsub; do
  .venv/bin/python scripts/workload_analysis.py --workload "$w"
done
```

This annotates every trial with tree-edit-distance to the LeanCheck
ground-truth minimum. Re-run it whenever a `store.*.jsonl` changes.

## Tier 1 — reproduce each claim from the existing data

One command per claim. `all` runs every handler.

```sh
.venv/bin/python scripts/reproduce.py C7      # one claim
.venv/bin/python scripts/reproduce.py all     # all claims
```

| # | paper line | Claim | Command | Expected |
|---|---|---|---|---|
| C1 | 501–502 | Task counts: BST 53, RBT 58, STLC 20, F<: 36 | `reproduce.py C1` | RBT 58, STLC 20, F<: 36 ✓ — **BST reproduces 52, not 53** (see note) |
| C2 | 647 | Median pre/post shrinking edit distance, type-based (unfilled `TODO: X`) | `reproduce.py C2` | per-workload 4 / 3 / 8 / 23; pooled **4** |
| C3 | 728–729 | Type-based: QC≈Hedgehog, Falsify ~order of magnitude slower | `reproduce.py C3` | Falsify/Quick 7×/6×/54×/5× (BST/RBT/STLC/F<:) |
| C4 | 729–731 | Falsify long tail up to 4 orders of magnitude slower | `reproduce.py C4` | peak ratio ≈ 25700× (~4 orders) |
| C5 | 733–734 | Shrink-budget semantics per framework | `reproduce.py C5` | QC=all execs, HH=accepted, Falsify=shrink steps |
| C6 | 737–738 | budget=0 vs default: no notable bug-finding overhead | `reproduce.py C6` | failure rates equal within ~1–2 pp |
| C7 | 738–739 | budget=100 did not standardize effort | `reproduce.py C7` | fixed-100 ≈ default execs (88/22/638 vs 88/23/658) |
| C8 | 741–742 | CBC BST/RBT shrink time: QC & HH tied, Falsify slower | `reproduce.py C8` | Friedman p≪0.05, order Quick<Hedgehog<Falsify |
| C9 | 742 | CBC STLC/F<: shrink time: QuickCheck < Hedgehog < Falsify | `reproduce.py C9` | order Correct<Hedgehog<Falsify, p≪0.05 |
| C10 | 802 | ms-per-edit consistent with absolute time for QC & HH | `reproduce.py C10` | same vanilla order on both metrics (STLC: one swap) |
| C11 | 804 | Falsify GbE pre-shrink TED ≈150 vs 15–20 | `reproduce.py C11` | Falsify 156/146, others 13–19 |
| C12 | 806 | Per-edit collapses Falsify/Quick gap 31×/96× → 3.7×/2.4× | `reproduce.py C12` | exactly 31.1×/95.9× → 3.7×/2.4× |
| C13 | 895–897 | CBC failure rate: Hedgehog 30–60%, QC 3–10%, Falsify 2% | `reproduce.py C13` | Hedgehog 28.6–55.8%, QC 3.2–10.3%, Falsify 1.7–2.3% |
| C14 | 898–899 | QuickCheck structural shrinking discards up to 70% | `reproduce.py C14` | peak **82.5%** (paper says 70% — see note) |

### Figures

The three ECDF figures and the bug-finding bucket charts:

```sh
for w in bst rbt stlc fsub; do
  .venv/bin/python scripts/workload_ecdf.py   --workload "$w"   # fig:ecdf_ted_to_gt,
                                                                # fig:ecdf_time_shrinking,
                                                                # fig:ecdf_ms_per_edit
  .venv/bin/python scripts/bucket_charts.py   --workload "$w"   # bug-finding bucket charts
done
```

### Supporting analysis tables

Not tied to a single sentence, but underpin the orderings in C3/C8–C14:

```sh
.venv/bin/python scripts/workload_shrink_effort.py   # figures/SHRINK_EFFORT.md
.venv/bin/python scripts/workload_friedman.py        # figures/STATS_FRIEDMAN.md
```

## Discrepancies found during reproduction

These do **not** match the paper text as written — flag for revision:

- **C1** — BST reproduces **52** distinct (property, mutation) tasks, the
  paper says 53. Confirm the intended count against the ETNA workload
  definition.
- **C2** — line 647 still contains the literal `[TODO: X]`. The value is
  **4** (pooled median); note the per-workload spread (4/3/8/23) and that
  F<: is an outlier.
- **C3** — "order of magnitude" is loose: Falsify/Quick is ~5–7× on
  BST/RBT/F<: and ~54× only on STLC.
- **C14** — peak QuickCheck discard rate reproduces at **82.5%** (RBT GbE),
  not 70%. The paper undersells it.

## Tier 2 — regenerate the stores from scratch (hours)

The `store.*.jsonl` files are produced by ETNA experiment runs. Each is
named `store.<workload>.<framework>.shrink-<label>.jsonl`. The sweep
script drives all of them:

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
ground-truth stores (`store.*.det.jsonl`, LeanCheck) are regenerated with
the `Lean` / `LeanRev` strategies. After regenerating any store, re-run
**Tier 0** before the Tier-1 commands.
