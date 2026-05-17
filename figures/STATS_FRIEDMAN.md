# Friedman + post-hoc Holm-Wilcoxon — library comparison

Per (workload, family, metric): Friedman omnibus across tasks on
per-task medians; on rejection, Holm-corrected pairwise Wilcoxon
signed-rank post-hoc. Lower is better. r = matched-pairs rank-biserial
(negative ⇒ first library better).

## BST / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=47 tasks)
  - Friedman χ²=23.89, p=6.487e-06 → **REJECT**  | avg ranks: Quick 1.71 · Hedgehog 2.39 · Falsify 1.89
    - Quick vs Hedgehog: median Δ=+0.00, nonzero=26/47, r=-0.635, p=0.00425, p_Holm=0.01275 *
    - Quick vs Falsify: median Δ=+0.00, nonzero=13/47, r=-0.308, p=0.3265, p_Holm=0.3265 n.s.
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=25/47, r=+0.563, p=0.01228, p_Holm=0.02456 *
- **time-shrinking-ms**  (N=47 tasks)
  - Friedman χ²=62.43, p=2.783e-14 → **REJECT**  | avg ranks: Quick 1.30 · Hedgehog 1.81 · Falsify 2.89
    - Quick vs Hedgehog: median Δ=-0.15, nonzero=47/47, r=-0.472, p=0.004268, p_Holm=0.004268 **
    - Quick vs Falsify: median Δ=-4.14, nonzero=47/47, r=-0.995, p=7.105e-14, p_Holm=2.132e-13 ***
    - Hedgehog vs Falsify: median Δ=-4.00, nonzero=47/47, r=-0.970, p=2.942e-12, p_Holm=5.883e-12 ***
- **ms-per-edit**  (N=47 tasks)
  - Friedman χ²=71.36, p=3.192e-16 → **REJECT**  | avg ranks: Quick 1.21 · Hedgehog 1.85 · Falsify 2.94
    - Quick vs Hedgehog: median Δ=-0.05, nonzero=47/47, r=-0.619, p=0.0001246, p_Holm=0.0001246 ***
    - Quick vs Falsify: median Δ=-1.24, nonzero=47/47, r=-0.975, p=1.563e-12, p_Holm=4.69e-12 ***
    - Hedgehog vs Falsify: median Δ=-1.09, nonzero=47/47, r=-0.941, p=4.566e-11, p_Holm=9.132e-11 ***

## BST / qbe  (QuickGbE, HedgehogGbE, FalsifyGbE)

- **ted-to-gt**  (N=52 tasks)
  - Friedman χ²=39.45, p=2.707e-09 → **REJECT**  | avg ranks: QuickGbE 1.81 · HedgehogGbE 2.56 · FalsifyGbE 1.63
    - QuickGbE vs HedgehogGbE: median Δ=-1.00, nonzero=34/52, r=-0.845, p=1.57e-05, p_Holm=3.141e-05 ***
    - QuickGbE vs FalsifyGbE: median Δ=+0.00, nonzero=18/52, r=+0.363, p=0.176, p_Holm=0.176 n.s.
    - HedgehogGbE vs FalsifyGbE: median Δ=+2.75, nonzero=40/52, r=+0.862, p=1.819e-06, p_Holm=5.457e-06 ***
- **time-shrinking-ms**  (N=52 tasks)
  - Friedman χ²=102.04, p=6.96e-23 → **REJECT**  | avg ranks: QuickGbE 1.00 · HedgehogGbE 2.02 · FalsifyGbE 2.98
    - QuickGbE vs HedgehogGbE: median Δ=-0.52, nonzero=52/52, r=-1.000, p=3.504e-10, p_Holm=1.051e-09 ***
    - QuickGbE vs FalsifyGbE: median Δ=-9.50, nonzero=52/52, r=-1.000, p=3.504e-10, p_Holm=1.051e-09 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-8.81, nonzero=52/52, r=-0.990, p=5.268e-10, p_Holm=1.051e-09 ***
