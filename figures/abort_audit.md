# Status audit

Row counts per (workload, strategy, shrinks) split by status. **aborted** rows are runtime crashes that the Failed-only filter in the rest of the report drops; high abort rates often mean a broken generator. Top error lines per (workload, strategy) are listed below the table.

| workload | strategy | shrinks | Failed | aborted | timed_out | other | abort% |
|---|---|---:|---:|---:|---:|---:|---:|
| bst-haskell | FalsifyCBC | — | 0 | 518 | 0 | 0 | 100% |
| bst-haskell | FalsifyCBC | 0 | 20 | 0 | 0 | 0 | 0% |
| bst-haskell | FalsifyCBC | 100 | 8 | 0 | 0 | 0 | 0% |
| bst-haskell | FalsifyCBC | 1000 | 2 | 0 | 0 | 0 | 0% |
| bst-haskell | FalsifyGbE | — | 0 | 0 | 1 | 0 | 0% |
| bst-haskell | FalsifyGbE | 0 | 652 | 0 | 0 | 0 | 0% |
| bst-haskell | FalsifyGbE | 100 | 511 | 0 | 0 | 0 | 0% |
| bst-haskell | FalsifyGbE | 1000 | 519 | 0 | 0 | 0 | 0% |
| bst-haskell | HedgehogCBC | 0 | 710 | 0 | 0 | 0 | 0% |
| bst-haskell | HedgehogCBC | 100 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | HedgehogCBC | 1000 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | HedgehogGbE | 0 | 710 | 0 | 0 | 0 | 0% |
| bst-haskell | HedgehogGbE | 100 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | HedgehogGbE | 1000 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | Lean | 0 | 52 | 0 | 0 | 0 | 0% |
| bst-haskell | LeanRev | 0 | 52 | 0 | 0 | 0 | 0% |
| bst-haskell | QuickCBC | 0 | 710 | 0 | 0 | 0 | 0% |
| bst-haskell | QuickCBC | 100 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | QuickCBC | 1000 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | QuickGbE | 0 | 710 | 0 | 0 | 0 | 0% |
| bst-haskell | QuickGbE | 100 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | QuickGbE | 1000 | 520 | 0 | 0 | 0 | 0% |
| bst-haskell | Size | — | 0 | 520 | 0 | 0 | 100% |
| fsub-haskell | Correct | — | 0 | 0 | 2 | 0 | 0% |
| fsub-haskell | Correct | 0 | 360 | 0 | 0 | 0 | 0% |
| fsub-haskell | Correct | 100 | 715 | 0 | 0 | 0 | 0% |
| fsub-haskell | Correct | 1000 | 713 | 0 | 0 | 0 | 0% |
| fsub-haskell | Lean | 0 | 50 | 0 | 0 | 0 | 0% |
| fsub-haskell | LeanRev | 0 | 48 | 0 | 0 | 0 | 0% |
| fsub-haskell | QuickIndex | — | 0 | 0 | 13 | 0 | 0% |
| fsub-haskell | QuickIndex | 0 | 337 | 0 | 0 | 0 | 0% |
| fsub-haskell | QuickIndex | 100 | 673 | 0 | 0 | 0 | 0% |
| fsub-haskell | QuickIndex | 1000 | 658 | 0 | 0 | 0 | 0% |
| rbt-haskell | Correct | 0 | 1160 | 0 | 0 | 0 | 0% |
| rbt-haskell | Correct | 100 | 1160 | 0 | 0 | 0 | 0% |
| rbt-haskell | Correct | 1000 | 1160 | 0 | 0 | 0 | 0% |
| rbt-haskell | FalsifyCBC | — | 0 | 580 | 0 | 0 | 100% |
| rbt-haskell | FalsifyCBC | 0 | 15 | 0 | 0 | 0 | 0% |
| rbt-haskell | FalsifyCBC | 100 | 3 | 0 | 0 | 0 | 0% |
| rbt-haskell | FalsifyGbE | — | 0 | 0 | 10 | 0 | 0% |
| rbt-haskell | FalsifyGbE | 0 | 556 | 0 | 0 | 0 | 0% |
| rbt-haskell | FalsifyGbE | 100 | 543 | 0 | 0 | 0 | 0% |
| rbt-haskell | FalsifyGbE | 1000 | 553 | 0 | 0 | 0 | 0% |
| rbt-haskell | HedgehogCBC | — | 0 | 0 | 42 | 0 | 0% |
| rbt-haskell | HedgehogCBC | 0 | 445 | 0 | 0 | 0 | 0% |
| rbt-haskell | HedgehogCBC | 100 | 443 | 0 | 0 | 0 | 0% |
| rbt-haskell | HedgehogCBC | 1000 | 446 | 0 | 0 | 0 | 0% |
| rbt-haskell | HedgehogGbE | — | 0 | 0 | 12 | 0 | 0% |
| rbt-haskell | HedgehogGbE | 0 | 539 | 0 | 0 | 0 | 0% |
| rbt-haskell | HedgehogGbE | 100 | 558 | 0 | 0 | 0 | 0% |
| rbt-haskell | HedgehogGbE | 1000 | 542 | 0 | 0 | 0 | 0% |
| rbt-haskell | Lean | — | 0 | 0 | 2 | 0 | 0% |
| rbt-haskell | Lean | 0 | 25 | 0 | 0 | 0 | 0% |
| rbt-haskell | LeanRev | — | 0 | 0 | 2 | 0 | 0% |
| rbt-haskell | LeanRev | 0 | 25 | 0 | 0 | 0 | 0% |
| rbt-haskell | QuickCBC | — | 0 | 0 | 25 | 0 | 0% |
| rbt-haskell | QuickCBC | 0 | 506 | 0 | 0 | 0 | 0% |
| rbt-haskell | QuickCBC | 100 | 504 | 0 | 0 | 0 | 0% |
| rbt-haskell | QuickCBC | 1000 | 507 | 0 | 0 | 0 | 0% |
| stlc-haskell | Correct | 0 | 400 | 0 | 0 | 0 | 0% |
| stlc-haskell | Correct | 100 | 400 | 0 | 0 | 0 | 0% |
| stlc-haskell | Correct | 1000 | 400 | 0 | 0 | 0 | 0% |
| stlc-haskell | Lean | 0 | 20 | 0 | 0 | 0 | 0% |
| stlc-haskell | LeanRev | 0 | 20 | 0 | 0 | 0 | 0% |

## Top abort error per (workload, strategy)

- **bst-haskell × FalsifyCBC** (518 aborted): `bst: withOrigin: origin not within bounds`
- **bst-haskell × Size** (520 aborted): `bst: BSTSIZE: getEnv: does not exist (no environment variable)`
- **rbt-haskell × FalsifyCBC** (580 aborted): `rbt: withOrigin: origin not within bounds`
