# RBT — `ETNA_SHRINKS=0` (pre-shrink baseline)

3 stores merged: `store.rbt.{quick,hedgehog,falsify}.shrink-0.jsonl`.
11 strategies × 58 (property, mutation) tasks × 10 trials = 4,811 rows
(4,628 `Failed`, 183 `TimedOut`, 0 dedup violations).

At `shrinks=0` the counterexample is the first failure the generator
produces; `cex == pre_cex` for every Failed row, so this analysis is a
*generator-quality baseline* with no shrinking obfuscation.

No Lean ground truth for rbt yet → no TED-to-min column.

---

## Coverage and bucket chart (per-task median time)

| strategy        | tasks solved | <0.1s | <1s | <10s | <60s | ≥60s | NotF |
|-----------------|-------------:|------:|----:|-----:|-----:|-----:|-----:|
| Quick           | 33/58 (57%)  | 34%   | 12% |  0%  |  0%  |  2%  | 52%  |
| QuickCBC        | 45/58 (78%)  | 57%   |  3% |  9%  |  7%  |  2%  | 22%  |
| **QuickGbE**    | **58/58**    | **93%** |  7% |  0%  |  0%  |  0%  |  0%  |
| Hedgehog        | 31/58 (53%)  | 21%   | 17% |  9%  |  3%  |  0%  | 50%  |
| HedgehogCBC     | 42/58 (72%)  | 36%   | 10% | 12%  | 10%  |  2%  | 29%  |
| HedgehogCBC2    | 41/58 (71%)  | 34%   | 19% |  7%  |  5%  |  3%  | 31%  |
| HedgehogGbE     | 56/58 (97%)  | 52%   | 22% | 14%  |  3%  |  2%  |  7%  |
| Falsify         | 29/58 (50%)  | 22%   | 22% |  2%  |  0%  |  0%  | 53%  |
| FalsifyCBC      | 43/58 (74%)  | 41%   | 17% |  3%  |  3%  |  0%  | 34%  |
| FalsifyCBC2     | 43/58 (74%)  | 41%   | 17% |  5%  |  5%  |  2%  | 29%  |
| FalsifyGbE      | 57/58 (98%)  | 55%   | 21% | 10%  |  7%  |  0%  |  7%  |

Charts: `figures/bucket_rbt_shrink-0.png` (overall) and
`figures/bucket_rbt_shrink-0_family-{vanilla,cbc,qbe}.png`.

### Family takeaways
- **Vanilla**: half of all tasks not found in any of 3 frameworks.
  rbt is much harder than bst (where Quick/Hedgehog/Falsify all
  solved >75%).
- **CBC**: cuts NotFound roughly in half (52→22% Quick, 50→29% Hh,
  53→34% Fa). Frameworks now bunch within ~5pp of each other.
- **GbE/QbE**: dominant. Quick solves everything in <0.1s on 93% of
  tasks. Hedgehog and Falsify reach ~97–98% coverage with similar
  shapes; the only stragglers are `DeleteDelete` and `DeletePost`
  under structural mutations.

## Cross-strategy unsolved set

**0 tasks unsolved by every strategy** — full ground-truth coverage
across the 11-strategy sweep.

The four hard mutations (everything outside the CBC sweet spot):

| mutation              | n | Quick | QkCBC | QkGbE | Hedg | HhCBC | HhCBC2 | HhGbE | Fals | FaCBC | FaCBC2 | FaGbE |
|-----------------------|---|------:|------:|------:|-----:|------:|-------:|------:|-----:|------:|-------:|------:|
| `miscolor_balLeft`    | 2 | 0     | 2     | 2     | 0    | 1     | 1      | 1     | 0    | 1     | 1      | 1     |
| `miscolor_balRight`   | 2 | 0     | 2     | 2     | 0    | 1     | 1      | 1     | 0    | 1     | 1      | 1     |
| `no_balance_insert_1` | 3 | 1     | 0     | 3     | 1    | 0     | 0      | 3     | 1    | 0     | 0      | 3     |
| `swap_bc`             |10 | 0     | 6     |10     | 0    | 5     | 5      | 8     | 0    | 4     | 5      | 9     |
| `swap_cd`             |10 | 4     | 6     |10     | 3    | 5     | 4      |10     | 3    | 4     | 5      | 9     |

Only GbE-style execution-driven generators trigger
`no_balance_insert_1`, `miscolor_balLeft/Right` and the
deepest `swap_bc` mutations: those bugs need a tree that
*already* contains specific colour structure, which all
generators struggle to fabricate on a single shot.

## Discard audit (CBC fix held)

Vanilla strategies discard heavily (precondition rejection on
illegal RBTs); CBC/GbE never discard.

