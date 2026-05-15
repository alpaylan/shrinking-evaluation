# STLC analysis — default shrink mode

Stores loaded:
  - `store.stlc.quick.shrink-default.jsonl` (364 rows)
  - `store.stlc.hedgehog.shrink-default.jsonl` (328 rows)
  - `store.stlc.hedgehog-cbc2.shrink-default.jsonl` (200 rows)
  - `store.stlc.falsify.shrink-default.jsonl` (328 rows)
  - `store.stlc.falsify-cbc2.shrink-default.jsonl` (173 rows)
Ground truth: `store.stlc.det.jsonl` — 20 (property, mutation) pairs

All stats restricted to `status == "Failed"` rows.
TED is Zhang-Shasha distance over the parens-structured cex.

## 1. Coverage

Failed rows per strategy. Expected = 10 (stlc) or 18 (fsub) mutations × 2 props × 10 trials.

| Strategy | Failed | TimedOut | total | gt-coverage |
|---|---:|---:|---:|---:|
| Quick | 160 | 4 | 164 | 160 |
| Correct | 200 | 0 | 200 | 200 |
| Hedgehog | 160 | 4 | 164 | 160 |
| HedgehogCBC | 160 | 4 | 164 | 160 |
| HedgehogCBC2 | 200 | 0 | 200 | 200 |
| Falsify | 160 | 4 | 164 | 160 |
| FalsifyCBC | 160 | 4 | 164 | 160 |
| FalsifyCBC2 | 170 | 3 | 173 | 170 |

## 2. Effectiveness — TED to ground-truth minimum

Lower is better. Format: **mean / median / p90 / max**.

| Strategy | TED | n |
|---|---|---:|
| Quick | 4.0 / 2.0 / 13.0 / 19.0 | 160 |
| Correct | 62.4 / 19.0 / 178.0 / 919.0 | 200 |
| Hedgehog | 6.3 / 6.0 / 13.0 / 17.0 | 160 |
| HedgehogCBC | 8.5 / 9.0 / 16.0 / 51.0 | 160 |
| HedgehogCBC2 | 34.3 / 25.0 / 67.0 / 203.0 | 200 |
| Falsify | 4.8 / 5.0 / 12.0 / 32.0 | 160 |
| FalsifyCBC | 6.5 / 7.0 / 13.0 / 22.0 | 160 |
| FalsifyCBC2 | 6.1 / 6.0 / 13.0 / 17.0 | 170 |

### 2a. Fraction of trials reaching TED = 0

| Strategy | TED=0 | n | % |
|---|---:|---:|---:|
| Quick | 70 | 160 | 43.8% |
| Correct | 46 | 200 | 23.0% |
| Hedgehog | 0 | 160 | 0.0% |
| HedgehogCBC | 0 | 160 | 0.0% |
| HedgehogCBC2 | 0 | 200 | 0.0% |
| Falsify | 19 | 160 | 11.9% |
| FalsifyCBC | 6 | 160 | 3.8% |
| FalsifyCBC2 | 3 | 170 | 1.8% |

## 3. Performance — ms spent shrinking per unit of TED reduction

`time_shrinking * 1000 / (TED(pre) − TED(post))`. Trials with no reduction excluded.

| Strategy | ms/edit (mean / med / p90 / max) | n |
|---|---|---:|
| Quick | 0.09 / 0.03 / 0.29 / 0.99 | 140 |
| Correct | 0.03 / 0.00 / 0.05 / 1.09 | 176 |
| Hedgehog | 0.07 / 0.05 / 0.13 / 0.43 | 110 |
| HedgehogCBC | 0.05 / 0.02 / 0.07 / 0.71 | 120 |
| HedgehogCBC2 | 0.03 / 0.01 / 0.06 / 0.38 | 169 |
| Falsify | 5.68 / 2.11 / 13.91 / 97.12 | 116 |
| FalsifyCBC | 0.31 / 0.15 / 0.68 / 3.08 | 133 |
| FalsifyCBC2 | 1.02 / 0.50 / 2.11 / 12.37 | 118 |

## 4. Pre vs post-shrinking counterexample size

Token count of `pre_counterexample` vs `counterexample` on Failed rows. Lower post is better.

| Strategy | mean pre | mean post | mean Δ | mean Δ % |
|---|---:|---:|---:|---:|
| Quick | 33.2 | 18.0 | 15.2 | 45.7% |
| Correct | 218.7 | 78.8 | 139.9 | 64.0% |
| Hedgehog | 29.7 | 18.9 | 10.8 | 36.5% |
| HedgehogCBC | 46.2 | 22.0 | 24.3 | 52.5% |
| HedgehogCBC2 | 129.6 | 50.4 | 79.2 | 61.1% |
| Falsify | 31.0 | 19.5 | 11.5 | 37.2% |
| FalsifyCBC | 46.5 | 20.3 | 26.3 | 56.5% |
| FalsifyCBC2 | 28.6 | 18.9 | 9.7 | 34.0% |

## 5. Shrink attempts (Failed rows only)

`passed` = candidate where property still held (rejected), `failed` = property
broke again (accepted as new minimum), `discarded` = precondition rejected.

| Strategy | passed | failed (accepted) | discarded | total |
|---|---:|---:|---:|---:|
| Quick | 6.6 | 2.2 | 4.6 | 13.4 |
| Correct | 13.9 | 4.5 | 86.7 | 105.1 |
| Hedgehog | 5.4 | 1.5 | 6.6 | 13.5 |
| HedgehogCBC | 7.1 | 1.8 | 0.0 | 8.9 |
| HedgehogCBC2 | 12.9 | 5.3 | 0.0 | 18.2 |
| Falsify | 302.5 | 17.6 | 265.5 | 585.6 |
| FalsifyCBC | 670.4 | 20.5 | 0.0 | 690.9 |
| FalsifyCBC2 | 954.7 | 23.8 | 0.0 | 978.6 |

## 6. Time decomposition (mean ms across Failed rows)

- execution = `exec_time_pre`
- generation = `time_pre_failure − exec_time_pre`
- shrinking = `time_shrinking`

| Strategy | execution | generation | shrinking | total |
|---|---:|---:|---:|---:|
| Quick | 830.81 ms | 1166.21 ms | 0.47 ms | 1997.48 ms |
| Correct | 5.13 ms | 1.74 ms | 0.62 ms | 7.49 ms |
| Hedgehog | 9.02 ms | 2140.71 ms | 0.45 ms | 2150.19 ms |
| HedgehogCBC | 0.19 ms | 8.60 ms | 0.55 ms | 9.33 ms |
| HedgehogCBC2 | 1.13 ms | 51.93 ms | 1.19 ms | 54.24 ms |
| Falsify | 123.36 ms | 1345.99 ms | 36.06 ms | 1505.41 ms |
| FalsifyCBC | 2.75 ms | 0.25 ms | 4.43 ms | 7.43 ms |
| FalsifyCBC2 | 4.26 ms | 0.57 ms | 5.16 ms | 9.99 ms |

