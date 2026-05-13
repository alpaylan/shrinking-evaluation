# BST analysis — paper draft

All stats restricted to `status == "Failed"` rows on BST.
Ground-truth counterexamples come from `store.det.jsonl` (Lean strategy, exhaustive).
TED is Zhang-Shasha tree edit distance using `zss.simple_distance`
over a parens-structured representation of the counterexample.

Ground-truth coverage: **52** (property, mutation) pairs from Lean.

## 1. Coverage

Rows per (strategy, mode), `Failed` only. Expected = 52 combos × 10 trials = 520.

| Strategy | none | fixed-100 | default |
|---|---:|---:|---:|
| Quick | 472 | 480 | 467 |
| Hedgehog | 488 | 485 | 483 |
| Falsify | 460 | 464 | 459 |
| QuickCBC | 520 | 520 | 520 |
| HedgehogCBC | 520 | 520 | 520 |
| FalsifyCBC | 511 | 520 | 520 |
| HedgehogCBC2 | 520 | 520 | 520 |
| FalsifyCBC2 | 519 | 520 | 520 |
| QuickGbE | 520 | 520 | 520 |
| HedgehogGbE | 520 | 520 | 520 |
| FalsifyGbE | 520 | 520 | 520 |

## 2. Effectiveness — TED to ground-truth minimum

Lower is better. Distribution of TED(final-cex, lean-ground-truth) across Failed trials.
Format: **mean / median / p90 / max**.

| Strategy | none | fixed-100 | default |
|---|---|---|---|
| Quick | 13.1 / 6.0 / 18.0 / 151.0 | 4.7 / 3.0 / 11.0 / 95.0 | 2.8 / 2.0 / 8.0 / 20.0 |
| Hedgehog | 13.1 / 6.0 / 22.0 / 155.0 | 3.8 / 3.0 / 10.0 / 25.0 | 4.0 / 3.0 / 10.0 / 25.0 |
| Falsify | 12.1 / 6.0 / 17.0 / 167.0 | 2.9 / 2.0 / 9.0 / 25.0 | 3.0 / 2.0 / 9.0 / 25.0 |
| QuickCBC | 128.6 / 124.0 / 221.0 / 354.0 | 21.2 / 3.0 / 84.0 / 269.0 | 3.4 / 3.0 / 9.0 / 20.0 |
| HedgehogCBC | 82.2 / 75.0 / 147.0 / 305.0 | 9.5 / 7.0 / 24.0 / 55.0 | 10.0 / 7.0 / 25.0 / 61.0 |
| FalsifyCBC | 127.0 / 119.0 / 222.0 / 390.0 | 10.9 / 4.0 / 25.0 / 165.0 | 10.2 / 4.0 / 25.0 / 50.0 |
| HedgehogCBC2 | 29.8 / 22.0 / 64.0 / 189.0 | 6.3 / 3.0 / 17.0 / 62.0 | 7.3 / 3.0 / 19.0 / 59.0 |
| FalsifyCBC2 | 126.2 / 118.0 / 217.0 / 378.0 | 11.2 / 4.0 / 25.0 / 207.0 | 10.3 / 4.0 / 25.0 / 56.0 |
| QuickGbE | 48.2 / 18.0 / 135.0 / 564.0 | 13.5 / 3.0 / 12.0 / 414.0 | 3.3 / 3.0 / 9.0 / 20.0 |
| HedgehogGbE | 48.4 / 18.0 / 139.0 / 307.0 | 5.6 / 6.0 / 11.0 / 23.0 | 5.6 / 6.0 / 11.0 / 22.0 |
| FalsifyGbE | 169.1 / 164.0 / 293.0 / 377.0 | 3.3 / 2.0 / 9.0 / 94.0 | 3.0 / 2.0 / 8.0 / 20.0 |

### 2a. Fraction of trials reaching the ground-truth minimum (TED = 0)

| Strategy | none | fixed-100 | default |
|---|---:|---:|---:|
| Quick | 0.0% | 34.6% | 39.4% |
| Hedgehog | 2.0% | 23.3% | 21.9% |
| Falsify | 0.0% | 42.2% | 40.5% |
| QuickCBC | 0.0% | 29.4% | 37.5% |
| HedgehogCBC | 0.0% | 21.5% | 19.8% |
| FalsifyCBC | 0.0% | 9.4% | 9.6% |
| HedgehogCBC2 | 0.0% | 23.8% | 21.2% |
| FalsifyCBC2 | 0.0% | 9.6% | 9.8% |
| QuickGbE | 0.4% | 35.6% | 36.9% |
| HedgehogGbE | 0.0% | 3.3% | 4.0% |
| FalsifyGbE | 0.0% | 41.0% | 40.4% |

