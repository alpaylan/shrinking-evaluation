# FSUB analysis — default shrink mode

Stores loaded:
  - `store.fsub.quick.shrink-default.jsonl` (336 rows)
  - `store.fsub.hedgehog.shrink-default.jsonl` (189 rows)
  - `store.fsub.falsify.shrink-default.jsonl` (43 rows)
Ground truth: `store.fsub.det.jsonl` — 36 (property, mutation) pairs

All stats restricted to `status == "Failed"` rows.
TED is Zhang-Shasha distance over the parens-structured cex.

## 1. Coverage

Failed rows per strategy. Expected = 10 (stlc) or 18 (fsub) mutations × 2 props × 10 trials.

| Strategy | Failed | TimedOut | total | gt-coverage |
|---|---:|---:|---:|---:|
| Quick | 299 | 8 | 307 | 299 |
| Correct | 29 | 0 | 29 | 29 |
| Hedgehog | 169 | 20 | 189 | 169 |
| HedgehogCBC | 0 | 0 | 0 | 0 |
| Falsify | 7 | 36 | 43 | 7 |
| FalsifyCBC | 0 | 0 | 0 | 0 |

## 2. Effectiveness — TED to ground-truth minimum

Lower is better. Format: **mean / median / p90 / max**.

| Strategy | TED | n |
|---|---|---:|
| Quick | 43.8 / 39.0 / 75.0 / 149.0 | 299 |
| Correct | 23.7 / 21.0 / 53.0 / 59.0 | 29 |
| Hedgehog | 7.7 / 8.0 / 13.0 / 24.0 | 169 |
| HedgehogCBC | — | 0 |
| Falsify | 4.6 / 4.0 / 6.0 / 6.0 | 7 |
| FalsifyCBC | — | 0 |

### 2a. Fraction of trials reaching TED = 0

| Strategy | TED=0 | n | % |
|---|---:|---:|---:|
| Quick | 0 | 299 | 0.0% |
| Correct | 0 | 29 | 0.0% |
| Hedgehog | 0 | 169 | 0.0% |
| HedgehogCBC | — | 0 | — |
| Falsify | 0 | 7 | 0.0% |
| FalsifyCBC | — | 0 | — |

## 3. Performance — ms spent shrinking per unit of TED reduction

`time_shrinking * 1000 / (TED(pre) − TED(post))`. Trials with no reduction excluded.

| Strategy | ms/edit (mean / med / p90 / max) | n |
|---|---|---:|
| Quick | — | 0 |
| Correct | 0.01 / 0.00 / 0.01 / 0.02 | 26 |
| Hedgehog | 0.09 / 0.05 / 0.23 / 0.54 | 141 |
| HedgehogCBC | — | 0 |
| Falsify | 0.56 / 0.66 / 0.94 / 0.94 | 6 |
| FalsifyCBC | — | 0 |

## 4. Pre vs post-shrinking counterexample size

Token count of `pre_counterexample` vs `counterexample` on Failed rows. Lower post is better.

| Strategy | mean pre | mean post | mean Δ | mean Δ % |
|---|---:|---:|---:|---:|
| Quick | 49.7 | 49.7 | 0.0 | 0.0% |
| Correct | 129.9 | 31.8 | 98.1 | 75.5% |
| Hedgehog | 27.9 | 18.8 | 9.1 | 32.5% |
| HedgehogCBC | — | — | — | — |
| Falsify | 22.0 | 16.4 | 5.6 | 25.3% |
| FalsifyCBC | — | — | — | — |

## 5. Shrink attempts (Failed rows only)

`passed` = candidate where property still held (rejected), `failed` = property
broke again (accepted as new minimum), `discarded` = precondition rejected.

| Strategy | passed | failed (accepted) | discarded | total |
|---|---:|---:|---:|---:|
| Quick | 0.0 | 0.0 | 0.0 | 0.0 |
| Correct | 20.2 | 6.8 | 42.9 | 69.9 |
| Hedgehog | 6.9 | 2.2 | 9.6 | 18.7 |
| HedgehogCBC | — | — | — | — |
| Falsify | 148.3 | 19.3 | 421.6 | 589.1 |
| FalsifyCBC | — | — | — | — |

## 6. Time decomposition (mean ms across Failed rows)

- execution = `exec_time_pre`
- generation = `time_pre_failure − exec_time_pre`
- shrinking = `time_shrinking`

| Strategy | execution | generation | shrinking | total |
|---|---:|---:|---:|---:|
| Quick | 56565.61 ms | 39531.02 ms | 0.49 ms | 96097.12 ms |
| Correct | 5.20 ms | 0.63 ms | 0.46 ms | 6.29 ms |
| Hedgehog | 0.79 ms | 21362.85 ms | 0.54 ms | 21364.19 ms |
| HedgehogCBC | — | — | — | — |
| Falsify | 7.89 ms | 155698.35 ms | 2.77 ms | 155709.01 ms |
| FalsifyCBC | — | — | — | — |

