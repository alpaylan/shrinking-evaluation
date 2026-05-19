# Friedman + post-hoc Holm-Wilcoxon — library comparison

Per (workload, family, metric): Friedman omnibus across tasks on
per-task medians; on rejection, Holm-corrected pairwise Wilcoxon
signed-rank post-hoc. Lower is better. r = matched-pairs rank-biserial
(negative ⇒ first library better).

## BST / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=48 tasks)
  - Friedman χ²=9.96, p=0.006888 → **REJECT**  | avg ranks: Quick 1.80 · Hedgehog 2.24 · Falsify 1.96
    - Quick vs Hedgehog: median Δ=+0.00, nonzero=25/48, r=-0.369, p=0.1049, p_Holm=0.3146 n.s.
    - Quick vs Falsify: median Δ=+0.00, nonzero=12/48, r=-0.372, p=0.2526, p_Holm=0.5052 n.s.
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=26/48, r=+0.199, p=0.3717, p_Holm=0.5052 n.s.
- **time-shrinking-ms**  (N=48 tasks)
  - Friedman χ²=80.79, p=2.86e-18 → **REJECT**  | avg ranks: Quick 1.06 · Hedgehog 2.04 · Falsify 2.90
    - Quick vs Hedgehog: median Δ=-0.23, nonzero=48/48, r=-0.917, p=1.984e-10, p_Holm=1.984e-10 ***
    - Quick vs Falsify: median Δ=-4.04, nonzero=48/48, r=-0.995, p=3.553e-14, p_Holm=1.066e-13 ***
    - Hedgehog vs Falsify: median Δ=-3.94, nonzero=48/48, r=-0.963, p=3.809e-12, p_Holm=7.617e-12 ***
- **ms-per-edit**  (N=48 tasks)
  - Friedman χ²=76.04, p=3.074e-17 → **REJECT**  | avg ranks: Quick 1.06 · Hedgehog 2.10 · Falsify 2.83
    - Quick vs Hedgehog: median Δ=-0.08, nonzero=48/48, r=-0.997, p=2.132e-14, p_Holm=6.395e-14 ***
    - Quick vs Falsify: median Δ=-1.25, nonzero=48/48, r=-0.986, p=1.776e-13, p_Holm=3.553e-13 ***
    - Hedgehog vs Falsify: median Δ=-1.20, nonzero=48/48, r=-0.930, p=7.075e-11, p_Holm=7.075e-11 ***

## BST / qbe  (QuickGbE, HedgehogGbE, FalsifyGbE)

- **ted-to-gt**  (N=53 tasks)
  - Friedman χ²=12.87, p=0.0016 → **REJECT**  | avg ranks: QuickGbE 1.85 · HedgehogGbE 2.29 · FalsifyGbE 1.86
    - QuickGbE vs HedgehogGbE: median Δ=+0.00, nonzero=25/53, r=-0.631, p=0.005601, p_Holm=0.0168 *
    - QuickGbE vs FalsifyGbE: median Δ=+0.00, nonzero=23/53, r=+0.007, p=0.9757, p_Holm=0.9757 n.s.
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.00, nonzero=30/53, r=+0.432, p=0.03797, p_Holm=0.07594 n.s.
- **time-shrinking-ms**  (N=53 tasks)
  - Friedman χ²=100.11, p=1.823e-22 → **REJECT**  | avg ranks: QuickGbE 1.02 · HedgehogGbE 2.02 · FalsifyGbE 2.96
    - QuickGbE vs HedgehogGbE: median Δ=-0.51, nonzero=53/53, r=-1.000, p=2.386e-10, p_Holm=7.159e-10 ***
    - QuickGbE vs FalsifyGbE: median Δ=-9.17, nonzero=53/53, r=-0.999, p=2.527e-10, p_Holm=7.159e-10 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-8.66, nonzero=53/53, r=-0.989, p=3.768e-10, p_Holm=7.159e-10 ***
