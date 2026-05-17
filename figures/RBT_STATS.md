# RBT — paired strategy comparison

Within each (property, mutation) task: Mann-Whitney U (two-sided) on the
two strategies' per-trial values. Per-task p-values Holm-corrected within
each (pair, metric). α = 0.05. All metrics lower-is-better.

**Â₁₂** = Vargha-Delaney effect size: probability a random A-trial beats
a random B-trial. Â₁₂ > 0.5 ⇒ A better; reported as the mean over tasks.

## Metric: ted-to-gt

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 9 | 0 | 20 | 0.705 | 29 |
| Quick | Falsify | 0 | 1 | 28 | 0.501 | 29 |
| Quick | QuickCBC | 2 | 0 | 25 | 0.593 | 27 |
| Quick | HedgehogCBC | 10 | 0 | 17 | 0.770 | 27 |
| Quick | FalsifyCBC | 14 | 1 | 12 | 0.789 | 27 |
| Quick | QuickGbE | 2 | 0 | 29 | 0.616 | 31 |
| Quick | HedgehogGbE | 14 | 0 | 17 | 0.778 | 31 |
| Quick | FalsifyGbE | 2 | 1 | 28 | 0.557 | 31 |
| Hedgehog | Falsify | 0 | 7 | 21 | 0.316 | 28 |
| Hedgehog | QuickCBC | 1 | 8 | 16 | 0.375 | 25 |
| Hedgehog | HedgehogCBC | 6 | 3 | 16 | 0.564 | 25 |
| Hedgehog | FalsifyCBC | 10 | 2 | 13 | 0.657 | 25 |
| Hedgehog | QuickGbE | 0 | 2 | 27 | 0.439 | 29 |
| Hedgehog | HedgehogGbE | 10 | 0 | 19 | 0.698 | 29 |
| Hedgehog | FalsifyGbE | 0 | 6 | 23 | 0.368 | 29 |
| Falsify | QuickCBC | 2 | 0 | 23 | 0.597 | 25 |
| Falsify | HedgehogCBC | 7 | 0 | 18 | 0.764 | 25 |
| Falsify | FalsifyCBC | 12 | 0 | 13 | 0.791 | 25 |
| Falsify | QuickGbE | 1 | 0 | 28 | 0.608 | 29 |
| Falsify | HedgehogGbE | 13 | 0 | 16 | 0.799 | 29 |
| Falsify | FalsifyGbE | 0 | 0 | 29 | 0.562 | 29 |
| QuickCBC | HedgehogCBC | 2 | 0 | 28 | 0.679 | 30 |
| QuickCBC | FalsifyCBC | 8 | 1 | 21 | 0.713 | 30 |
| QuickCBC | QuickGbE | 0 | 0 | 30 | 0.470 | 30 |
| QuickCBC | HedgehogGbE | 9 | 3 | 18 | 0.592 | 30 |
| QuickCBC | FalsifyGbE | 1 | 4 | 25 | 0.391 | 30 |
| HedgehogCBC | FalsifyCBC | 4 | 1 | 25 | 0.560 | 30 |
| HedgehogCBC | QuickGbE | 0 | 3 | 27 | 0.319 | 30 |
| HedgehogCBC | HedgehogGbE | 6 | 10 | 14 | 0.450 | 30 |
| HedgehogCBC | FalsifyGbE | 0 | 13 | 17 | 0.230 | 30 |
| FalsifyCBC | QuickGbE | 1 | 7 | 22 | 0.280 | 30 |
| FalsifyCBC | HedgehogGbE | 8 | 11 | 11 | 0.506 | 30 |
| FalsifyCBC | FalsifyGbE | 0 | 17 | 13 | 0.212 | 30 |
| QuickGbE | HedgehogGbE | 8 | 0 | 26 | 0.623 | 34 |
| QuickGbE | FalsifyGbE | 0 | 1 | 33 | 0.431 | 34 |
| HedgehogGbE | FalsifyGbE | 0 | 11 | 23 | 0.294 | 34 |

