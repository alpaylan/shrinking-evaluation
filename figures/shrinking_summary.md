# Counterexample size + time summary

Per (workload, strategy, ETNA_SHRINKS) cell across all (mutation, property, trial) trials. **Depth** = max paren nesting in the (post-shrink) counterexample (lower is better). **Pre depth** = depth of the *first* failing input before shrinking; **Δ** = pre − post (how much shrinking reduced the input). **Time** = wall-clock to find the counterexample. All reduced via median / p25–p75 IQR. Cohorts with no `shrinks` field (legacy runs) are shown as `legacy`.


## bst-haskell


### shrinks=0

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FalsifyCBC | 20 | 2 | 2 | 2 | 2 | +0 | 569µs | 428µs | 691µs |
| FalsifyGbE | 652 | 9 | 6 | 10 | 10 | +1 | 2.0ms | 799µs | 23.9ms |
| HedgehogCBC | 710 | 7 | 7 | 7 | 7 | +0 | 1.3ms | 966µs | 7.6ms |
| HedgehogGbE | 710 | 4 | 3 | 7 | 4 | +0 | 3.1ms | 990µs | 20.5ms |
| Lean | 52 | 3 | 3 | 4 | 3 | +0 | 1.1ms | 840µs | 1.4ms |
| LeanRev | 52 | 3 | 3 | 4 | 3 | +0 | 1.0ms | 873µs | 1.9ms |
| QuickCBC | 710 | 7 | 7 | 7 | 7 | +0 | 1.4ms | 877µs | 6.3ms |
| QuickGbE | 710 | 4 | 3 | 6 | 4 | +0 | 870µs | 780µs | 1.1ms |

### shrinks=100

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FalsifyCBC | 8 | 2 | 2 | 2 | 2 | +0 | 1.0ms | 932µs | 1.1ms |
| FalsifyGbE | 511 | 3 | 3 | 3 | 10 | +7 | 18.7ms | 4.4ms | 80.6ms |
| HedgehogCBC | 520 | 4 | 3 | 6 | 7 | +3 | 1.7ms | 1.1ms | 10.9ms |
| HedgehogGbE | 520 | 3 | 2 | 4 | 5 | +2 | 3.9ms | 1.2ms | 23.8ms |
| QuickCBC | 520 | 3 | 3 | 4 | 7 | +4 | 1.4ms | 958µs | 6.0ms |
| QuickGbE | 520 | 3 | 3 | 4 | 5 | +2 | 930µs | 838µs | 1.1ms |

### shrinks=1000

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FalsifyCBC | 2 | 2 | 2 | 2 | 2.5 | +0.5 | 2.3ms | 1.8ms | 2.8ms |
| FalsifyGbE | 519 | 3 | 3 | 3 | 10 | +7 | 21.0ms | 4.4ms | 105.4ms |
| HedgehogCBC | 520 | 4 | 3 | 6 | 7 | +3 | 2.0ms | 1.2ms | 13.5ms |
| HedgehogGbE | 520 | 3 | 2 | 4 | 5 | +2 | 4.6ms | 1.4ms | 26.7ms |
| QuickCBC | 520 | 3 | 3 | 4 | 7 | +4 | 2.0ms | 984µs | 8.6ms |
| QuickGbE | 520 | 3 | 3 | 4 | 5 | +2 | 931µs | 808µs | 1.2ms |

## fsub-haskell


### shrinks=0

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 360 | 9 | 8 | 11 | 9 | +0 | 1.6ms | 989µs | 4.1ms |
| Lean | 50 | 5 | 4 | 5 | 5 | +0 | 1.83s | 27.9ms | 2.63s |
| LeanRev | 48 | 5 | 4 | 5 | 5 | +0 | 2.84s | 9.5ms | 6.27s |
| QuickIndex | 337 | 6 | 6 | 7 | 6 | +0 | 291.1ms | 34.2ms | 8.21s |

### shrinks=100

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 715 | 7 | 5 | 10 | 10 | +3 | 1.6ms | 1.0ms | 3.8ms |
| QuickIndex | 673 | 5 | 4 | 6 | 6 | +1 | 238.2ms | 50.5ms | 6.01s |

### shrinks=1000

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 713 | 7 | 5 | 10 | 10 | +3 | 1.7ms | 1.0ms | 4.6ms |
| QuickIndex | 658 | 5 | 4 | 6 | 6 | +1 | 294.4ms | 49.0ms | 7.45s |