- **ms-per-edit**  (N=53 tasks)
  - Friedman χ²=34.68, p=2.948e-08 → **REJECT**  | avg ranks: QuickGbE 1.34 · HedgehogGbE 2.34 · FalsifyGbE 2.32
    - QuickGbE vs HedgehogGbE: median Δ=-0.04, nonzero=53/53, r=-0.933, p=3.437e-09, p_Holm=1.031e-08 ***
    - QuickGbE vs FalsifyGbE: median Δ=-0.07, nonzero=53/53, r=-0.772, p=1.002e-06, p_Holm=2.005e-06 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-0.06, nonzero=53/53, r=-0.377, p=0.01704, p_Holm=0.01704 *

## BST / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=53 tasks)
  - Friedman χ²=54.15, p=1.743e-12 → **REJECT**  | avg ranks: QuickCBC 1.27 · HedgehogCBC 2.23 · FalsifyCBC 2.50
    - QuickCBC vs HedgehogCBC: median Δ=-5.00, nonzero=38/53, r=-0.958, p=2.596e-07, p_Holm=5.193e-07 ***
    - QuickCBC vs FalsifyCBC: median Δ=-3.00, nonzero=45/53, r=-0.979, p=1.016e-08, p_Holm=3.048e-08 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.00, nonzero=42/53, r=-0.326, p=0.06553, p_Holm=0.06553 n.s.
- **time-shrinking-ms**  (N=53 tasks)
  - Friedman χ²=81.62, p=1.889e-18 → **REJECT**  | avg ranks: QuickCBC 1.07 · HedgehogCBC 2.13 · FalsifyCBC 2.80
    - QuickCBC vs HedgehogCBC: median Δ=-0.49, nonzero=53/53, r=-0.866, p=4.151e-08, p_Holm=4.151e-08 ***
    - QuickCBC vs FalsifyCBC: median Δ=-15.62, nonzero=52/53, r=-1.000, p=3.504e-10, p_Holm=1.051e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-14.56, nonzero=53/53, r=-0.891, p=1.665e-08, p_Holm=3.33e-08 ***
- **ms-per-edit**  (N=53 tasks)
  - Friedman χ²=72.11, p=2.192e-16 → **REJECT**  | avg ranks: QuickCBC 1.08 · HedgehogCBC 2.26 · FalsifyCBC 2.66
    - QuickCBC vs HedgehogCBC: median Δ=-0.01, nonzero=53/53, r=-0.973, p=7.006e-10, p_Holm=2.102e-09 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.17, nonzero=53/53, r=-0.973, p=7.006e-10, p_Holm=2.102e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.14, nonzero=53/53, r=-0.760, p=1.498e-06, p_Holm=1.498e-06 ***

## RBT / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=27 tasks)
  - Friedman χ²=8.42, p=0.01486 → **REJECT**  | avg ranks: Quick 1.80 · Hedgehog 2.28 · Falsify 1.93
    - Quick vs Hedgehog: median Δ=+0.00, nonzero=11/27, r=-0.667, p=0.04763, p_Holm=0.1429 n.s.
    - Quick vs Falsify: median Δ=+0.00, nonzero=6/27, r=-0.190, p=0.6733, p_Holm=1 n.s.
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=12/27, r=+0.167, p=0.6066, p_Holm=1 n.s.
- **time-shrinking-ms**  (N=27 tasks)
  - Friedman χ²=50.30, p=1.198e-11 → **REJECT**  | avg ranks: Quick 1.00 · Hedgehog 2.07 · Falsify 2.93
    - Quick vs Hedgehog: median Δ=-0.35, nonzero=27/27, r=-1.000, p=1.49e-08, p_Holm=4.47e-08 ***
    - Quick vs Falsify: median Δ=-2.82, nonzero=27/27, r=-1.000, p=1.49e-08, p_Holm=4.47e-08 ***
    - Hedgehog vs Falsify: median Δ=-2.47, nonzero=27/27, r=-0.974, p=1.49e-07, p_Holm=1.49e-07 ***
