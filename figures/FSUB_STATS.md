# FSUB — paired strategy comparison

Within each (property, mutation) task: Mann-Whitney U (two-sided) on the
two strategies' per-trial values. Per-task p-values Holm-corrected within
each (pair, metric). α = 0.05. All metrics lower-is-better.

**Â₁₂** = Vargha-Delaney effect size: probability a random A-trial beats
a random B-trial. Â₁₂ > 0.5 ⇒ A better; reported as the mean over tasks.

## Metric: ted-to-gt

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 13 | 0 | 13 | 0.850 | 26 |
| Quick | Falsify | 1 | 0 | 25 | 0.639 | 26 |
| Quick | Correct | 21 | 0 | 7 | 0.874 | 28 |
| Quick | HedgehogCBC | 28 | 0 | 0 | 0.994 | 28 |
| Quick | FalsifyCBC | 28 | 0 | 0 | 1.000 | 28 |
| Hedgehog | Falsify | 0 | 6 | 20 | 0.255 | 26 |
| Hedgehog | Correct | 18 | 1 | 7 | 0.817 | 26 |
| Hedgehog | HedgehogCBC | 26 | 0 | 0 | 1.000 | 26 |
| Hedgehog | FalsifyCBC | 26 | 0 | 0 | 1.000 | 26 |
| Falsify | Correct | 20 | 0 | 6 | 0.858 | 26 |
| Falsify | HedgehogCBC | 26 | 0 | 0 | 1.000 | 26 |
| Falsify | FalsifyCBC | 26 | 0 | 0 | 1.000 | 26 |
| Correct | HedgehogCBC | 32 | 0 | 4 | 0.945 | 36 |
| Correct | FalsifyCBC | 27 | 0 | 9 | 0.918 | 36 |
| HedgehogCBC | FalsifyCBC | 0 | 2 | 34 | 0.384 | 36 |

## Metric: time-shrinking

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 8 | 0 | 18 | 0.711 | 26 |
| Quick | Falsify | 26 | 0 | 0 | 0.997 | 26 |
| Quick | Correct | 1 | 1 | 26 | 0.464 | 28 |
| Quick | HedgehogCBC | 21 | 0 | 7 | 0.898 | 28 |
| Quick | FalsifyCBC | 28 | 0 | 0 | 0.994 | 28 |
| Hedgehog | Falsify | 26 | 0 | 0 | 1.000 | 26 |
| Hedgehog | Correct | 1 | 9 | 16 | 0.275 | 26 |
| Hedgehog | HedgehogCBC | 20 | 0 | 6 | 0.894 | 26 |
| Hedgehog | FalsifyCBC | 26 | 0 | 0 | 0.978 | 26 |
| Falsify | Correct | 0 | 25 | 1 | 0.016 | 26 |
| Falsify | HedgehogCBC | 0 | 7 | 19 | 0.257 | 26 |
| Falsify | FalsifyCBC | 18 | 4 | 4 | 0.777 | 26 |
| Correct | HedgehogCBC | 29 | 0 | 7 | 0.903 | 36 |
| Correct | FalsifyCBC | 36 | 0 | 0 | 0.993 | 36 |
| HedgehogCBC | FalsifyCBC | 25 | 0 | 11 | 0.844 | 36 |

## Metric: ms-per-edit

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 1 | 0 | 25 | 0.715 | 26 |
| Quick | Falsify | 26 | 0 | 0 | 0.974 | 26 |
| Quick | Correct | 0 | 25 | 3 | 0.036 | 28 |
| Quick | HedgehogCBC | 0 | 5 | 23 | 0.287 | 28 |
| Quick | FalsifyCBC | 13 | 1 | 14 | 0.751 | 28 |
| Hedgehog | Falsify | 5 | 0 | 21 | 0.830 | 26 |
| Hedgehog | Correct | 0 | 26 | 0 | 0.019 | 26 |
| Hedgehog | HedgehogCBC | 0 | 7 | 19 | 0.169 | 26 |
| Hedgehog | FalsifyCBC | 4 | 1 | 21 | 0.609 | 26 |
| Falsify | Correct | 0 | 26 | 0 | 0.006 | 26 |
| Falsify | HedgehogCBC | 0 | 19 | 7 | 0.063 | 26 |
| Falsify | FalsifyCBC | 0 | 5 | 21 | 0.348 | 26 |
| Correct | HedgehogCBC | 28 | 0 | 8 | 0.941 | 36 |
| Correct | FalsifyCBC | 34 | 0 | 2 | 0.978 | 36 |
| HedgehogCBC | FalsifyCBC | 14 | 0 | 22 | 0.792 | 36 |

