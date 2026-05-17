# STLC — paired strategy comparison

Within each (property, mutation) task: Mann-Whitney U (two-sided) on the
two strategies' per-trial values. Per-task p-values Holm-corrected within
each (pair, metric). α = 0.05. All metrics lower-is-better.

**Â₁₂** = Vargha-Delaney effect size: probability a random A-trial beats
a random B-trial. Â₁₂ > 0.5 ⇒ A better; reported as the mean over tasks.

## Metric: ted-to-gt

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 8 | 0 | 8 | 0.775 | 16 |
| Quick | Falsify | 5 | 0 | 11 | 0.717 | 16 |
| Quick | Correct | 6 | 0 | 10 | 0.828 | 16 |
| Quick | HedgehogCBC | 15 | 0 | 1 | 0.935 | 16 |
| Quick | FalsifyCBC | 11 | 0 | 5 | 0.826 | 16 |
| Hedgehog | Falsify | 0 | 1 | 15 | 0.344 | 16 |
| Hedgehog | Correct | 1 | 0 | 15 | 0.729 | 16 |
| Hedgehog | HedgehogCBC | 10 | 0 | 6 | 0.837 | 16 |
| Hedgehog | FalsifyCBC | 0 | 0 | 16 | 0.583 | 16 |
| Falsify | Correct | 3 | 0 | 13 | 0.753 | 16 |
| Falsify | HedgehogCBC | 12 | 0 | 4 | 0.873 | 16 |
| Falsify | FalsifyCBC | 2 | 0 | 14 | 0.689 | 16 |
| Correct | HedgehogCBC | 0 | 0 | 20 | 0.526 | 20 |
| Correct | FalsifyCBC | 0 | 1 | 19 | 0.358 | 20 |
| HedgehogCBC | FalsifyCBC | 0 | 7 | 13 | 0.192 | 20 |

## Metric: time-shrinking

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 0 | 1 | 15 | 0.373 | 16 |
| Quick | Falsify | 16 | 0 | 0 | 1.000 | 16 |
| Quick | Correct | 0 | 0 | 16 | 0.449 | 16 |
| Quick | HedgehogCBC | 10 | 0 | 6 | 0.897 | 16 |
| Quick | FalsifyCBC | 16 | 0 | 0 | 1.000 | 16 |
| Hedgehog | Falsify | 16 | 0 | 0 | 1.000 | 16 |
| Hedgehog | Correct | 0 | 0 | 16 | 0.440 | 16 |
| Hedgehog | HedgehogCBC | 16 | 0 | 0 | 0.953 | 16 |
| Hedgehog | FalsifyCBC | 16 | 0 | 0 | 1.000 | 16 |
| Falsify | Correct | 0 | 16 | 0 | 0.004 | 16 |
| Falsify | HedgehogCBC | 0 | 16 | 0 | 0.022 | 16 |
| Falsify | FalsifyCBC | 0 | 4 | 12 | 0.217 | 16 |
| Correct | HedgehogCBC | 9 | 0 | 11 | 0.867 | 20 |
| Correct | FalsifyCBC | 20 | 0 | 0 | 0.997 | 20 |
| HedgehogCBC | FalsifyCBC | 20 | 0 | 0 | 0.983 | 20 |

## Metric: ms-per-edit

| A | B | A better | B better | n.s. | mean Â₁₂(A,B) | n tasks |
|---|---|---:|---:|---:|---:|---:|
| Quick | Hedgehog | 0 | 0 | 16 | 0.528 | 16 |
| Quick | Falsify | 13 | 0 | 2 | 0.962 | 15 |
| Quick | Correct | 0 | 4 | 12 | 0.196 | 16 |
| Quick | HedgehogCBC | 0 | 4 | 12 | 0.253 | 16 |
| Quick | FalsifyCBC | 11 | 0 | 5 | 0.861 | 16 |
| Hedgehog | Falsify | 12 | 0 | 3 | 0.981 | 15 |
| Hedgehog | Correct | 0 | 3 | 13 | 0.178 | 16 |
| Hedgehog | HedgehogCBC | 0 | 3 | 13 | 0.207 | 16 |
| Hedgehog | FalsifyCBC | 11 | 0 | 5 | 0.914 | 16 |
| Falsify | Correct | 0 | 13 | 2 | 0.021 | 15 |
| Falsify | HedgehogCBC | 0 | 13 | 2 | 0.011 | 15 |
| Falsify | FalsifyCBC | 0 | 6 | 9 | 0.131 | 15 |
| Correct | HedgehogCBC | 1 | 0 | 19 | 0.690 | 20 |
| Correct | FalsifyCBC | 18 | 0 | 2 | 0.960 | 20 |
| HedgehogCBC | FalsifyCBC | 20 | 0 | 0 | 0.980 | 20 |

