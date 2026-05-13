# BST analysis — v2 (per-task aggregation + medians)

**Aggregation rule for every table:**
1. *Within each task* `(property, mutation)`, collapse the 10 trials with **median**.
2. *Across the 52 tasks*, report **median / mean / p90 / max** of the per-task medians.

This drops the influence of outlier trials within a task AND prevents one
expensive task (insert_3 / union_8) from dominating the cross-task mean.

Format: **task-median / cross-task-mean / p90 / max** for cross-task distribution columns,
or **task-median / cross-task-mean** where a single headline is enough.

## 2. Effectiveness — TED to ground-truth minimum

Lower is better. Per task: median TED across trials. Then cross-task:
median / mean / p90 / max of those per-task medians.

| Strategy | none | fixed-100 | default |
|---|---|---|---|
| Quick | 6.0 / 11.6 / 13.0 / 88.5 | 3.0 / 4.5 / 10.0 / 42.0 | 3.0 / 2.9 / 8.0 / 10.5 |
| Hedgehog | 5.0 / 11.5 / 15.0 / 97.0 | 3.0 / 3.6 / 9.0 / 14.0 | 3.0 / 3.7 / 9.5 / 13.0 |
| Falsify | 5.0 / 10.6 / 13.0 / 113.0 | 3.0 / 3.2 / 9.0 / 12.0 | 3.0 / 3.0 / 8.0 / 12.0 |
| QuickCBC | 126.8 / 128.0 / 195.0 / 270.0 | 3.0 / 16.8 / 56.5 / 163.5 | 3.0 / 3.4 / 9.0 / 13.5 |
| HedgehogCBC | 69.5 / 79.0 / 129.0 / 193.5 | 7.8 / 8.8 / 19.0 / 22.0 | 8.2 / 9.3 / 19.0 / 32.0 |
| FalsifyCBC | 118.5 / 123.8 / 187.5 / 255.0 | 8.0 / 10.7 / 22.0 / 83.5 | 8.0 / 10.5 / 24.0 / 39.0 |
| HedgehogCBC2 | 23.5 / 26.2 / 53.0 / 65.0 | 4.0 / 5.6 / 13.0 / 15.5 | 6.0 / 6.6 / 14.5 / 26.5 |
| FalsifyCBC2 | 117.8 / 125.3 / 184.0 / 246.0 | 7.5 / 10.5 / 23.0 / 56.5 | 8.5 / 10.4 / 25.0 / 33.0 |
| QuickGbE | 19.8 / 38.0 / 69.5 / 263.0 | 3.0 / 12.1 / 10.0 / 208.0 | 3.0 / 3.3 / 8.0 / 12.0 |
| HedgehogGbE | 20.5 / 42.8 / 111.0 / 170.0 | 6.0 / 5.6 / 9.0 / 14.0 | 6.0 / 5.5 / 9.5 / 13.0 |
| FalsifyGbE | 164.5 / 169.5 / 254.0 / 312.0 | 2.5 / 3.1 / 8.0 / 19.5 | 3.0 / 2.9 / 7.0 / 10.0 |

### 2a. Fraction of *tasks* whose median trial reaches TED = 0

Per task: take the median TED across its 10 trials. Count the task as 'solved'
if that per-task median is 0 — i.e., at least half the trials hit the optimum.

| Strategy | none | fixed-100 | default |
|---|---:|---:|---:|
| Quick | 0.0% | 34.0% | 35.4% |
| Hedgehog | 2.0% | 22.0% | 20.0% |
| Falsify | 0.0% | 35.4% | 33.3% |
| QuickCBC | 0.0% | 30.8% | 34.6% |
| HedgehogCBC | 0.0% | 17.3% | 13.5% |
| FalsifyCBC | 0.0% | 9.6% | 9.6% |
| HedgehogCBC2 | 0.0% | 21.2% | 13.5% |
| FalsifyCBC2 | 0.0% | 9.6% | 9.6% |
| QuickGbE | 0.0% | 32.7% | 32.7% |
| HedgehogGbE | 0.0% | 0.0% | 3.8% |
| FalsifyGbE | 0.0% | 38.5% | 34.6% |

## 3. Performance — milliseconds spent shrinking per unit of TED progress

Per trial: `time_shrinking / (pre_TED − post_TED)` if reduction > 0, else excluded.
Per task: median ms/edit. Cross-task: median / mean / p90 / max.