## rbt-haskell


### shrinks=0

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 1160 | 6 | 4 | 8 | 6 | +0 | 1.3ms | 835µs | 4.5ms |
| FalsifyCBC | 15 | 2 | 2 | 3 | 3 | +1 | 592µs | 498µs | 669µs |
| FalsifyGbE | 556 | 7 | 6 | 8 | 8 | +1 | 28.7ms | 1.2ms | 391.1ms |
| HedgehogCBC | 445 | 4 | 3 | 5 | 4 | +0 | 35.6ms | 1.3ms | 1.48s |
| HedgehogGbE | 539 | 6 | 4 | 7 | 6 | +0 | 23.8ms | 1.4ms | 470.0ms |
| Lean | 25 | 3 | 3 | 3 | 3 | +0 | 1.1ms | 873µs | 2.0ms |
| LeanRev | 25 | 3 | 3 | 3 | 3 | +0 | 954µs | 749µs | 1.1ms |
| QuickCBC | 506 | 5 | 4 | 6 | 5 | +0 | 31.1ms | 3.4ms | 1.20s |

### shrinks=100

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 1160 | 5 | 3 | 7 | 6 | +1 | 1.2ms | 815µs | 4.8ms |
| FalsifyCBC | 3 | 2 | 2 | 2.5 | 3 | +1 | 1.2ms | 991µs | 1.5ms |
| FalsifyGbE | 543 | 4 | 3 | 6 | 8 | +4 | 121.7ms | 12.8ms | 585.4ms |
| HedgehogCBC | 443 | 4 | 4 | 5 | 4 | +0 | 30.3ms | 1.3ms | 1.35s |
| HedgehogGbE | 558 | 4 | 3 | 6 | 6 | +2 | 34.7ms | 2.7ms | 529.3ms |
| QuickCBC | 504 | 4 | 3 | 6 | 5 | +1 | 29.9ms | 2.9ms | 825.5ms |

### shrinks=1000

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 1160 | 5 | 3 | 7 | 6 | +1 | 1.3ms | 832µs | 4.9ms |
| FalsifyGbE | 553 | 4 | 3 | 6 | 8 | +4 | 197.0ms | 20.0ms | 1.97s |
| HedgehogCBC | 446 | 4 | 4 | 5 | 4 | +0 | 35.3ms | 1.3ms | 1.42s |
| HedgehogGbE | 542 | 4 | 3 | 6 | 6 | +2 | 28.2ms | 2.7ms | 523.2ms |
| QuickCBC | 507 | 4 | 3 | 5.5 | 5 | +1 | 31.6ms | 2.7ms | 1.16s |

## stlc-haskell


### shrinks=0

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 400 | 11 | 8 | 15 | 11 | +0 | 1.3ms | 967µs | 2.8ms |
| Lean | 20 | 4 | 4 | 5 | 4 | +0 | 4.4ms | 1.3ms | 10.7ms |
| LeanRev | 20 | 4 | 4 | 5 | 4 | +0 | 1.1ms | 810µs | 1.2ms |

### shrinks=100

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 400 | 9 | 6 | 13 | 12 | +3 | 1.3ms | 990µs | 2.9ms |

### shrinks=1000

| strategy | n | depth med | depth p25 | depth p75 | pre depth med | Δ med | time med | time p25 | time p75 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | 400 | 9 | 6 | 13 | 11 | +2 | 1.3ms | 1.0ms | 2.7ms |

## Notes

- **Size excluded.** Size is a parameterised input-size generator (reads BSTSIZE from the environment), not a shrinker. With BSTSIZE unset every trial crashes in `getEnv` and records the exception text as a fake counterexample. Belongs in a separate input-size sweep, not in this comparison.
- **Zero-data cells (timeout-only):** bst-haskell/Correct, bst-haskell/QuickIndex, fsub-haskell/FalsifyCBC, fsub-haskell/FalsifyGbE, fsub-haskell/HedgehogCBC, fsub-haskell/HedgehogGbE, fsub-haskell/QuickCBC, fsub-haskell/QuickGbE, rbt-haskell/QuickGbE, rbt-haskell/QuickIndex, stlc-haskell/FalsifyCBC, stlc-haskell/FalsifyGbE, stlc-haskell/HedgehogCBC, stlc-haskell/HedgehogGbE, stlc-haskell/QuickCBC, stlc-haskell/QuickGbE, stlc-haskell/QuickIndex. The strategy ran but never produced a Failed result within the configured timeout, so there's nothing to score. Treat as 'failed to find any counterexample,' not 'large counterexample.'

