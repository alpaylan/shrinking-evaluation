# BST — paired strategy comparison

Within each (property, mutation) task: Mann-Whitney U (two-sided) on the
two strategies' per-trial values. Per-task p-values Holm-corrected within
each (pair, metric). α = 0.05. All metrics lower-is-better.

**Â₁₂** = Vargha-Delaney effect size: probability a random A-trial beats
a random B-trial. Â₁₂ > 0.5 ⇒ A better; reported as the mean over tasks.

## Metric: ted-to-gt

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 3 | 0 | 45 | 0.672 | 48 |
| Quick | Falsify | 0 | 1 | 46 | 0.518 | 47 |
| Quick | QuickCBC | 0 | 1 | 47 | 0.487 | 48 |
| Quick | HedgehogCBC | 16 | 0 | 32 | 0.764 | 48 |
| Quick | HedgehogIdiomatic | 7 | 0 | 41 | 0.708 | 48 |
| Quick | FalsifyCBC | 31 | 1 | 16 | 0.816 | 48 |
| Quick | FalsifyIdiomatic | 28 | 1 | 19 | 0.813 | 48 |
| Quick | QuickGbE | 0 | 0 | 48 | 0.497 | 48 |
| Quick | HedgehogGbE | 19 | 0 | 29 | 0.742 | 48 |
| Quick | FalsifyGbE | 0 | 2 | 46 | 0.460 | 48 |
| Hedgehog | Falsify | 0 | 3 | 44 | 0.359 | 47 |
| Hedgehog | QuickCBC | 0 | 3 | 46 | 0.322 | 49 |
| Hedgehog | HedgehogCBC | 7 | 0 | 42 | 0.678 | 49 |
| Hedgehog | HedgehogIdiomatic | 0 | 0 | 49 | 0.595 | 49 |
| Hedgehog | FalsifyCBC | 12 | 1 | 36 | 0.757 | 49 |
| Hedgehog | FalsifyIdiomatic | 16 | 1 | 32 | 0.756 | 49 |
| Hedgehog | QuickGbE | 0 | 1 | 48 | 0.348 | 49 |
| Hedgehog | HedgehogGbE | 15 | 0 | 34 | 0.627 | 49 |
| Hedgehog | FalsifyGbE | 0 | 4 | 45 | 0.313 | 49 |
| Falsify | QuickCBC | 1 | 0 | 46 | 0.473 | 47 |
| Falsify | HedgehogCBC | 13 | 0 | 34 | 0.758 | 47 |
| Falsify | HedgehogIdiomatic | 6 | 0 | 41 | 0.702 | 47 |
| Falsify | FalsifyCBC | 24 | 0 | 23 | 0.814 | 47 |
| Falsify | FalsifyIdiomatic | 23 | 0 | 24 | 0.812 | 47 |
| Falsify | QuickGbE | 1 | 0 | 46 | 0.486 | 47 |
| Falsify | HedgehogGbE | 18 | 0 | 29 | 0.745 | 47 |
| Falsify | FalsifyGbE | 0 | 1 | 46 | 0.456 | 47 |
| QuickCBC | HedgehogCBC | 15 | 0 | 37 | 0.780 | 52 |
| QuickCBC | HedgehogIdiomatic | 8 | 0 | 44 | 0.716 | 52 |
| QuickCBC | FalsifyCBC | 33 | 1 | 18 | 0.838 | 52 |
| QuickCBC | FalsifyIdiomatic | 32 | 1 | 19 | 0.836 | 52 |
| QuickCBC | QuickGbE | 0 | 0 | 52 | 0.504 | 52 |
| QuickCBC | HedgehogGbE | 18 | 0 | 34 | 0.742 | 52 |
| QuickCBC | FalsifyGbE | 0 | 1 | 51 | 0.469 | 52 |
| HedgehogCBC | HedgehogIdiomatic | 0 | 1 | 51 | 0.394 | 52 |
| HedgehogCBC | FalsifyCBC | 5 | 2 | 45 | 0.548 | 52 |
| HedgehogCBC | FalsifyIdiomatic | 6 | 2 | 44 | 0.550 | 52 |
| HedgehogCBC | QuickGbE | 0 | 14 | 38 | 0.239 | 52 |
| HedgehogCBC | HedgehogGbE | 6 | 8 | 38 | 0.397 | 52 |
| HedgehogCBC | FalsifyGbE | 0 | 17 | 35 | 0.203 | 52 |
| HedgehogIdiomatic | FalsifyCBC | 10 | 2 | 40 | 0.683 | 52 |
| HedgehogIdiomatic | FalsifyIdiomatic | 12 | 2 | 38 | 0.685 | 52 |
| HedgehogIdiomatic | QuickGbE | 0 | 8 | 44 | 0.312 | 52 |
| HedgehogIdiomatic | HedgehogGbE | 13 | 2 | 37 | 0.507 | 52 |
| HedgehogIdiomatic | FalsifyGbE | 0 | 11 | 41 | 0.267 | 52 |
| FalsifyCBC | FalsifyIdiomatic | 0 | 0 | 52 | 0.504 | 52 |
| FalsifyCBC | QuickGbE | 1 | 29 | 22 | 0.181 | 52 |
| FalsifyCBC | HedgehogGbE | 13 | 14 | 25 | 0.467 | 52 |
| FalsifyCBC | FalsifyGbE | 0 | 29 | 23 | 0.161 | 52 |
| FalsifyIdiomatic | QuickGbE | 1 | 30 | 21 | 0.186 | 52 |
| FalsifyIdiomatic | HedgehogGbE | 13 | 12 | 27 | 0.474 | 52 |
| FalsifyIdiomatic | FalsifyGbE | 0 | 31 | 21 | 0.159 | 52 |
| QuickGbE | HedgehogGbE | 16 | 0 | 36 | 0.730 | 52 |
| QuickGbE | FalsifyGbE | 0 | 2 | 50 | 0.471 | 52 |
| HedgehogGbE | FalsifyGbE | 0 | 19 | 33 | 0.240 | 52 |

