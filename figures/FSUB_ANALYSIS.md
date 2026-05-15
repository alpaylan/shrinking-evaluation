# FSUB analysis — default shrink mode

Stores loaded:
  - `store.fsub.quick.shrink-default.jsonl` (667 rows)
  - `store.fsub.hedgehog.shrink-default.jsonl` (549 rows)
  - `store.fsub.falsify.shrink-default.jsonl` (403 rows)
Ground truth: `store.fsub.det.jsonl` — 36 (property, mutation) pairs

All stats restricted to `status == "Failed"` rows.
TED is Zhang-Shasha distance over the parens-structured cex.

## 1. Coverage

Failed rows per strategy. Expected = 10 (stlc) or 18 (fsub) mutations × 2 props × 10 trials.

| Strategy | Failed | TimedOut | total | gt-coverage |
|---|---:|---:|---:|---:|
| Quick | 299 | 8 | 307 | 299 |
| Correct | 360 | 0 | 360 | 360 |
| Hedgehog | 169 | 20 | 189 | 169 |
| HedgehogCBC | 360 | 0 | 360 | 360 |
| Falsify | 7 | 36 | 43 | 7 |
| FalsifyCBC | 360 | 0 | 360 | 360 |

## 2. Effectiveness — TED to ground-truth minimum

Lower is better. Format: **mean / median / p90 / max**.

| Strategy | TED | n |
|---|---|---:|
| Quick | 43.8 / 39.0 / 75.0 / 149.0 | 299 |
| Correct | 26.9 / 23.0 / 53.0 / 146.0 | 360 |
| Hedgehog | 7.7 / 8.0 / 13.0 / 24.0 | 169 |
| HedgehogCBC | 95.6 / 91.5 / 158.0 / 275.0 | 360 |
| Falsify | 4.6 / 4.0 / 6.0 / 6.0 | 7 |
| FalsifyCBC | 74.7 / 62.0 / 134.0 / 266.0 | 360 |

### 2a. Fraction of trials reaching TED = 0

| Strategy | TED=0 | n | % |
|---|---:|---:|---:|
| Quick | 0 | 299 | 0.0% |
| Correct | 14 | 360 | 3.9% |
| Hedgehog | 0 | 169 | 0.0% |
| HedgehogCBC | 0 | 360 | 0.0% |
| Falsify | 0 | 7 | 0.0% |
| FalsifyCBC | 0 | 360 | 0.0% |

## 3. Performance — ms spent shrinking per unit of TED reduction

`time_shrinking * 1000 / (TED(pre) − TED(post))`. Trials with no reduction excluded.

| Strategy | ms/edit (mean / med / p90 / max) | n |
|---|---|---:|
| Quick | — | 0 |
| Correct | 0.01 / 0.00 / 0.01 / 0.09 | 339 |
| Hedgehog | 0.09 / 0.05 / 0.23 / 0.54 | 141 |
| HedgehogCBC | 0.06 / 0.02 / 0.11 / 1.91 | 287 |
| Falsify | 0.56 / 0.66 / 0.94 / 0.94 | 6 |
| FalsifyCBC | 0.87 / 0.19 / 1.44 / 62.04 | 313 |

## 4. Pre vs post-shrinking counterexample size

Token count of `pre_counterexample` vs `counterexample` on Failed rows. Lower post is better.

| Strategy | mean pre | mean post | mean Δ | mean Δ % |
|---|---:|---:|---:|---:|
| Quick | 49.7 | 49.7 | 0.0 | 0.0% |
| Correct | 159.4 | 34.5 | 124.9 | 78.4% |
| Hedgehog | 27.9 | 18.8 | 9.1 | 32.5% |
| HedgehogCBC | 152.7 | 86.9 | 65.8 | 43.1% |
| Falsify | 22.0 | 16.4 | 5.6 | 25.3% |
| FalsifyCBC | 151.0 | 71.4 | 79.6 | 52.7% |

## 5. Shrink attempts (Failed rows only)

`passed` = candidate where property still held (rejected), `failed` = property
broke again (accepted as new minimum), `discarded` = precondition rejected.

| Strategy | passed | failed (accepted) | discarded | total |
|---|---:|---:|---:|---:|
| Quick | 0.0 | 0.0 | 0.0 | 0.0 |
| Correct | 18.3 | 6.7 | 39.9 | 64.9 |
| Hedgehog | 6.9 | 2.2 | 9.6 | 18.7 |
| HedgehogCBC | 9.3 | 11.8 | 0.0 | 21.1 |
| Falsify | 148.3 | 19.3 | 421.6 | 589.1 |
| FalsifyCBC | 1038.0 | 24.5 | 8.4 | 1071.0 |

## 6. Time decomposition (mean ms across Failed rows)

- execution = `exec_time_pre`
- generation = `time_pre_failure − exec_time_pre`
- shrinking = `time_shrinking`

| Strategy | execution | generation | shrinking | total |
|---|---:|---:|---:|---:|
| Quick | 56565.61 ms | 39531.02 ms | 0.49 ms | 96097.12 ms |
| Correct | 9.67 ms | 0.88 ms | 0.45 ms | 11.00 ms |
| Hedgehog | 0.79 ms | 21362.85 ms | 0.54 ms | 21364.19 ms |
| HedgehogCBC | 3.59 ms | 45.53 ms | 2.40 ms | 51.52 ms |
| Falsify | 7.89 ms | 155698.35 ms | 2.77 ms | 155709.01 ms |
| FalsifyCBC | 1.97 ms | 27.69 ms | 29.08 ms | 58.74 ms |