| Strategy | fixed-100 | default |
|---|---|---|
| Quick | 0.10 / 0.14 / 0.39 / 0.41 | 0.12 / 0.19 / 0.36 / 1.27 |
| Hedgehog | 0.14 / 0.21 / 0.47 / 0.99 | 0.16 / 0.28 / 0.58 / 1.98 |
| Falsify | 0.94 / 108.91 / 9.14 / 4819.20 | 1.38 / 73.43 / 15.12 / 2666.31 |
| QuickCBC | 0.00 / 0.01 / 0.01 / 0.04 | 0.01 / 0.01 / 0.01 / 0.02 |
| HedgehogCBC | 0.01 / 0.02 / 0.03 / 0.11 | 0.02 / 0.02 / 0.03 / 0.08 |
| FalsifyCBC | 0.09 / 0.43 / 1.06 / 8.82 | 0.12 / 0.43 / 1.48 / 5.49 |
| HedgehogCBC2 | 0.05 / 0.07 / 0.13 / 0.42 | 0.04 / 0.06 / 0.13 / 0.19 |
| FalsifyCBC2 | 0.10 / 0.45 / 1.16 / 9.13 | 0.12 / 1.07 / 1.24 / 37.51 |
| QuickGbE | 0.02 / 0.03 / 0.05 / 0.09 | 0.02 / 0.03 / 0.07 / 0.11 |
| HedgehogGbE | 0.06 / 0.07 / 0.16 / 0.25 | 0.05 / 0.09 / 0.17 / 0.40 |
| FalsifyGbE | 0.06 / 0.21 / 0.50 / 1.86 | 0.08 / 0.35 / 0.50 / 8.91 |

## 4. Cost of enabling shrinking — search-phase overhead

`time_pre_failure` (s). Per task: median across 10 trials. Cross-task: median, mean.
`default/none` is the task-level paired ratio (geometric over tasks where both exist).

| Strategy | none (med / mean) | 100 (med / mean) | default (med / mean) | default/none task-median ratio |
|---|---|---|---|---:|
| Quick | 0.0181 / 6.1582 | 0.0202 / 13.2350 | 0.0243 / 10.0929 | 1.04x |
| Hedgehog | 0.2393 / 15.5838 | 0.2379 / 11.9182 | 0.2366 / 9.3840 | 1.14x |
| Falsify | 0.0609 / 7.5334 | 0.0531 / 13.3886 | 0.0643 / 15.1203 | 1.02x |
| QuickCBC | 0.0007 / 0.2231 | 0.0010 / 0.1868 | 0.0008 / 0.1692 | 1.07x |
| HedgehogCBC | 0.0004 / 0.0305 | 0.0004 / 0.0204 | 0.0004 / 0.0409 | 1.03x |
| FalsifyCBC | 0.0021 / 0.4478 | 0.0022 / 1.2851 | 0.0025 / 1.7490 | 1.01x |
| HedgehogCBC2 | 0.0069 / 0.2291 | 0.0059 / 0.2354 | 0.0049 / 0.1912 | 1.01x |
| FalsifyCBC2 | 0.0021 / 2.2694 | 0.0023 / 1.8406 | 0.0028 / 2.7524 | 0.96x |
| QuickGbE | 0.0003 / 0.0005 | 0.0003 / 0.0007 | 0.0003 / 0.0006 | 1.09x |
| HedgehogGbE | 0.0037 / 0.4235 | 0.0042 / 0.4418 | 0.0037 / 0.3286 | 0.96x |
| FalsifyGbE | 0.0021 / 0.6578 | 0.0039 / 0.7507 | 0.0029 / 1.9958 | 1.04x |

## 5. Stability across generators (default mode)

### vanilla

| Framework | TED (med / mean / p90 / max) | time_pre s (med / mean) | n tasks |
|---|---|---|---:|
| Quick | 3.0 / 2.9 / 8.0 / 10.5 | 0.0243 / 10.0929 | 48 |
| Hedgehog | 3.0 / 3.7 / 9.5 / 13.0 | 0.2366 / 9.3840 | 50 |
| Falsify | 3.0 / 3.0 / 8.0 / 12.0 | 0.0643 / 15.1203 | 48 |

### CBC

| Framework | TED (med / mean / p90 / max) | time_pre s (med / mean) | n tasks |
|---|---|---|---:|
| QuickCBC | 3.0 / 3.4 / 9.0 / 13.5 | 0.0008 / 0.1692 | 52 |
| HedgehogCBC | 8.2 / 9.3 / 19.0 / 32.0 | 0.0004 / 0.0409 | 52 |
| FalsifyCBC | 8.0 / 10.5 / 24.0 / 39.0 | 0.0025 / 1.7490 | 52 |

### CBC2

| Framework | TED (med / mean / p90 / max) | time_pre s (med / mean) | n tasks |
|---|---|---|---:|
| HedgehogCBC2 | 6.0 / 6.6 / 14.5 / 26.5 | 0.0049 / 0.1912 | 52 |
| FalsifyCBC2 | 8.5 / 10.4 / 25.0 / 33.0 | 0.0028 / 2.7524 | 52 |

### GbE

| Framework | TED (med / mean / p90 / max) | time_pre s (med / mean) | n tasks |
|---|---|---|---:|
| QuickGbE | 3.0 / 3.3 / 8.0 / 12.0 | 0.0003 / 0.0006 | 52 |
| HedgehogGbE | 6.0 / 5.5 / 9.5 / 13.0 | 0.0037 / 0.3286 | 52 |
| FalsifyGbE | 3.0 / 2.9 / 7.0 / 10.0 | 0.0029 / 1.9958 | 52 |