## Metric: time-shrinking

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 10 | 2 | 36 | 0.650 | 48 |
| Quick | Falsify | 43 | 0 | 4 | 0.965 | 47 |
| Quick | QuickCBC | 2 | 0 | 46 | 0.550 | 48 |
| Quick | HedgehogCBC | 15 | 0 | 33 | 0.747 | 48 |
| Quick | HedgehogIdiomatic | 4 | 0 | 44 | 0.683 | 48 |
| Quick | FalsifyCBC | 38 | 1 | 9 | 0.876 | 48 |
| Quick | FalsifyIdiomatic | 37 | 3 | 8 | 0.865 | 48 |
| Quick | QuickGbE | 0 | 16 | 32 | 0.146 | 48 |
| Quick | HedgehogGbE | 18 | 0 | 30 | 0.858 | 48 |
| Quick | FalsifyGbE | 46 | 0 | 2 | 0.982 | 48 |
| Hedgehog | Falsify | 38 | 1 | 8 | 0.916 | 47 |
| Hedgehog | QuickCBC | 2 | 7 | 40 | 0.394 | 49 |
| Hedgehog | HedgehogCBC | 4 | 2 | 43 | 0.624 | 49 |
| Hedgehog | HedgehogIdiomatic | 1 | 7 | 41 | 0.462 | 49 |
| Hedgehog | FalsifyCBC | 36 | 8 | 5 | 0.813 | 49 |
| Hedgehog | FalsifyIdiomatic | 35 | 7 | 7 | 0.804 | 49 |
| Hedgehog | QuickGbE | 0 | 30 | 19 | 0.097 | 49 |
| Hedgehog | HedgehogGbE | 10 | 0 | 39 | 0.737 | 49 |
| Hedgehog | FalsifyGbE | 43 | 1 | 5 | 0.937 | 49 |
| Falsify | QuickCBC | 0 | 42 | 5 | 0.055 | 47 |
| Falsify | HedgehogCBC | 1 | 36 | 10 | 0.091 | 47 |
| Falsify | HedgehogIdiomatic | 0 | 41 | 6 | 0.061 | 47 |
| Falsify | FalsifyCBC | 7 | 8 | 32 | 0.530 | 47 |
| Falsify | FalsifyIdiomatic | 14 | 7 | 26 | 0.556 | 47 |
| Falsify | QuickGbE | 0 | 44 | 3 | 0.020 | 47 |
| Falsify | HedgehogGbE | 0 | 38 | 9 | 0.080 | 47 |
| Falsify | FalsifyGbE | 10 | 1 | 36 | 0.702 | 47 |
| QuickCBC | HedgehogCBC | 10 | 1 | 41 | 0.702 | 52 |
| QuickCBC | HedgehogIdiomatic | 5 | 1 | 46 | 0.615 | 52 |
| QuickCBC | FalsifyCBC | 41 | 2 | 9 | 0.875 | 52 |
| QuickCBC | FalsifyIdiomatic | 41 | 4 | 7 | 0.864 | 52 |
| QuickCBC | QuickGbE | 0 | 22 | 30 | 0.132 | 52 |
| QuickCBC | HedgehogGbE | 13 | 0 | 39 | 0.835 | 52 |
| QuickCBC | FalsifyGbE | 51 | 0 | 1 | 0.975 | 52 |
| HedgehogCBC | HedgehogIdiomatic | 0 | 3 | 49 | 0.333 | 52 |
| HedgehogCBC | FalsifyCBC | 40 | 8 | 4 | 0.820 | 52 |
| HedgehogCBC | FalsifyIdiomatic | 40 | 8 | 4 | 0.811 | 52 |
| HedgehogCBC | QuickGbE | 0 | 41 | 11 | 0.084 | 52 |
| HedgehogCBC | HedgehogGbE | 5 | 1 | 46 | 0.585 | 52 |
| HedgehogCBC | FalsifyGbE | 48 | 1 | 3 | 0.948 | 52 |
| HedgehogIdiomatic | FalsifyCBC | 43 | 6 | 3 | 0.852 | 52 |
| HedgehogIdiomatic | FalsifyIdiomatic | 42 | 6 | 4 | 0.842 | 52 |
| HedgehogIdiomatic | QuickGbE | 0 | 26 | 26 | 0.110 | 52 |
| HedgehogIdiomatic | HedgehogGbE | 9 | 0 | 43 | 0.790 | 52 |
| HedgehogIdiomatic | FalsifyGbE | 49 | 0 | 3 | 0.968 | 52 |
| FalsifyCBC | FalsifyIdiomatic | 0 | 0 | 52 | 0.514 | 52 |
| FalsifyCBC | QuickGbE | 1 | 45 | 6 | 0.072 | 52 |
| FalsifyCBC | HedgehogGbE | 7 | 42 | 3 | 0.170 | 52 |
| FalsifyCBC | FalsifyGbE | 10 | 2 | 40 | 0.567 | 52 |
| FalsifyIdiomatic | QuickGbE | 2 | 45 | 5 | 0.086 | 52 |
| FalsifyIdiomatic | HedgehogGbE | 6 | 38 | 8 | 0.182 | 52 |
| FalsifyIdiomatic | FalsifyGbE | 7 | 4 | 41 | 0.547 | 52 |
| QuickGbE | HedgehogGbE | 45 | 0 | 7 | 0.953 | 52 |
| QuickGbE | FalsifyGbE | 52 | 0 | 0 | 0.992 | 52 |
| HedgehogGbE | FalsifyGbE | 48 | 1 | 3 | 0.955 | 52 |