## Shrinking effect (framework shrinkers only)

Per (workload, strategy, shrinks) cell. **Δdepth** = pre median depth − post median depth (positive means shrinking made the tree shallower). **Δlen** = pre median character length − post median length (positive means shrinking reduced the printed term). **% changed** = fraction of trials where pre ≠ post by character. *Note*: Quick/Correct currently ignore ETNA_SHRINKS — QuickCheck always shrinks until exhausted, so their pre/post is captured but the same across cohorts.

| workload | strategy | shrinks | n | depth med (pre→post) | Δdepth | len med (pre→post) | Δlen | % changed |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| bst-haskell | QuickCBC | shrinks=0 | 710 | 7→7 | +0 | 332.5→332.5 | +0 | 0% |
| bst-haskell | QuickCBC | shrinks=100 | 520 | 7→3 | +4 | 357→33 | +324 | 100% |
| bst-haskell | QuickCBC | shrinks=1000 | 520 | 7→3 | +4 | 366→32 | +334 | 100% |
| bst-haskell | QuickGbE | shrinks=0 | 710 | 4→4 | +0 | 53→53 | +0 | 0% |
| bst-haskell | QuickGbE | shrinks=100 | 520 | 5→3 | +2 | 63→30 | +33 | 94% |
| bst-haskell | QuickGbE | shrinks=1000 | 520 | 5→3 | +2 | 65→29 | +36 | 96% |
| bst-haskell | HedgehogCBC | shrinks=0 | 710 | 7→7 | +0 | 185.5→185.5 | +0 | 0% |
| bst-haskell | HedgehogCBC | shrinks=100 | 520 | 7→4 | +3 | 195→40 | +155 | 99% |
| bst-haskell | HedgehogCBC | shrinks=1000 | 520 | 7→4 | +3 | 189→43.5 | +145.5 | 100% |
| bst-haskell | HedgehogGbE | shrinks=0 | 710 | 4→4 | +0 | 67→67 | +0 | 0% |
| bst-haskell | HedgehogGbE | shrinks=100 | 520 | 5→3 | +2 | 78→27 | +51 | 99% |
| bst-haskell | HedgehogGbE | shrinks=1000 | 520 | 5→3 | +2 | 76→27.5 | +48.5 | 99% |
| bst-haskell | FalsifyCBC | shrinks=0 | 20 | 2→2 | +0 | 23→19 | +4 | 80% |
| bst-haskell | FalsifyCBC | shrinks=100 | 8 | 2→2 | +0 | 19.5→11 | +8.5 | 100% |
| bst-haskell | FalsifyCBC | shrinks=1000 | 2 | 2.5→2 | +0.5 | 28.5→12 | +16.5 | 100% |
| bst-haskell | FalsifyGbE | shrinks=0 | 652 | 10→9 | +1 | 449→280 | +169 | 90% |
| bst-haskell | FalsifyGbE | shrinks=100 | 511 | 10→3 | +7 | 479→29 | +450 | 100% |
| bst-haskell | FalsifyGbE | shrinks=1000 | 519 | 10→3 | +7 | 477→29 | +448 | 100% |
| rbt-haskell | QuickCBC | shrinks=0 | 506 | 5→5 | +0 | 116→116 | +0 | 0% |
| rbt-haskell | QuickCBC | shrinks=100 | 504 | 5→4 | +1 | 115→67.5 | +47.5 | 99% |
| rbt-haskell | QuickCBC | shrinks=1000 | 507 | 5→4 | +1 | 114→58 | +56 | 100% |
| rbt-haskell | HedgehogCBC | shrinks=0 | 445 | 4→4 | +0 | 65→65 | +0 | 0% |
| rbt-haskell | HedgehogCBC | shrinks=100 | 443 | 4→4 | +0 | 65→60 | +5 | 95% |
| rbt-haskell | HedgehogCBC | shrinks=1000 | 446 | 4→4 | +0 | 65.5→60 | +5.5 | 96% |
| rbt-haskell | HedgehogGbE | shrinks=0 | 539 | 6→6 | +0 | 158→158 | +0 | 0% |
| rbt-haskell | HedgehogGbE | shrinks=100 | 558 | 6→4 | +2 | 157.5→47 | +110.5 | 100% |
| rbt-haskell | HedgehogGbE | shrinks=1000 | 542 | 6→4 | +2 | 158→45 | +113 | 99% |
| rbt-haskell | FalsifyCBC | shrinks=0 | 15 | 3→2 | +1 | 31→21 | +10 | 47% |
| rbt-haskell | FalsifyCBC | shrinks=100 | 3 | 3→2 | +1 | 37→11 | +26 | 100% |
| rbt-haskell | FalsifyGbE | shrinks=0 | 556 | 8→7 | +1 | 455.5→320.5 | +135 | 73% |
| rbt-haskell | FalsifyGbE | shrinks=100 | 543 | 8→4 | +4 | 458→60 | +398 | 100% |
| rbt-haskell | FalsifyGbE | shrinks=1000 | 553 | 8→4 | +4 | 436→60 | +376 | 100% |