- **ms-per-edit**  (N=27 tasks)
  - Friedman χ²=46.52, p=7.918e-11 → **REJECT**  | avg ranks: Quick 1.04 · Hedgehog 2.07 · Falsify 2.89
    - Quick vs Hedgehog: median Δ=-0.15, nonzero=27/27, r=-1.000, p=1.49e-08, p_Holm=4.47e-08 ***
    - Quick vs Falsify: median Δ=-1.39, nonzero=27/27, r=-0.995, p=2.98e-08, p_Holm=5.96e-08 ***
    - Hedgehog vs Falsify: median Δ=-1.21, nonzero=27/27, r=-0.942, p=8.196e-07, p_Holm=8.196e-07 ***

## RBT / qbe  (QuickGbE, HedgehogGbE, FalsifyGbE)

- **ted-to-gt**  (N=31 tasks)
  - Friedman χ²=2.23, p=0.3287 → **n.s.**  | avg ranks: QuickGbE 2.11 · HedgehogGbE 2.05 · FalsifyGbE 1.84
- **time-shrinking-ms**  (N=52 tasks)
  - Friedman χ²=102.04, p=6.96e-23 → **REJECT**  | avg ranks: QuickGbE 1.00 · HedgehogGbE 2.02 · FalsifyGbE 2.98
    - QuickGbE vs HedgehogGbE: median Δ=-1.39, nonzero=52/52, r=-1.000, p=3.504e-10, p_Holm=1.051e-09 ***
    - QuickGbE vs FalsifyGbE: median Δ=-44.22, nonzero=52/52, r=-1.000, p=3.504e-10, p_Holm=1.051e-09 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-43.02, nonzero=52/52, r=-0.988, p=5.582e-10, p_Holm=1.051e-09 ***
- **ms-per-edit**  (N=31 tasks)
  - Friedman χ²=22.65, p=1.21e-05 → **REJECT**  | avg ranks: QuickGbE 1.32 · HedgehogGbE 2.48 · FalsifyGbE 2.19
    - QuickGbE vs HedgehogGbE: median Δ=-0.08, nonzero=31/31, r=-0.988, p=4.657e-09, p_Holm=1.397e-08 ***
    - QuickGbE vs FalsifyGbE: median Δ=-0.03, nonzero=31/31, r=-0.653, p=0.0009815, p_Holm=0.001963 **
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.01, nonzero=31/31, r=-0.016, p=0.9461, p_Holm=0.9461 n.s.

## RBT / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=28 tasks)
  - Friedman χ²=18.52, p=9.527e-05 → **REJECT**  | avg ranks: QuickCBC 1.48 · HedgehogCBC 2.04 · FalsifyCBC 2.48
    - QuickCBC vs HedgehogCBC: median Δ=-0.50, nonzero=18/28, r=-0.538, p=0.04367, p_Holm=0.04367 *
    - QuickCBC vs FalsifyCBC: median Δ=-2.00, nonzero=21/28, r=-0.792, p=0.001397, p_Holm=0.00419 **
    - HedgehogCBC vs FalsifyCBC: median Δ=-1.00, nonzero=22/28, r=-0.569, p=0.01887, p_Holm=0.03774 *
- **time-shrinking-ms**  (N=39 tasks)
  - Friedman χ²=31.74, p=1.279e-07 → **REJECT**  | avg ranks: QuickCBC 1.44 · HedgehogCBC 1.87 · FalsifyCBC 2.69
    - QuickCBC vs HedgehogCBC: median Δ=-0.36, nonzero=39/39, r=-0.024, p=0.8945, p_Holm=0.8945 n.s.
    - QuickCBC vs FalsifyCBC: median Δ=-4.79, nonzero=39/39, r=-0.936, p=3.289e-09, p_Holm=9.866e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-4.50, nonzero=39/39, r=-0.856, p=2.321e-07, p_Holm=4.642e-07 ***
