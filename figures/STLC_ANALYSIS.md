# STLC analysis — default shrink mode

Stores loaded:
  - `store.stlc.quick.shrink-default.jsonl` (364 rows)
  - `store.stlc.hedgehog.shrink-default.jsonl` (364 rows)
  - `store.stlc.falsify.shrink-default.jsonl` (364 rows)
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
| HedgehogCBC | 200 | 0 | 200 | 200 |
| Falsify | 160 | 4 | 164 | 160 |
| FalsifyCBC | 200 | 0 | 200 | 200 |

## 2. Effectiveness — TED to ground-truth minimum

Lower is better. Format: **mean / median / p90 / max**.

| Strategy | TED | n |
|---|---|---:|
| Quick | 4.0 / 2.0 / 13.0 / 19.0 | 160 |
| Correct | 62.4 / 19.0 / 178.0 / 919.0 | 200 |
| Hedgehog | 6.3 / 6.0 / 13.0 / 17.0 | 160 |
| HedgehogCBC | 32.1 / 24.5 / 71.0 / 183.0 | 200 |
| Falsify | 4.8 / 5.0 / 12.0 / 32.0 | 160 |
| FalsifyCBC | 10.1 / 9.0 / 23.0 / 37.0 | 200 |

### 2a. Fraction of trials reaching TED = 0

| Strategy | TED=0 | n | % |
|---|---:|---:|---:|
| Quick | 70 | 160 | 43.8% |
| Correct | 46 | 200 | 23.0% |
| Hedgehog | 0 | 160 | 0.0% |
| HedgehogCBC | 0 | 200 | 0.0% |
| Falsify | 19 | 160 | 11.9% |
| FalsifyCBC | 15 | 200 | 7.5% |

## 3. Performance — ms spent shrinking per unit of TED reduction

`time_shrinking * 1000 / (TED(pre) − TED(post))`. Trials with no reduction excluded.

| Strategy | ms/edit (mean / med / p90 / max) | n |
|---|---|---:|
| Quick | 0.09 / 0.03 / 0.29 / 0.99 | 140 |
| Correct | 0.03 / 0.00 / 0.05 / 1.09 | 176 |
| Hedgehog | 0.07 / 0.05 / 0.13 / 0.43 | 110 |
| HedgehogCBC | 0.03 / 0.01 / 0.06 / 0.49 | 177 |
| Falsify | 5.68 / 2.11 / 13.91 / 97.12 | 116 |
| FalsifyCBC | 0.63 / 0.34 / 1.15 / 9.77 | 153 |

## 4. Pre vs post-shrinking counterexample size

Token count of `pre_counterexample` vs `counterexample` on Failed rows. Lower post is better.

| Strategy | mean pre | mean post | mean Δ | mean Δ % |
|---|---:|---:|---:|---:|
| Quick | 33.2 | 18.0 | 15.2 | 45.7% |
| Correct | 218.7 | 78.8 | 139.9 | 64.0% |
| Hedgehog | 29.7 | 18.9 | 10.8 | 36.5% |
| HedgehogCBC | 135.6 | 48.4 | 87.2 | 64.3% |
| Falsify | 31.0 | 19.5 | 11.5 | 37.2% |
| FalsifyCBC | 48.1 | 25.8 | 22.3 | 46.4% |

## 5. Shrink attempts (Failed rows only)

`passed` = candidate where property still held (rejected), `failed` = property
broke again (accepted as new minimum), `discarded` = precondition rejected.

| Strategy | passed | failed (accepted) | discarded | total |
|---|---:|---:|---:|---:|
| Quick | 6.6 | 2.2 | 4.6 | 13.4 |
| Correct | 13.9 | 4.5 | 86.7 | 105.1 |
| Hedgehog | 5.4 | 1.5 | 6.6 | 13.5 |
| HedgehogCBC | 12.7 | 5.2 | 0.0 | 17.9 |
| Falsify | 302.5 | 17.6 | 265.5 | 585.6 |
| FalsifyCBC | 1227.3 | 28.4 | 0.0 | 1255.7 |

## 6. Time decomposition (mean ms across Failed rows)

- execution = `exec_time_pre`
- generation = `time_pre_failure − exec_time_pre`
- shrinking = `time_shrinking`

| Strategy | execution | generation | shrinking | total |
|---|---:|---:|---:|---:|
| Quick | 830.81 ms | 1166.21 ms | 0.47 ms | 1997.48 ms |
| Correct | 5.13 ms | 1.74 ms | 0.62 ms | 7.49 ms |
| Hedgehog | 9.02 ms | 2140.71 ms | 0.45 ms | 2150.19 ms |
| HedgehogCBC | 1.16 ms | 53.44 ms | 1.30 ms | 55.90 ms |
| Falsify | 123.36 ms | 1345.99 ms | 36.06 ms | 1505.41 ms |
| FalsifyCBC | 91.87 ms | 7.97 ms | 11.25 ms | 111.09 ms |