- **ms-per-edit**  (N=52 tasks)
  - Friedman χ²=24.50, p=4.785e-06 → **REJECT**  | avg ranks: QuickGbE 1.44 · HedgehogGbE 2.33 · FalsifyGbE 2.23
    - QuickGbE vs HedgehogGbE: median Δ=-0.04, nonzero=52/52, r=-0.875, p=3.986e-08, p_Holm=1.196e-07 ***
    - QuickGbE vs FalsifyGbE: median Δ=-0.07, nonzero=52/52, r=-0.644, p=5.267e-05, p_Holm=0.0001053 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-0.04, nonzero=52/52, r=-0.293, p=0.06583, p_Holm=0.06583 n.s.

## BST / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=52 tasks)
  - Friedman χ²=52.04, p=4.997e-12 → **REJECT**  | avg ranks: QuickCBC 1.25 · HedgehogCBC 2.27 · FalsifyCBC 2.48
    - QuickCBC vs HedgehogCBC: median Δ=-4.00, nonzero=41/52, r=-0.969, p=6.411e-08, p_Holm=1.282e-07 ***
    - QuickCBC vs FalsifyCBC: median Δ=-3.25, nonzero=43/52, r=-0.978, p=2.142e-08, p_Holm=6.427e-08 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.75, nonzero=47/52, r=-0.216, p=0.1961, p_Holm=0.1961 n.s.
- **time-shrinking-ms**  (N=52 tasks)
  - Friedman χ²=47.58, p=4.664e-11 → **REJECT**  | avg ranks: QuickCBC 1.37 · HedgehogCBC 1.92 · FalsifyCBC 2.71
    - QuickCBC vs HedgehogCBC: median Δ=-0.17, nonzero=52/52, r=-0.598, p=0.0001754, p_Holm=0.0001754 ***
    - QuickCBC vs FalsifyCBC: median Δ=-9.65, nonzero=52/52, r=-0.954, p=2.187e-09, p_Holm=6.562e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-9.38, nonzero=52/52, r=-0.913, p=1.015e-08, p_Holm=2.029e-08 ***
- **ms-per-edit**  (N=52 tasks)
  - Friedman χ²=63.38, p=1.723e-14 → **REJECT**  | avg ranks: QuickCBC 1.15 · HedgehogCBC 2.15 · FalsifyCBC 2.69
    - QuickCBC vs HedgehogCBC: median Δ=-0.01, nonzero=52/52, r=-0.927, p=5.909e-09, p_Holm=1.182e-08 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.11, nonzero=52/52, r=-0.958, p=1.849e-09, p_Holm=5.546e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.10, nonzero=52/52, r=-0.816, p=3.086e-07, p_Holm=3.086e-07 ***

## RBT / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=29 tasks)
  - Friedman χ²=11.29, p=0.003538 → **REJECT**  | avg ranks: Quick 1.79 · Hedgehog 2.36 · Falsify 1.84
    - Quick vs Hedgehog: median Δ=-0.50, nonzero=18/29, r=-0.690, p=0.009096, p_Holm=0.02729 *
    - Quick vs Falsify: median Δ=+0.00, nonzero=6/29, r=-0.238, p=0.5982, p_Holm=0.5982 n.s.
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=17/29, r=+0.490, p=0.07157, p_Holm=0.1431 n.s.
- **time-shrinking-ms**  (N=30 tasks)
  - Friedman χ²=48.07, p=3.651e-11 → **REJECT**  | avg ranks: Quick 1.20 · Hedgehog 1.83 · Falsify 2.97
    - Quick vs Hedgehog: median Δ=-0.13, nonzero=30/30, r=-0.785, p=5.593e-05, p_Holm=5.593e-05 ***
    - Quick vs Falsify: median Δ=-2.66, nonzero=30/30, r=-1.000, p=1.863e-09, p_Holm=5.588e-09 ***
    - Hedgehog vs Falsify: median Δ=-2.65, nonzero=30/30, r=-0.978, p=1.863e-08, p_Holm=3.725e-08 ***