- **ms-per-edit**  (N=28 tasks)
  - Friedman χ²=39.93, p=2.136e-09 → **REJECT**  | avg ranks: QuickCBC 1.04 · HedgehogCBC 2.61 · FalsifyCBC 2.36
    - QuickCBC vs HedgehogCBC: median Δ=-0.17, nonzero=28/28, r=-1.000, p=7.451e-09, p_Holm=2.235e-08 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.09, nonzero=28/28, r=-0.985, p=3.725e-08, p_Holm=7.451e-08 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.06, nonzero=28/28, r=-0.158, p=0.4791, p_Holm=0.4791 n.s.

## STLC / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=16 tasks)
  - Friedman χ²=14.47, p=0.0007193 → **REJECT**  | avg ranks: Quick 1.31 · Hedgehog 2.59 · Falsify 2.09
    - Quick vs Hedgehog: median Δ=-2.50, nonzero=16/16, r=-0.779, p=0.005797, p_Holm=0.01739 *
    - Quick vs Falsify: median Δ=-1.00, nonzero=14/16, r=-0.562, p=0.0585, p_Holm=0.117 n.s.
    - Hedgehog vs Falsify: median Δ=+1.00, nonzero=13/16, r=+0.538, p=0.08619, p_Holm=0.117 n.s.
- **time-shrinking-ms**  (N=16 tasks)
  - Friedman χ²=32.00, p=1.125e-07 → **REJECT**  | avg ranks: Quick 1.00 · Hedgehog 2.00 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.26, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***
    - Quick vs Falsify: median Δ=-23.52, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***
    - Hedgehog vs Falsify: median Δ=-23.28, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***
- **ms-per-edit**  (N=16 tasks)
  - Friedman χ²=25.12, p=3.501e-06 → **REJECT**  | avg ranks: Quick 1.31 · Hedgehog 1.69 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.01, nonzero=16/16, r=-0.353, p=0.2312, p_Holm=0.2312 n.s.
    - Quick vs Falsify: median Δ=-2.13, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***
    - Hedgehog vs Falsify: median Δ=-2.06, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***

## STLC / cbc  (Correct, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=20 tasks)
  - Friedman χ²=14.66, p=0.0006562 → **REJECT**  | avg ranks: Correct 2.05 · HedgehogCBC 2.58 · FalsifyCBC 1.38
    - Correct vs HedgehogCBC: median Δ=-4.50, nonzero=20/20, r=+0.000, p=1, p_Holm=1 n.s.
    - Correct vs FalsifyCBC: median Δ=+5.00, nonzero=20/20, r=+0.543, p=0.03322, p_Holm=0.06643 n.s.
    - HedgehogCBC vs FalsifyCBC: median Δ=+7.75, nonzero=19/20, r=+1.000, p=0.000131, p_Holm=0.000393 ***
- **time-shrinking-ms**  (N=20 tasks)
  - Friedman χ²=40.00, p=2.061e-09 → **REJECT**  | avg ranks: Correct 1.00 · HedgehogCBC 2.00 · FalsifyCBC 3.00
    - Correct vs HedgehogCBC: median Δ=-0.65, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - Correct vs FalsifyCBC: median Δ=-6.50, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-5.88, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
- **ms-per-edit**  (N=20 tasks)
  - Friedman χ²=36.40, p=1.247e-08 → **REJECT**  | avg ranks: Correct 1.10 · HedgehogCBC 1.90 · FalsifyCBC 3.00
    - Correct vs HedgehogCBC: median Δ=-0.01, nonzero=20/20, r=-0.952, p=1.907e-05, p_Holm=1.907e-05 ***
    - Correct vs FalsifyCBC: median Δ=-0.32, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.30, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***

## FSUB / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**: only 0 common tasks — skipped
- **time-shrinking-ms**: only 0 common tasks — skipped
- **ms-per-edit**: only 0 common tasks — skipped

## FSUB / cbc  (Correct, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**: only 0 common tasks — skipped
- **time-shrinking-ms**: only 0 common tasks — skipped
- **ms-per-edit**: only 0 common tasks — skipped