## 6. Time decomposition (default mode)

Per-task medians (ms). Then cross-task **median / mean**.

| Strategy | execution (med/mean) | generation (med/mean) | shrinking (med/mean) | total (med) |
|---|---|---|---|---:|
| Quick | 12.68 / 5356.71 | 11.24 / 4736.12 | 0.59 / 0.69 | 24.50 ms |
| Hedgehog | 0.43 / 9.76 | 236.23 / 9374.28 | 0.58 / 0.73 | 237.23 ms |
| Falsify | 4.77 / 1177.05 | 57.29 / 13943.25 | 4.74 / 308.42 | 66.80 ms |
| QuickCBC | 0.41 / 137.31 | 0.35 / 31.79 | 0.57 / 0.87 | 1.34 ms |
| HedgehogCBC | 0.01 / 0.94 | 0.37 / 39.93 | 0.87 / 1.02 | 1.25 ms |
| FalsifyCBC | 2.22 / 1693.91 | 0.14 / 51.72 | 10.08 / 45.32 | 12.44 ms |
| HedgehogCBC2 | 0.13 / 3.35 | 4.82 / 187.87 | 0.64 / 0.78 | 5.59 ms |
| FalsifyCBC2 | 2.52 / 2685.65 | 0.15 / 67.84 | 15.48 / 100.38 | 18.15 ms |
| QuickGbE | 0.03 / 0.28 | 0.25 / 0.28 | 0.33 / 0.42 | 0.61 ms |
| HedgehogGbE | 0.20 / 22.61 | 3.53 / 305.94 | 0.86 / 1.42 | 4.59 ms |
| FalsifyGbE | 2.86 / 1964.92 | 0.07 / 30.83 | 9.86 / 41.48 | 12.78 ms |

## 7. Shrink-attempt counts (default mode)

Per-task medians across 10 trials. Cross-task **median / mean**.

| Strategy | passed (med/mean) | failed (med/mean) | discarded (med/mean) |
|---|---|---|---|
| Quick | 85.5 / 130.2 | 13.5 / 12.8 | 0.0 / 3.0 |
| Hedgehog | 19.5 / 27.7 | 8.0 / 8.0 | 0.0 / 0.7 |
| Falsify | 637.0 / 899.6 | 24.2 / 29.8 | 0.0 / 80.9 |
| QuickCBC | 105.8 / 191.0 | 17.2 / 19.4 | 0.0 / 26.3 |
| HedgehogCBC | 9.0 / 12.5 | 9.0 / 9.7 | 0.0 / 0.0 |
| FalsifyCBC | 920.2 / 1696.9 | 26.8 / 29.3 | 0.0 / 0.0 |
| HedgehogCBC2 | 13.2 / 15.4 | 9.5 / 9.6 | 0.0 / 0.0 |
| FalsifyCBC2 | 1186.5 / 1888.1 | 27.2 / 29.5 | 0.0 / 0.0 |
| QuickGbE | 35.5 / 51.0 | 7.0 / 8.6 | 0.0 / 8.0 |
| HedgehogGbE | 42.5 / 90.4 | 8.8 / 11.1 | 0.0 / 0.0 |
| FalsifyGbE | 1006.2 / 1721.1 | 26.0 / 32.0 | 0.0 / 0.0 |

## 8. Pre vs post-shrinking counterexample size (default mode)

Per-task medians of token-count. Cross-task **median / mean**.

| Strategy | mean pre (med/mean) | mean post (med/mean) | mean Δ (med/mean) | mean Δ % |
|---|---|---|---|---:|
| Quick | 15.5 / 21.6 | 13.0 / 15.2 | 0.0 / 6.4 | 0.0% |
| Hedgehog | 15.5 / 22.3 | 13.0 / 15.7 | 0.0 / 6.1 | 0.0% |
| Falsify | 16.0 / 19.6 | 13.0 / 15.2 | 0.0 / 4.1 | 0.0% |
| QuickCBC | 127.0 / 130.6 | 13.0 / 16.1 | 109.5 / 114.5 | 88.3% |
| HedgehogCBC | 82.0 / 92.2 | 22.5 / 22.8 | 58.5 / 68.4 | 73.6% |
| FalsifyCBC | 125.5 / 139.5 | 23.0 / 23.8 | 109.5 / 115.8 | 82.1% |
| HedgehogCBC2 | 31.5 / 38.4 | 17.0 / 19.1 | 15.0 / 18.3 | 45.7% |
| FalsifyCBC2 | 133.5 / 139.2 | 23.0 / 23.6 | 103.5 / 115.0 | 83.2% |
| QuickGbE | 33.5 / 48.3 | 13.0 / 15.9 | 18.0 / 32.1 | 50.0% |
| HedgehogGbE | 28.5 / 54.8 | 12.0 / 13.6 | 12.0 / 41.0 | 58.3% |
| FalsifyGbE | 164.5 / 176.1 | 14.5 / 16.1 | 147.0 / 159.8 | 90.9% |