- **ms-per-edit**  (N=29 tasks)
  - Friedman χ²=48.48, p=2.966e-11 → **REJECT**  | avg ranks: Quick 1.10 · Hedgehog 1.97 · Falsify 2.93
    - Quick vs Hedgehog: median Δ=-0.07, nonzero=29/29, r=-0.880, p=3.982e-06, p_Holm=3.982e-06 ***
    - Quick vs Falsify: median Δ=-1.36, nonzero=29/29, r=-0.977, p=3.725e-08, p_Holm=1.118e-07 ***
    - Hedgehog vs Falsify: median Δ=-1.35, nonzero=29/29, r=-0.949, p=2.049e-07, p_Holm=4.098e-07 ***

## RBT / qbe  (QuickGbE, HedgehogGbE, FalsifyGbE)

- **ted-to-gt**  (N=34 tasks)
  - Friedman χ²=11.09, p=0.003909 → **REJECT**  | avg ranks: QuickGbE 1.90 · HedgehogGbE 2.37 · FalsifyGbE 1.74
    - QuickGbE vs HedgehogGbE: median Δ=-0.50, nonzero=26/34, r=-0.219, p=0.3274, p_Holm=0.3274 n.s.
    - QuickGbE vs FalsifyGbE: median Δ=+0.00, nonzero=15/34, r=+0.583, p=0.04634, p_Holm=0.09268 n.s.
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.50, nonzero=23/34, r=+0.649, p=0.006406, p_Holm=0.01922 *
- **time-shrinking-ms**  (N=54 tasks)
  - Friedman χ²=104.04, p=2.562e-23 → **REJECT**  | avg ranks: QuickGbE 1.02 · HedgehogGbE 2.00 · FalsifyGbE 2.98
    - QuickGbE vs HedgehogGbE: median Δ=-1.05, nonzero=54/54, r=-0.999, p=1.72e-10, p_Holm=4.877e-10 ***
    - QuickGbE vs FalsifyGbE: median Δ=-46.71, nonzero=54/54, r=-1.000, p=1.626e-10, p_Holm=4.877e-10 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-45.66, nonzero=54/54, r=-0.989, p=2.545e-10, p_Holm=4.877e-10 ***
- **ms-per-edit**  (N=31 tasks)
  - Friedman χ²=16.26, p=0.0002949 → **REJECT**  | avg ranks: QuickGbE 1.42 · HedgehogGbE 2.39 · FalsifyGbE 2.19
    - QuickGbE vs HedgehogGbE: median Δ=-0.05, nonzero=31/31, r=-0.944, p=1.024e-07, p_Holm=3.073e-07 ***
    - QuickGbE vs FalsifyGbE: median Δ=-0.03, nonzero=31/31, r=-0.665, p=0.000764, p_Holm=0.001528 **
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.00, nonzero=31/31, r=-0.282, p=0.1757, p_Holm=0.1757 n.s.

## RBT / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=30 tasks)
  - Friedman χ²=21.30, p=2.367e-05 → **REJECT**  | avg ranks: QuickCBC 1.43 · HedgehogCBC 2.17 · FalsifyCBC 2.40
    - QuickCBC vs HedgehogCBC: median Δ=-0.50, nonzero=18/30, r=-0.924, p=0.0005472, p_Holm=0.001094 **
    - QuickCBC vs FalsifyCBC: median Δ=-1.50, nonzero=20/30, r=-0.924, p=0.0002699, p_Holm=0.0008097 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.50, nonzero=24/30, r=-0.200, p=0.3892, p_Holm=0.3892 n.s.
