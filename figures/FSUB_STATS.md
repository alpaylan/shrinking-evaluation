# FSUB — paired strategy comparison

Within each (property, mutation) task: Mann-Whitney U (two-sided) on the
two strategies' per-trial values. Per-task p-values Holm-corrected within
each (pair, metric). α = 0.05. All metrics lower-is-better.

**Â₁₂** = Vargha-Delaney effect size: probability a random A-trial beats
a random B-trial. Â₁₂ > 0.5 ⇒ A better; reported as the mean over tasks.

## Metric: ted-to-gt

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 3 | 2 | 13 | 0.644 | 18 |
| Quick | Falsify | 0 | 1 | 0 | 0.037 | 1 |
| Quick | Correct | 18 | 0 | 13 | 0.847 | 31 |
| Quick | HedgehogCBC | 31 | 0 | 0 | 0.997 | 31 |
| Quick | FalsifyCBC | 30 | 0 | 1 | 0.997 | 31 |
| Hedgehog | Falsify | 0 | 0 | 1 | 0.700 | 1 |
| Hedgehog | Correct | 12 | 3 | 3 | 0.756 | 18 |
| Hedgehog | HedgehogCBC | 18 | 0 | 0 | 1.000 | 18 |
| Hedgehog | FalsifyCBC | 18 | 0 | 0 | 1.000 | 18 |
| Falsify | Correct | 1 | 0 | 0 | 1.000 | 1 |
| Falsify | HedgehogCBC | 1 | 0 | 0 | 1.000 | 1 |
| Falsify | FalsifyCBC | 1 | 0 | 0 | 1.000 | 1 |
| Correct | HedgehogCBC | 29 | 0 | 7 | 0.935 | 36 |
| Correct | FalsifyCBC | 22 | 0 | 14 | 0.893 | 36 |
| HedgehogCBC | FalsifyCBC | 0 | 0 | 36 | 0.357 | 36 |

## Metric: time-shrinking

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 2 | 0 | 16 | 0.625 | 18 |
| Quick | Falsify | 1 | 0 | 0 | 1.000 | 1 |
| Quick | Correct | 0 | 3 | 28 | 0.247 | 31 |
| Quick | HedgehogCBC | 20 | 0 | 11 | 0.884 | 31 |
| Quick | FalsifyCBC | 28 | 0 | 3 | 0.985 | 31 |
| Hedgehog | Falsify | 1 | 0 | 0 | 1.000 | 1 |
| Hedgehog | Correct | 0 | 4 | 14 | 0.186 | 18 |
| Hedgehog | HedgehogCBC | 11 | 0 | 7 | 0.839 | 18 |
| Hedgehog | FalsifyCBC | 17 | 0 | 1 | 0.973 | 18 |
| Falsify | Correct | 0 | 1 | 0 | 0.000 | 1 |
| Falsify | HedgehogCBC | 0 | 0 | 1 | 0.500 | 1 |
| Falsify | FalsifyCBC | 0 | 1 | 0 | 0.125 | 1 |
| Correct | HedgehogCBC | 28 | 0 | 8 | 0.904 | 36 |
| Correct | FalsifyCBC | 36 | 0 | 0 | 0.989 | 36 |
| HedgehogCBC | FalsifyCBC | 24 | 0 | 12 | 0.818 | 36 |

## Metric: ms-per-edit

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 17 | 0 | 1 | 0.947 | 18 |
| Quick | Falsify | 1 | 0 | 0 | 1.000 | 1 |
| Quick | Correct | 0 | 21 | 10 | 0.083 | 31 |
| Quick | HedgehogCBC | 2 | 0 | 29 | 0.688 | 31 |
| Quick | FalsifyCBC | 17 | 0 | 14 | 0.820 | 31 |
| Hedgehog | Falsify | 1 | 0 | 0 | 0.950 | 1 |
| Hedgehog | Correct | 0 | 16 | 2 | 0.020 | 18 |
| Hedgehog | HedgehogCBC | 0 | 3 | 15 | 0.223 | 18 |
| Hedgehog | FalsifyCBC | 0 | 3 | 15 | 0.487 | 18 |
| Falsify | Correct | 0 | 1 | 0 | 0.000 | 1 |
| Falsify | HedgehogCBC | 0 | 1 | 0 | 0.050 | 1 |
| Falsify | FalsifyCBC | 0 | 1 | 0 | 0.000 | 1 |
| Correct | HedgehogCBC | 25 | 0 | 11 | 0.953 | 36 |
| Correct | FalsifyCBC | 34 | 0 | 2 | 0.971 | 36 |
| HedgehogCBC | FalsifyCBC | 13 | 0 | 23 | 0.794 | 36 |