## Phase timing breakdown

Per (workload, strategy, shrinks) cell. **exec** = time inside the user's property body. **non-exec** = wall-clock minus exec — covers input generation, framework bookkeeping, and (for shrinking) the shrink-algorithm itself. **pre** = before first observed failure; **shrink** = from first failure to final reported counterexample. **total** = pre + shrink. **overhead** = `time` − total (small harness gap; should be near zero). Median across trials. Cells missing the timing fields render as `—`.


### bst-haskell

| strategy | shrinks | n | exec pre | non-exec pre | exec shrink | non-exec shrink | total | overhead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FalsifyCBC | shrinks=0 | 20 | 53µs | 34µs | 16µs | 82µs | 184µs | 385µs |
| FalsifyGbE | shrinks=0 | 652 | 775µs | 45µs | 81µs | 216µs | 1.1ms | 881µs |
| HedgehogCBC | shrinks=0 | 710 | 11µs | 429µs | 0µs | 351µs | 791µs | 510µs |
| HedgehogGbE | shrinks=0 | 710 | 99µs | 2.0ms | 0µs | 334µs | 2.4ms | 603µs |
| Lean | shrinks=0 | 52 | 21µs | 701µs | 0µs | 0µs | 723µs | 386µs |
| LeanRev | shrinks=0 | 52 | 24µs | 602µs | 0µs | 0µs | 626µs | 399µs |
| QuickCBC | shrinks=0 | 710 | 259µs | 359µs | 0µs | 278µs | 896µs | 526µs |
| QuickGbE | shrinks=0 | 710 | 28µs | 254µs | 0µs | 224µs | 506µs | 364µs |
| FalsifyCBC | shrinks=100 | 8 | 42µs | 24µs | 427µs | 167µs | 659µs | 347µs |
| FalsifyGbE | shrinks=100 | 511 | 1.4ms | 35µs | 7.1ms | 1.3ms | 9.9ms | 8.8ms |
| HedgehogCBC | shrinks=100 | 520 | 10µs | 381µs | 10µs | 776µs | 1.2ms | 532µs |
| HedgehogGbE | shrinks=100 | 520 | 73µs | 1.7ms | 23µs | 814µs | 2.6ms | 1.3ms |
| QuickCBC | shrinks=100 | 520 | 265µs | 273µs | 62µs | 361µs | 960µs | 449µs |
| QuickGbE | shrinks=100 | 520 | 27µs | 236µs | 24µs | 276µs | 563µs | 367µs |
| FalsifyCBC | shrinks=1000 | 2 | 206µs | 135µs | 1.0ms | 420µs | 1.8ms | 522µs |
| FalsifyGbE | shrinks=1000 | 519 | 1.7ms | 41µs | 8.4ms | 1.5ms | 11.6ms | 9.4ms |
| HedgehogCBC | shrinks=1000 | 520 | 12µs | 458µs | 12µs | 823µs | 1.3ms | 728µs |
| HedgehogGbE | shrinks=1000 | 520 | 84µs | 1.9ms | 25µs | 873µs | 2.9ms | 1.7ms |
| QuickCBC | shrinks=1000 | 520 | 294µs | 303µs | 117µs | 415µs | 1.1ms | 885µs |
| QuickGbE | shrinks=1000 | 520 | 28µs | 250µs | 24µs | 263µs | 565µs | 366µs |

### fsub-haskell