- **time-shrinking-ms**  (N=40 tasks)
  - Friedman χ²=28.55, p=6.316e-07 → **REJECT**  | avg ranks: QuickCBC 1.48 · HedgehogCBC 1.88 · FalsifyCBC 2.65
    - QuickCBC vs HedgehogCBC: median Δ=-0.17, nonzero=40/40, r=-0.151, p=0.4125, p_Holm=0.4125 n.s.
    - QuickCBC vs FalsifyCBC: median Δ=-4.99, nonzero=40/40, r=-0.932, p=2.698e-09, p_Holm=8.093e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-4.05, nonzero=40/40, r=-0.880, p=5.064e-08, p_Holm=1.013e-07 ***
- **ms-per-edit**  (N=30 tasks)
  - Friedman χ²=22.07, p=1.615e-05 → **REJECT**  | avg ranks: QuickCBC 1.30 · HedgehogCBC 2.37 · FalsifyCBC 2.33
    - QuickCBC vs HedgehogCBC: median Δ=-0.13, nonzero=30/30, r=-0.703, p=0.0004184, p_Holm=0.0008368 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.09, nonzero=30/30, r=-0.897, p=1.419e-06, p_Holm=4.258e-06 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.01, nonzero=30/30, r=-0.363, p=0.08407, p_Holm=0.08407 n.s.

## STLC / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=16 tasks)
  - Friedman χ²=10.10, p=0.00642 → **REJECT**  | avg ranks: Quick 1.41 · Hedgehog 2.50 · Falsify 2.09
    - Quick vs Hedgehog: median Δ=-4.50, nonzero=15/16, r=-0.700, p=0.01675, p_Holm=0.05024 n.s.
    - Quick vs Falsify: median Δ=-1.00, nonzero=16/16, r=-0.500, p=0.07688, p_Holm=0.0991 n.s.
    - Hedgehog vs Falsify: median Δ=+2.00, nonzero=15/16, r=+0.575, p=0.04955, p_Holm=0.0991 n.s.
- **time-shrinking-ms**  (N=16 tasks)
  - Friedman χ²=30.12, p=2.874e-07 → **REJECT**  | avg ranks: Quick 1.94 · Hedgehog 1.06 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=+0.07, nonzero=16/16, r=+0.779, p=0.004181, p_Holm=0.004181 **
    - Quick vs Falsify: median Δ=-23.21, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***
    - Hedgehog vs Falsify: median Δ=-23.27, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***
- **ms-per-edit**  (N=16 tasks)
  - Friedman χ²=24.00, p=6.144e-06 → **REJECT**  | avg ranks: Quick 1.50 · Hedgehog 1.50 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.00, nonzero=16/16, r=+0.029, p=0.9399, p_Holm=0.9399 n.s.
    - Quick vs Falsify: median Δ=-2.09, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***
    - Hedgehog vs Falsify: median Δ=-2.04, nonzero=16/16, r=-1.000, p=3.052e-05, p_Holm=9.155e-05 ***

## STLC / cbc  (Correct, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=20 tasks)
  - Friedman χ²=16.95, p=0.0002088 → **REJECT**  | avg ranks: Correct 2.23 · HedgehogCBC 2.50 · FalsifyCBC 1.27
    - Correct vs HedgehogCBC: median Δ=-1.75, nonzero=19/20, r=-0.016, p=0.9519, p_Holm=0.9519 n.s.
    - Correct vs FalsifyCBC: median Δ=+14.50, nonzero=20/20, r=+0.786, p=0.002061, p_Holm=0.004122 **
    - HedgehogCBC vs FalsifyCBC: median Δ=+14.00, nonzero=19/20, r=+1.000, p=0.0001314, p_Holm=0.0003943 ***