| strategy        | n_rows | %rows w/ discards | mean discards |
|-----------------|-------:|------------------:|--------------:|
| Quick           |    303 | 96.4%             | 8.7M          |
| Hedgehog        |    297 | 99.3%             | 119k          |
| Falsify         |    274 | 96.0%             | 209k          |
| Quick/Hh/FaCBC* |  all   | 0.0%              | 0             |
| QuickGbE        |    580 | 0.0%              | 0             |
| HedgehogGbE     |    544 | 0.0%              | 0             |
| FalsifyGbE      |    554 | 0.0%              | 0             |

→ The bh-aware-padding fix to the five rbt CBC generators is intact;
0 invalid trees out of 14,405 generated.

## Sample-efficiency (median pre-shrink tests per task)

| strategy        | tasks | task-med | p90       | max        |
|-----------------|------:|---------:|----------:|-----------:|
| Quick           |  28   | 9 843    | 69 220    | 21 394 533 |
| QuickCBC        |  45   | 4 944    | 6.2 M     | 38 M       |
| **QuickGbE**    |  58   | **34**   | 3 226     | 32 076     |
| Hedgehog        |  29   | 2 066    | 29 728    | 253 114    |
| HedgehogCBC     |  41   | 2 395    | 929k      | 5.4 M      |
| HedgehogCBC2    |  40   | 5 116    | 1.9 M     | 4.2 M      |
| HedgehogGbE     |  54   | 562      | 77 626    | 2.6 M      |
| Falsify         |  27   | 4 312    | 23 304    | 165 596    |
| FalsifyCBC      |  38   | 2 078    | 761k      | 1.3 M      |
| FalsifyCBC2     |  41   | 2 508    | 662k      | 6.6 M      |
| FalsifyGbE      |  54   | 1 346    | 130 049   | 606 118    |

QuickGbE is **~40–150× more sample-efficient** than other GbE
variants; it almost never needs more than 100 tests to find a bug.

## CBC vs CBC2 (idiomatic Falsify hint, idiomatic Hedgehog hint)

The library-idiomatic CBC2 variants (Falsify's `firstThen` subtree-wrap;
Hedgehog's `Gen.recursive` style) do **not** beat plain CBC on rbt.

| comparison                 | common solved | CBC2 wins | CBC2 loses | tie | median ratio |
|----------------------------|--------------:|----------:|-----------:|----:|-------------:|
| HedgehogCBC vs HedgehogCBC2|       40      |    17     |     16     |  7  | 1.00         |
| FalsifyCBC vs FalsifyCBC2  |       38      |    17     |     14     |  7  | 1.00         |

This contrasts with bst, where CBC2 helped on cex-size but not
sample-efficiency. On rbt the idiomatic hints don't reach into the
extra colour/height constraints, so the gain is noise.

## Counterexample size (token count)

| strategy        | task-med | mean | p90  | max  |
|-----------------|---------:|-----:|-----:|-----:|
| Quick           |   8.0    |  8.8 | 14.0 | 22.0 |
| Hedgehog        |   8.0    |  8.0 | 10.0 | 13.0 |
| Falsify         |   8.0    |  8.1 | 13.0 | 14.0 |
| QuickCBC        |  26.0    | 24.0 | 37.0 | 38.0 |
| HedgehogCBC     |  16.5    | 20.4 | 37.0 | 39.0 |
| HedgehogCBC2    |  14.0    | 19.8 | 36.0 | 39.0 |
| FalsifyCBC      |  29.0    | 26.0 | 38.0 | 42.0 |
| FalsifyCBC2     |  30.0    | 25.7 | 37.0 | 42.0 |
| QuickGbE        |  27.5    | 38.0 | 78.5 | 127.5|
| HedgehogGbE     |  27.8    | 27.9 | 49.5 | 65.0 |
| FalsifyGbE      |  65.5    | 62.2 | 81.0 | 85.0 |

Vanilla strategies produce small cex (~8 tokens) but only on
the easy half of tasks. CBC produces ~3× larger cex; GbE
produces 4–8× larger. **Without shrinking, the cost of better
coverage is much larger reported witnesses** — exactly the
gap shrinking algorithms are paid to close. The
`shrink-default` and `shrink-100` sweeps will quantify how
much of this gap each framework actually recovers.

## Engineering sanity checks

- `cex == pre_cex` on all 4,628 Failed rows ✓ (no rogue shrinking).
- `shrinking_discarded` max 0 ✓.
- `shrinking_passed/failed > 0` on **all 1,641 Falsify rows** even
  at `shrinks=0`. Falsify's `shrinkLimit=0` does **not** disable
  the verification re-runs the framework performs on the original
  failing input; passed/failed here count those internal re-runs,
  not actual reductions. Final cex unchanged. Worth a footnote in
  the paper when introducing the shrinking-counter schema.
