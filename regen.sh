#!/usr/bin/env bash
# Regenerate the analysis CSVs, charts, stats/appendix tables, and the
# paper PDF from the existing store.*.jsonl files.
#
# This does NOT re-run experiments. To regenerate the underlying data,
# run ./run_shrink_sweep.sh (frameworks) and the LeanCheck ground-truth
# runs (etna experiment run --tests <wl>-haskell-lean --store store.<wl>.det.jsonl)
# first, then run this.
#
# Usage:
#   ./regen.sh                 # all workloads: bst rbt stlc fsub
#   ./regen.sh bst rbt         # only the named workloads
#   REGEN_SKIP_BUILD=1 ./regen.sh   # skip the final latexmk build
set -euo pipefail

cd "$(dirname "$0")"
PY=.venv/bin/python

WORKLOADS=("$@")
[ ${#WORKLOADS[@]} -eq 0 ] && WORKLOADS=(bst rbt stlc fsub)

if [ "${REGEN_SKIP_ANALYSIS:-0}" = "1" ]; then
  echo "== analysis skipped (REGEN_SKIP_ANALYSIS=1) =="
else
  echo "== Stage 1/4: analysis (stores -> figures/<WL>_ANALYSIS.csv) =="
  for wl in "${WORKLOADS[@]}"; do
    echo "  workload_analysis $wl"
    $PY scripts/workload_analysis.py --workload "$wl"
  done
fi

echo "== Stage 2/4: charts (ECDF + bucket) =="
for wl in "${WORKLOADS[@]}"; do
  echo "  ecdf + buckets $wl"
  $PY scripts/workload_ecdf.py    --workload "$wl"
  $PY scripts/workload_buckets.py --workload "$wl"
done

echo "== Stage 3/4: stats + appendix tables =="
$PY scripts/workload_friedman.py > figures/friedman_report.txt
echo "  wrote figures/friedman_report.txt"
$PY scripts/gen_stats_tables.py          # -> ShrinkingEval/appendix_stats.tex
$PY scripts/gen_groundtruth_tables.py    # -> ShrinkingEval/appendix_groundtruth.tex

echo "== Stage 4/4: copy figures into the paper =="
n=0
for f in $(grep -oE '(bucket|shrink)_(bst|rbt|stlc|fsub)[a-z_-]*\.png' ShrinkingEval/paper.tex | sort -u); do
  if [ -f "figures/$f" ]; then
    cp "figures/$f" "ShrinkingEval/figures/$f"
    n=$((n + 1))
  else
    echo "  WARNING: figures/$f not found"
  fi
done
echo "  copied $n figures into ShrinkingEval/figures/"

if [ "${REGEN_SKIP_BUILD:-0}" = "1" ]; then
  echo "== build skipped (REGEN_SKIP_BUILD=1) =="
else
  echo "== building paper =="
  ( cd ShrinkingEval && latexmk -pdf -interaction=nonstopmode paper.tex >/dev/null )
  echo "  ShrinkingEval/paper.pdf built"
fi

echo "== regen complete =="