## 3. Performance — time spent shrinking per unit of TED progress

`time_shrinking / max(1, TED(pre) - TED(post))`, in milliseconds per edit.
Trials where shrinking didn't reduce TED are excluded.
Format: **mean / median / p90 / max** ms/edit.

| Strategy | fixed-100 | default |
|---|---|---|
| Quick | 0.16 / 0.08 / 0.40 / 8.57 | 0.17 / 0.09 / 0.40 / 1.43 |
| Hedgehog | 0.24 / 0.14 / 0.56 / 2.38 | 0.28 / 0.15 / 0.62 / 2.59 |
| Falsify | 60.52 / 0.73 / 6.97 / 10444.82 | 49.15 / 0.81 / 6.36 / 4115.57 |
| QuickCBC | 0.01 / 0.00 / 0.02 / 1.10 | 0.02 / 0.01 / 0.03 / 0.47 |
| HedgehogCBC | 0.03 / 0.01 / 0.05 / 0.82 | 0.03 / 0.02 / 0.06 / 2.07 |
| FalsifyCBC | 1.26 / 0.09 / 1.33 / 205.75 | 1.43 / 0.11 / 1.45 / 381.62 |
| HedgehogCBC2 | 0.10 / 0.05 / 0.23 / 1.70 | 0.09 / 0.05 / 0.21 / 0.91 |
| FalsifyCBC2 | 13.91 / 0.11 / 1.20 / 5498.08 | 3.44 / 0.12 / 1.49 / 583.15 |
| QuickGbE | 0.04 / 0.02 / 0.12 / 1.22 | 0.05 / 0.02 / 0.14 / 0.73 |
| HedgehogGbE | 0.11 / 0.05 / 0.24 / 1.36 | 0.13 / 0.06 / 0.26 / 6.55 |
| FalsifyGbE | 0.49 / 0.07 / 0.64 / 108.26 | 0.89 / 0.09 / 0.76 / 214.48 |

## 4. Cost of enabling shrinking — search-phase overhead

`time_pre_failure` (s) by mode. Pre-failure search shouldn't depend on shrinking budget — the
`none` vs `default` gap measures the structural overhead of running with shrinking enabled.
Per-group ratios (default / none) summarise the relative cost.

| Strategy | none mean | 100 mean | default mean | default/none ratio (median per-task) |
|---|---:|---:|---:|---:|
| Quick | 4.9447 | 9.0317 | 7.0637 | 1.04x |
| Hedgehog | 12.4342 | 9.7925 | 9.4729 | 1.14x |
| Falsify | 6.4526 | 8.4299 | 7.6684 | 1.02x |
| QuickCBC | 0.3164 | 0.2367 | 0.2098 | 1.07x |
| HedgehogCBC | 0.0419 | 0.0277 | 0.0539 | 1.03x |
| FalsifyCBC | 0.6681 | 1.9954 | 2.0100 | 1.01x |
| HedgehogCBC2 | 0.2933 | 0.3206 | 0.2647 | 1.01x |
| FalsifyCBC2 | 2.3456 | 2.1154 | 2.9417 | 0.96x |
| QuickGbE | 0.0006 | 0.0008 | 0.0008 | 1.09x |
| HedgehogGbE | 0.6030 | 0.6619 | 0.5563 | 0.96x |
| FalsifyGbE | 0.8582 | 1.2212 | 1.8416 | 1.04x |

## 5. Stability across generators (default mode)

Per generator family: how do the three frameworks compare on
**TED to ground truth** and **time_pre_failure**?

### vanilla

| Framework | TED (mean / med / max) | time_pre (s, mean) | n |
|---|---|---:|---:|
| Quick | 2.8 / 2.0 / 8.0 / 20.0 | 7.0637 | 467 |
| Hedgehog | 4.0 / 3.0 / 10.0 / 25.0 | 9.4729 | 483 |
| Falsify | 3.0 / 2.0 / 9.0 / 25.0 | 7.6684 | 459 |

### CBC

| Framework | TED (mean / med / max) | time_pre (s, mean) | n |
|---|---|---:|---:|
| QuickCBC | 3.4 / 3.0 / 9.0 / 20.0 | 0.2098 | 520 |
| HedgehogCBC | 10.0 / 7.0 / 25.0 / 61.0 | 0.0539 | 520 |
| FalsifyCBC | 10.2 / 4.0 / 25.0 / 50.0 | 2.0100 | 520 |

### CBC2

| Framework | TED (mean / med / max) | time_pre (s, mean) | n |
|---|---|---:|---:|
| HedgehogCBC2 | 7.3 / 3.0 / 19.0 / 59.0 | 0.2647 | 520 |
| FalsifyCBC2 | 10.3 / 4.0 / 25.0 / 56.0 | 2.9417 | 520 |

