# Shrinking sample-efficiency — per (workload, family, library)

Failed trials, default shrink budget. edit = reduction in TED to
ground truth (d = pre_ted_to_gt - ted_to_gt); trials with d <= 0
excluded from per-edit metrics. ms/edit = execs/edit * ms/exec.

## BST / vanilla

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| Quick | 16.58 | 0.0948 | 0.00557 | 80/13/0 | 87.6/8.6/3.8 |
| Hedgehog | 4.73 | 0.1515 | 0.02452 | 12/8/0 | 73.7/22.2/4.2 |
| Falsify | 152.10 | 0.8125 | 0.00486 | 614/24/0 | 87.2/2.8/10.0 |

## BST / qbe

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| QuickGbE | 2.56 | 0.0232 | 0.00884 | 30/7/0 | 72.9/11.3/15.8 |
| HedgehogGbE | 3.00 | 0.0554 | 0.01587 | 41/9/0 | 89.4/10.6/0.0 |
| FalsifyGbE | 8.33 | 0.0857 | 0.00924 | 982/25/0 | 98.2/1.8/0.0 |

## BST / cbc

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| QuickCBC | 1.52 | 0.0067 | 0.00454 | 108/17/0 | 77.9/7.9/14.3 |
| HedgehogCBC | 0.29 | 0.0165 | 0.05471 | 7/9/0 | 60.5/39.5/0.0 |
| FalsifyCBC | 10.76 | 0.1121 | 0.00919 | 876/24/0 | 98.3/1.7/0.0 |

## RBT / vanilla

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| Quick | 30.75 | 0.1272 | 0.00528 | 72/13/0 | 70.3/9.3/20.4 |
| Hedgehog | 12.42 | 0.2435 | 0.01837 | 9/7/6 | 55.2/21.0/23.8 |
| Falsify | 294.60 | 1.3393 | 0.00385 | 480/26/261 | 59.7/2.6/37.7 |

## RBT / qbe

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| QuickGbE | 3.50 | 0.0260 | 0.00720 | 81/16/126 | 14.9/2.6/82.5 |
| HedgehogGbE | 3.47 | 0.0904 | 0.01448 | 133/17/0 | 95.5/4.5/0.0 |
| FalsifyGbE | 10.47 | 0.0611 | 0.00575 | 3982/65/0 | 99.4/0.6/0.0 |

## RBT / cbc

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| QuickCBC | 5.52 | 0.0206 | 0.00406 | 210/20/187 | 24.5/3.2/72.3 |
| HedgehogCBC | 4.35 | 0.1747 | 0.03089 | 28/14/5 | 53.3/28.6/18.2 |
| FalsifyCBC | 34.11 | 0.1531 | 0.00457 | 741/19/0 | 98.1/1.9/0.0 |

## STLC / vanilla

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| Quick | 1.02 | 0.0302 | 0.03658 | 6/2/4 | 49.2/16.4/34.3 |
| Hedgehog | 1.35 | 0.0474 | 0.03444 | 5/1/6 | 40.0/10.9/49.2 |
| Falsify | 43.92 | 2.0010 | 0.04278 | 218/16/243 | 51.7/3.0/45.3 |

## STLC / cbc

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| Correct | 0.72 | 0.0052 | 0.00913 | 10/4/22 | 13.2/4.3/82.5 |
| HedgehogCBC | 0.21 | 0.0148 | 0.06330 | 12/5/0 | 70.9/29.1/0.0 |
| FalsifyCBC | 44.53 | 0.3392 | 0.00728 | 934/27/0 | 97.7/2.3/0.0 |

## FSUB / vanilla

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| Quick | 0.81 | 0.0131 | 0.01679 | 13/5/11 | 45.9/17.0/37.1 |
| Hedgehog | 1.78 | 0.0518 | 0.02870 | 7/2/10 | 36.8/11.8/51.4 |
| Falsify | 135.75 | 0.6632 | 0.00467 | 174/20/425 | 25.2/3.3/71.6 |

## FSUB / cbc

| library | execs/edit | ms/edit | ms/exec | med pass/fail/disc | pooled %pass/%fail/%disc |
|---|--:|--:|--:|--:|--:|
| Correct | 0.36 | 0.0029 | 0.00771 | 15/6/26 | 28.2/10.3/61.5 |
| HedgehogCBC | 0.23 | 0.0229 | 0.09619 | 9/11/0 | 44.2/55.8/0.0 |
| FalsifyCBC | 7.98 | 0.1937 | 0.02151 | 734/24/0 | 96.9/2.3/0.8 |

