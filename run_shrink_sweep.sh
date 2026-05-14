#!/usr/bin/env bash
# Run the shrink-mode experiments sequentially across workloads.
# Stops on first failure.
set -euo pipefail

# Run one experiment.
#   $1 = test name (e.g. bst-haskell-falsify, rbt-haskell-quick)
#   $2 = ETNA_SHRINKS value (none / 100 / default / etc.)
#   $3 = label used in the output store filename (0 / 100 / default / ...)
#Wh
# Store filename: store.<workload-short>.<framework>.shrink-<label>.jsonl
#   e.g. bst-haskell-falsify -> store.bst.falsify.shrink-0.jsonl
#        rbt-haskell-quick   -> store.rbt.quick.shrink-0.jsonl
run() {
  local test=$1 mode=$2 label=$3
  # Strip the "-haskell-" middle: "bst-haskell-quick" -> workload "bst",
  # framework "quick". The "haskell" in the middle is the language, not
  # the workload, so we elide it from the store filename.
  local workload="${test%%-haskell-*}"
  local framework="${test##*-haskell-}"
  local store="store.${workload}.${framework}.shrink-${label}.jsonl"
  echo "=== ETNA_SHRINKS=${mode} test=${test} -> ${store} ==="
  ETNA_SHRINKS="${mode}" etna experiment run \
    --tests "${test}" \
    --store "${store}" \
    --short-circuit
}

# bst-haskell sweeps (continuation of the existing data).
run bst-haskell-quick    none 0
run bst-haskell-hedgehog none 0
run bst-haskell-falsify  none 0
run bst-haskell-quick    default default
run bst-haskell-hedgehog default default
run bst-haskell-falsify  default default
run bst-haskell-quick    100  100
run bst-haskell-hedgehog 100  100
run bst-haskell-falsify  100  100

# rbt-haskell sweeps — same layout for the new workload.
run rbt-haskell-quick    none    0
run rbt-haskell-hedgehog none    0
run rbt-haskell-falsify  none 0
run rbt-haskell-quick    default default
run rbt-haskell-hedgehog default default
run rbt-haskell-falsify  default default

# stlc-haskell sweeps.
run stlc-haskell-quick    default default
run stlc-haskell-hedgehog default default
run stlc-haskell-falsify  default default
run stlc-haskell-quick    none    0
run stlc-haskell-hedgehog none    0
run stlc-haskell-falsify  none    0

# fsub-haskell sweeps.
run fsub-haskell-quick    default default
run fsub-haskell-hedgehog default default
run fsub-haskell-falsify  default default
run fsub-haskell-quick    none    0
run fsub-haskell-hedgehog none    0
run fsub-haskell-falsify  none    0

echo "=== all runs complete ==="