### GbE

| Framework | TED (mean / med / max) | time_pre (s, mean) | n |
|---|---|---:|---:|
| QuickGbE | 3.3 / 3.0 / 9.0 / 20.0 | 0.0008 | 520 |
| HedgehogGbE | 5.6 / 6.0 / 11.0 / 22.0 | 0.5563 | 520 |
| FalsifyGbE | 3.0 / 2.0 / 8.0 / 20.0 | 1.8416 | 520 |

## 6. Time decomposition (default mode)

Per the paper: 
- **execution** = `exec_time_pre` (predicate force time before failure)
- **generation** = `time_pre_failure - exec_time_pre` (gen + harness)
- **shrinking** = `time_shrinking`

Mean seconds across Failed trials.

| Strategy | execution | generation | shrinking | total |
|---|---:|---:|---:|---:|
| Quick | 3779.43 ms | 3284.25 ms | 0.69 ms | 7064.37 ms |
| Hedgehog | 11.81 ms | 9461.14 ms | 0.79 ms | 9473.73 ms |
| Falsify | 581.77 ms | 7086.65 ms | 127.99 ms | 7796.41 ms |
| QuickCBC | 171.01 ms | 38.79 ms | 1.22 ms | 211.03 ms |
| HedgehogCBC | 1.23 ms | 52.64 ms | 1.25 ms | 55.12 ms |
| FalsifyCBC | 1947.45 ms | 62.53 ms | 76.09 ms | 2086.08 ms |
| HedgehogCBC2 | 4.73 ms | 260.01 ms | 0.95 ms | 265.69 ms |
| FalsifyCBC2 | 2868.31 ms | 73.43 ms | 142.68 ms | 3084.42 ms |
| QuickGbE | 0.45 ms | 0.32 ms | 0.51 ms | 1.28 ms |
| HedgehogGbE | 37.15 ms | 519.16 ms | 1.50 ms | 557.82 ms |
| FalsifyGbE | 1812.86 ms | 28.69 ms | 54.31 ms | 1895.87 ms |

## 7. Shrink-attempt counts (default mode)

Per failed trial: how much work does the shrinker do? `passed` = candidate
kept the property holding (rejected by shrinker), `failed` = property still broke
(accepted as new minimum), `discarded` = precondition rejected.

| Strategy | passed | failed (= accepted shrinks) | discarded | total |
|---|---:|---:|---:|---:|
| Quick | 137.3 | 13.4 | 6.0 | 156.8 |
| Hedgehog | 28.5 | 8.6 | 1.6 | 38.7 |
| Falsify | 950.6 | 30.6 | 108.6 | 1089.8 |
| QuickCBC | 195.7 | 19.8 | 35.8 | 251.3 |
| HedgehogCBC | 15.7 | 10.3 | 0.0 | 26.0 |
| FalsifyCBC | 1916.9 | 32.8 | 0.0 | 1949.7 |
| HedgehogCBC2 | 17.0 | 10.0 | 0.0 | 27.0 |
| FalsifyCBC2 | 2034.6 | 31.9 | 0.0 | 2066.6 |
| QuickGbE | 55.6 | 8.6 | 12.1 | 76.3 |
| HedgehogGbE | 94.8 | 11.2 | 0.0 | 106.0 |
| FalsifyGbE | 1851.5 | 33.2 | 0.0 | 1884.7 |

## 8. Pre vs post-shrinking counterexample size (default mode)

Token count of `pre_counterexample` and `counterexample`. 
`Δ` = how much the shrinker compressed the input.

| Strategy | mean pre | mean post | mean Δ | mean Δ % |
|---|---:|---:|---:|---:|
| Quick | 23.3 | 15.3 | 8.0 | 34.5% |
| Hedgehog | 23.9 | 16.0 | 7.9 | 32.9% |
| Falsify | 21.6 | 15.4 | 6.2 | 28.6% |
| QuickCBC | 132.2 | 16.2 | 116.0 | 87.8% |
| HedgehogCBC | 93.4 | 23.2 | 70.2 | 75.2% |
| FalsifyCBC | 137.2 | 23.5 | 113.7 | 82.8% |
| HedgehogCBC2 | 41.8 | 20.2 | 21.6 | 51.7% |
| FalsifyCBC2 | 138.9 | 23.6 | 115.2 | 83.0% |
| QuickGbE | 56.4 | 16.2 | 40.2 | 71.2% |
| HedgehogGbE | 60.8 | 13.8 | 47.0 | 77.3% |
| FalsifyGbE | 174.6 | 16.3 | 158.3 | 90.7% |