## Metric: ms-per-edit

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 1 | 0 | 47 | 0.636 | 48 |
| Quick | Falsify | 38 | 0 | 9 | 0.920 | 47 |
| Quick | QuickCBC | 0 | 42 | 6 | 0.044 | 48 |
| Quick | HedgehogCBC | 1 | 33 | 14 | 0.102 | 48 |
| Quick | HedgehogIdiomatic | 3 | 8 | 37 | 0.321 | 48 |
| Quick | FalsifyCBC | 5 | 11 | 32 | 0.419 | 48 |
| Quick | FalsifyIdiomatic | 5 | 8 | 35 | 0.468 | 48 |
| Quick | QuickGbE | 0 | 21 | 27 | 0.193 | 48 |
| Quick | HedgehogGbE | 5 | 7 | 34 | 0.435 | 46 |
| Quick | FalsifyGbE | 4 | 12 | 32 | 0.333 | 48 |
| Hedgehog | Falsify | 26 | 1 | 20 | 0.853 | 47 |
| Hedgehog | QuickCBC | 0 | 44 | 5 | 0.035 | 49 |
| Hedgehog | HedgehogCBC | 1 | 40 | 8 | 0.084 | 49 |
| Hedgehog | HedgehogIdiomatic | 2 | 12 | 35 | 0.207 | 49 |
| Hedgehog | FalsifyCBC | 6 | 11 | 32 | 0.379 | 49 |
| Hedgehog | FalsifyIdiomatic | 5 | 12 | 32 | 0.416 | 49 |
| Hedgehog | QuickGbE | 0 | 22 | 27 | 0.148 | 49 |
| Hedgehog | HedgehogGbE | 0 | 8 | 39 | 0.338 | 47 |
| Hedgehog | FalsifyGbE | 4 | 17 | 28 | 0.281 | 49 |
| Falsify | QuickCBC | 0 | 47 | 0 | 0.008 | 47 |
| Falsify | HedgehogCBC | 0 | 41 | 6 | 0.031 | 47 |
| Falsify | HedgehogIdiomatic | 0 | 36 | 11 | 0.075 | 47 |
| Falsify | FalsifyCBC | 0 | 35 | 12 | 0.086 | 47 |
| Falsify | FalsifyIdiomatic | 0 | 41 | 6 | 0.086 | 47 |
| Falsify | QuickGbE | 0 | 40 | 7 | 0.050 | 47 |
| Falsify | HedgehogGbE | 0 | 30 | 15 | 0.132 | 45 |
| Falsify | FalsifyGbE | 0 | 42 | 5 | 0.044 | 47 |
| QuickCBC | HedgehogCBC | 10 | 0 | 42 | 0.807 | 52 |
| QuickCBC | HedgehogIdiomatic | 47 | 0 | 5 | 0.939 | 52 |
| QuickCBC | FalsifyCBC | 34 | 0 | 18 | 0.865 | 52 |
| QuickCBC | FalsifyIdiomatic | 33 | 0 | 19 | 0.861 | 52 |
| QuickCBC | QuickGbE | 19 | 0 | 33 | 0.760 | 52 |
| QuickCBC | HedgehogGbE | 31 | 0 | 19 | 0.927 | 50 |
| QuickCBC | FalsifyGbE | 42 | 0 | 10 | 0.913 | 52 |
| HedgehogCBC | HedgehogIdiomatic | 9 | 0 | 43 | 0.841 | 52 |
| HedgehogCBC | FalsifyCBC | 28 | 4 | 20 | 0.744 | 52 |
| HedgehogCBC | FalsifyIdiomatic | 27 | 2 | 23 | 0.744 | 52 |
| HedgehogCBC | QuickGbE | 5 | 0 | 47 | 0.586 | 52 |
| HedgehogCBC | HedgehogGbE | 11 | 0 | 39 | 0.792 | 50 |
| HedgehogCBC | FalsifyGbE | 28 | 2 | 22 | 0.797 | 52 |
| HedgehogIdiomatic | FalsifyCBC | 14 | 9 | 29 | 0.612 | 52 |
| HedgehogIdiomatic | FalsifyIdiomatic | 16 | 9 | 27 | 0.617 | 52 |
| HedgehogIdiomatic | QuickGbE | 0 | 3 | 49 | 0.293 | 52 |
| HedgehogIdiomatic | HedgehogGbE | 0 | 2 | 48 | 0.589 | 50 |
| HedgehogIdiomatic | FalsifyGbE | 11 | 10 | 31 | 0.574 | 52 |
| FalsifyCBC | FalsifyIdiomatic | 0 | 0 | 52 | 0.526 | 52 |
| FalsifyCBC | QuickGbE | 7 | 22 | 23 | 0.315 | 52 |
| FalsifyCBC | HedgehogGbE | 6 | 16 | 28 | 0.413 | 50 |
| FalsifyCBC | FalsifyGbE | 7 | 5 | 40 | 0.460 | 52 |
| FalsifyIdiomatic | QuickGbE | 6 | 23 | 23 | 0.306 | 52 |
| FalsifyIdiomatic | HedgehogGbE | 7 | 17 | 26 | 0.398 | 50 |
| FalsifyIdiomatic | FalsifyGbE | 4 | 4 | 44 | 0.441 | 52 |
| QuickGbE | HedgehogGbE | 4 | 0 | 46 | 0.759 | 50 |
| QuickGbE | FalsifyGbE | 23 | 8 | 21 | 0.666 | 52 |
| HedgehogGbE | FalsifyGbE | 13 | 10 | 27 | 0.553 | 50 |