## Metric: time-shrinking

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 5 | 0 | 24 | 0.754 | 29 |
| Quick | Falsify | 26 | 0 | 3 | 0.982 | 29 |
| Quick | QuickCBC | 3 | 2 | 22 | 0.530 | 27 |
| Quick | HedgehogCBC | 18 | 0 | 9 | 0.907 | 27 |
| Quick | FalsifyCBC | 20 | 6 | 1 | 0.762 | 27 |
| Quick | QuickGbE | 0 | 11 | 21 | 0.230 | 32 |
| Quick | HedgehogGbE | 21 | 0 | 11 | 0.911 | 32 |
| Quick | FalsifyGbE | 31 | 0 | 1 | 0.977 | 32 |
| Hedgehog | Falsify | 25 | 0 | 3 | 0.959 | 28 |
| Hedgehog | QuickCBC | 0 | 14 | 11 | 0.240 | 25 |
| Hedgehog | HedgehogCBC | 4 | 0 | 21 | 0.589 | 25 |
| Hedgehog | FalsifyCBC | 18 | 6 | 1 | 0.720 | 25 |
| Hedgehog | QuickGbE | 0 | 22 | 7 | 0.102 | 29 |
| Hedgehog | HedgehogGbE | 6 | 1 | 22 | 0.680 | 29 |
| Hedgehog | FalsifyGbE | 28 | 0 | 1 | 0.955 | 29 |
| Falsify | QuickCBC | 0 | 21 | 4 | 0.036 | 25 |
| Falsify | HedgehogCBC | 0 | 20 | 5 | 0.078 | 25 |
| Falsify | FalsifyCBC | 0 | 12 | 13 | 0.259 | 25 |
| Falsify | QuickGbE | 0 | 27 | 2 | 0.009 | 29 |
| Falsify | HedgehogGbE | 1 | 26 | 2 | 0.048 | 29 |
| Falsify | FalsifyGbE | 2 | 6 | 21 | 0.479 | 29 |
| QuickCBC | HedgehogCBC | 14 | 6 | 20 | 0.663 | 40 |
| QuickCBC | FalsifyCBC | 33 | 6 | 2 | 0.820 | 41 |
| QuickCBC | QuickGbE | 0 | 13 | 32 | 0.217 | 45 |
| QuickCBC | HedgehogGbE | 18 | 0 | 25 | 0.816 | 43 |
| QuickCBC | FalsifyGbE | 41 | 0 | 1 | 0.984 | 42 |
| HedgehogCBC | FalsifyCBC | 29 | 7 | 4 | 0.795 | 40 |
| HedgehogCBC | QuickGbE | 0 | 23 | 17 | 0.171 | 40 |
| HedgehogCBC | HedgehogGbE | 10 | 0 | 30 | 0.624 | 40 |
| HedgehogCBC | FalsifyGbE | 39 | 1 | 0 | 0.960 | 40 |
| FalsifyCBC | QuickGbE | 4 | 33 | 4 | 0.166 | 41 |
| FalsifyCBC | HedgehogGbE | 6 | 21 | 14 | 0.276 | 41 |
| FalsifyCBC | FalsifyGbE | 17 | 0 | 24 | 0.739 | 41 |
| QuickGbE | HedgehogGbE | 38 | 0 | 18 | 0.914 | 56 |
| QuickGbE | FalsifyGbE | 55 | 0 | 0 | 0.994 | 55 |
| HedgehogGbE | FalsifyGbE | 53 | 1 | 0 | 0.973 | 54 |

## Metric: ms-per-edit

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 4 | 0 | 25 | 0.786 | 29 |
| Quick | Falsify | 26 | 1 | 2 | 0.956 | 29 |
| Quick | QuickCBC | 1 | 20 | 6 | 0.144 | 27 |
| Quick | HedgehogCBC | 3 | 0 | 24 | 0.574 | 27 |
| Quick | FalsifyCBC | 4 | 3 | 20 | 0.472 | 27 |
| Quick | QuickGbE | 0 | 12 | 19 | 0.156 | 31 |
| Quick | HedgehogGbE | 5 | 4 | 18 | 0.415 | 27 |
| Quick | FalsifyGbE | 5 | 15 | 11 | 0.282 | 31 |
| Hedgehog | Falsify | 17 | 1 | 10 | 0.872 | 28 |
| Hedgehog | QuickCBC | 0 | 25 | 0 | 0.040 | 25 |
| Hedgehog | HedgehogCBC | 0 | 5 | 20 | 0.304 | 25 |
| Hedgehog | FalsifyCBC | 3 | 8 | 14 | 0.346 | 25 |
| Hedgehog | QuickGbE | 0 | 23 | 6 | 0.078 | 29 |
| Hedgehog | HedgehogGbE | 0 | 6 | 19 | 0.235 | 25 |
| Hedgehog | FalsifyGbE | 3 | 16 | 10 | 0.194 | 29 |
| Falsify | QuickCBC | 0 | 23 | 2 | 0.005 | 25 |
| Falsify | HedgehogCBC | 1 | 17 | 7 | 0.106 | 25 |
| Falsify | FalsifyCBC | 0 | 16 | 9 | 0.093 | 25 |
| Falsify | QuickGbE | 0 | 24 | 5 | 0.038 | 29 |
| Falsify | HedgehogGbE | 0 | 17 | 8 | 0.083 | 25 |
| Falsify | FalsifyGbE | 0 | 24 | 5 | 0.040 | 29 |
| QuickCBC | HedgehogCBC | 16 | 0 | 14 | 0.827 | 30 |
| QuickCBC | FalsifyCBC | 11 | 0 | 19 | 0.782 | 30 |
| QuickCBC | QuickGbE | 1 | 2 | 27 | 0.535 | 30 |
| QuickCBC | HedgehogGbE | 5 | 0 | 21 | 0.687 | 26 |
| QuickCBC | FalsifyGbE | 5 | 0 | 25 | 0.647 | 30 |
| HedgehogCBC | FalsifyCBC | 8 | 3 | 19 | 0.543 | 30 |
| HedgehogCBC | QuickGbE | 0 | 14 | 16 | 0.181 | 30 |
| HedgehogCBC | HedgehogGbE | 0 | 6 | 20 | 0.345 | 26 |
| HedgehogCBC | FalsifyGbE | 4 | 11 | 15 | 0.301 | 30 |
| FalsifyCBC | QuickGbE | 1 | 11 | 18 | 0.295 | 30 |
| FalsifyCBC | HedgehogGbE | 2 | 12 | 12 | 0.338 | 26 |
| FalsifyCBC | FalsifyGbE | 0 | 8 | 22 | 0.277 | 30 |
| QuickGbE | HedgehogGbE | 5 | 0 | 25 | 0.742 | 30 |
| QuickGbE | FalsifyGbE | 13 | 4 | 17 | 0.626 | 34 |
| HedgehogGbE | FalsifyGbE | 4 | 4 | 22 | 0.557 | 30 |

