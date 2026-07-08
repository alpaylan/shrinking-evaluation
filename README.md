# Evaluating Shrinking — artifact

This repository is the artifact for the experience report *Evaluating
Shrinking*, which compares the shrinking phase of three Haskell
property-based testing frameworks — QuickCheck, Hedgehog, and Falsify —
across four ETNA workloads (BST, RBT, STLC, F<:) and several generator
families (type-based, API-based, correct-by-construction).

> **Getting started:** download and extract the archive, then read this
> `README.md` and follow `REPRODUCTION.md`, which lists every quantitative
> claim in the paper and the exact command that reproduces it.

## What is here

| Path                  | Contents                                                                 |
| --------------------- | ------------------------------------------------------------------------ |
| `REPRODUCTION.md`     | **Start here.** Every quantitative claim in the paper and the exact command that reproduces it. |
| `ShrinkingEval/`      | The LaTeX source of the paper (`paper.tex`, build with `make`).           |
| `scripts/`            | Python analysis scripts (statistics, figures, per-claim reproduction).    |
| `store.*.jsonl`       | Raw experiment data (ETNA runs). Consumed by the scripts.                 |
| `figures/`            | Generated figures and the per-workload `*_ANALYSIS.csv` tables.           |
| `workloads/`          | The four Haskell workloads (generators, properties, strategies).          |
| `run_shrink_sweep.sh` | Regenerates the raw data from scratch (Tier 2; needs ETNA + Haskell).     |

## Quick start

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Build the per-workload analysis tables (once), then reproduce every claim:
for w in bst rbt stlc fsub; do .venv/bin/python scripts/workload_analysis.py --workload "$w"; done
.venv/bin/python scripts/reproduce.py all
```

See `REPRODUCTION.md` for the full, claim-by-claim guide (including how to
regenerate the raw data and the figures).

## Requirements

- **Reproducing the paper's numbers and figures from the shipped data**
  (`REPRODUCTION.md` Tier 0–1): Python 3.9+ and the packages in
  `requirements.txt` (`scipy`, `matplotlib`, `zss`).
- **Regenerating the raw data from scratch** (Tier 2): additionally the
  [`etna` CLI](https://github.com/alpaylan/etna-cli) and a Haskell toolchain
  (GHC + `stack`, e.g. via [ghcup](https://www.haskell.org/ghcup/)). See the
  "Setup" step in `REPRODUCTION.md`.

## Citing

If you use this artifact, please cite the paper and this artifact record
(Zenodo DOI [10.5281/zenodo.21266467](https://doi.org/10.5281/zenodo.21266467)).