| strategy | shrinks | n | exec pre | non-exec pre | exec shrink | non-exec shrink | total | overhead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | shrinks=0 | 360 | 622µs | 366µs | 0µs | 258µs | 1.2ms | 364µs |
| Lean | shrinks=0 | 50 | 130.6ms | 1.70s | 0µs | 0µs | 1.83s | 445µs |
| LeanRev | shrinks=0 | 48 | 346.4ms | 2.49s | 0µs | 0µs | 2.84s | 225µs |
| QuickIndex | shrinks=0 | 337 | 148.7ms | 141.7ms | 0µs | 455µs | 290.9ms | 192µs |
| Correct | shrinks=100 | 715 | 484µs | 362µs | 0µs | 297µs | 1.1ms | 423µs |
| QuickIndex | shrinks=100 | 673 | 120.7ms | 116.8ms | 2µs | 418µs | 237.9ms | 244µs |
| Correct | shrinks=1000 | 713 | 573µs | 410µs | 0µs | 317µs | 1.3ms | 416µs |
| QuickIndex | shrinks=1000 | 658 | 143.0ms | 151.1ms | 4µs | 422µs | 294.5ms | -88µs |

### rbt-haskell

| strategy | shrinks | n | exec pre | non-exec pre | exec shrink | non-exec shrink | total | overhead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | shrinks=0 | 1160 | 196µs | 398µs | 0µs | 235µs | 829µs | 460µs |
| FalsifyCBC | shrinks=0 | 15 | 16µs | 76µs | 10µs | 84µs | 186µs | 406µs |
| FalsifyGbE | shrinks=0 | 556 | 4.5ms | 23.6ms | 22µs | 364µs | 28.5ms | 295µs |
| HedgehogCBC | shrinks=0 | 445 | 503µs | 34.4ms | 0µs | 322µs | 35.2ms | 341µs |
| HedgehogGbE | shrinks=0 | 539 | 659µs | 22.4ms | 0µs | 339µs | 23.4ms | 446µs |
| Lean | shrinks=0 | 25 | 31µs | 783µs | 0µs | 0µs | 814µs | 315µs |
| LeanRev | shrinks=0 | 25 | 22µs | 573µs | 0µs | 0µs | 595µs | 359µs |
| QuickCBC | shrinks=0 | 506 | 22.5ms | 8.1ms | 0µs | 304µs | 30.8ms | 261µs |
| Correct | shrinks=100 | 1160 | 215µs | 337µs | 0µs | 248µs | 800µs | 448µs |
| FalsifyCBC | shrinks=100 | 3 | 7µs | 71µs | 377µs | 371µs | 826µs | 351µs |
| FalsifyGbE | shrinks=100 | 543 | 6.1ms | 26.9ms | 8.0ms | 40.1ms | 81.2ms | 40.5ms |
| HedgehogCBC | shrinks=100 | 443 | 364µs | 29.0ms | 11µs | 689µs | 30.1ms | 208µs |
| HedgehogGbE | shrinks=100 | 558 | 669µs | 26.2ms | 48µs | 1.9ms | 28.8ms | 5.9ms |
| QuickCBC | shrinks=100 | 504 | 20.9ms | 8.4ms | 55µs | 335µs | 29.7ms | 270µs |
| Correct | shrinks=1000 | 1160 | 182µs | 370µs | 0µs | 262µs | 814µs | 440µs |
| FalsifyGbE | shrinks=1000 | 553 | 6.6ms | 27.6ms | 10.7ms | 49.2ms | 94.1ms | 103.0ms |
| HedgehogCBC | shrinks=1000 | 446 | 419µs | 33.7ms | 10µs | 694µs | 34.9ms | 458µs |
| HedgehogGbE | shrinks=1000 | 542 | 646µs | 22.8ms | 41µs | 1.7ms | 25.3ms | 3.0ms |
| QuickCBC | shrinks=1000 | 507 | 22.4ms | 8.6ms | 186µs | 592µs | 31.7ms | -184µs |

### stlc-haskell

| strategy | shrinks | n | exec pre | non-exec pre | exec shrink | non-exec shrink | total | overhead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Correct | shrinks=0 | 400 | 301µs | 353µs | 0µs | 285µs | 939µs | 357µs |
| Lean | shrinks=0 | 20 | 338µs | 3.6ms | 0µs | 0µs | 3.9ms | 470µs |
| LeanRev | shrinks=0 | 20 | 110µs | 627µs | 0µs | 0µs | 737µs | 317µs |
| Correct | shrinks=100 | 400 | 274µs | 364µs | 1µs | 294µs | 933µs | 388µs |
| Correct | shrinks=1000 | 400 | 269µs | 333µs | 1µs | 295µs | 899µs | 441µs |