- **time-shrinking-ms**  (N=20 tasks)
  - Friedman χ²=40.00, p=2.061e-09 → **REJECT**  | avg ranks: Correct 1.00 · HedgehogCBC 2.00 · FalsifyCBC 3.00
    - Correct vs HedgehogCBC: median Δ=-0.66, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - Correct vs FalsifyCBC: median Δ=-6.30, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-5.84, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
- **ms-per-edit**  (N=20 tasks)
  - Friedman χ²=33.60, p=5.057e-08 → **REJECT**  | avg ranks: Correct 1.20 · HedgehogCBC 1.80 · FalsifyCBC 3.00
    - Correct vs HedgehogCBC: median Δ=-0.01, nonzero=20/20, r=-0.819, p=0.0005856, p_Holm=0.0005856 ***
    - Correct vs FalsifyCBC: median Δ=-0.31, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.31, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***

## FSUB / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=4 tasks)
  - Friedman χ²=2.80, p=0.2466 → **n.s.**  | avg ranks: Quick 2.12 · Hedgehog 2.50 · Falsify 1.38
- **time-shrinking-ms**  (N=4 tasks)
  - Friedman χ²=6.00, p=0.04979 → **REJECT**  | avg ranks: Quick 1.50 · Hedgehog 1.50 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.06, nonzero=4/4, r=-0.400, p=0.625, p_Holm=0.625 n.s.
    - Quick vs Falsify: median Δ=-2.49, nonzero=4/4, r=-1.000, p=0.125, p_Holm=0.375 n.s.
    - Hedgehog vs Falsify: median Δ=-2.41, nonzero=4/4, r=-1.000, p=0.125, p_Holm=0.375 n.s.
- **ms-per-edit**  (N=3 tasks)
  - Friedman χ²=6.00, p=0.04979 → **REJECT**  | avg ranks: Quick 1.00 · Hedgehog 2.00 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.05, nonzero=3/3, r=-1.000, p=0.25, p_Holm=0.75 n.s.
    - Quick vs Falsify: median Δ=-0.74, nonzero=3/3, r=-1.000, p=0.25, p_Holm=0.75 n.s.
    - Hedgehog vs Falsify: median Δ=-0.68, nonzero=3/3, r=-1.000, p=0.25, p_Holm=0.75 n.s.

## FSUB / cbc  (Correct, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=36 tasks)
  - Friedman χ²=54.31, p=1.608e-12 → **REJECT**  | avg ranks: Correct 1.06 · HedgehogCBC 2.74 · FalsifyCBC 2.21
    - Correct vs HedgehogCBC: median Δ=-71.00, nonzero=36/36, r=-1.000, p=1.678e-07, p_Holm=5.034e-07 ***
    - Correct vs FalsifyCBC: median Δ=-45.25, nonzero=36/36, r=-0.991, p=2.162e-07, p_Holm=5.034e-07 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+22.25, nonzero=33/36, r=+0.736, p=0.0002243, p_Holm=0.0002243 ***
- **time-shrinking-ms**  (N=36 tasks)
  - Friedman χ²=56.17, p=6.362e-13 → **REJECT**  | avg ranks: Correct 1.06 · HedgehogCBC 2.14 · FalsifyCBC 2.81
    - Correct vs HedgehogCBC: median Δ=-1.68, nonzero=36/36, r=-0.988, p=2.037e-10, p_Holm=4.075e-10 ***
    - Correct vs FalsifyCBC: median Δ=-13.32, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-12.19, nonzero=36/36, r=-0.877, p=2.893e-07, p_Holm=2.893e-07 ***
- **ms-per-edit**  (N=36 tasks)
  - Friedman χ²=60.72, p=6.521e-14 → **REJECT**  | avg ranks: Correct 1.00 · HedgehogCBC 2.19 · FalsifyCBC 2.81
    - Correct vs HedgehogCBC: median Δ=-0.02, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - Correct vs FalsifyCBC: median Δ=-0.19, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.16, nonzero=36/36, r=-0.895, p=1.254e-07, p_Holm=1.254e-07 ***

