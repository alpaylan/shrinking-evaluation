# Friedman + post-hoc Holm-Wilcoxon — library comparison

Per (workload, family, metric): Friedman omnibus across tasks on
per-task medians; on rejection, Holm-corrected pairwise Wilcoxon
signed-rank post-hoc. Lower is better. r = matched-pairs rank-biserial
(negative ⇒ first library better).

## BST / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=48 tasks)
  - Friedman χ²=23.89, p=6.487e-06 → **REJECT**  | avg ranks: Quick 1.72 · Hedgehog 2.39 · Falsify 1.90
    - Quick vs Hedgehog: median Δ=+0.00, nonzero=26/48, r=-0.635, p=0.00425, p_Holm=0.01275 *
    - Quick vs Falsify: median Δ=+0.00, nonzero=13/48, r=-0.308, p=0.3265, p_Holm=0.3265 n.s.
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=25/48, r=+0.563, p=0.01228, p_Holm=0.02456 *
- **time-shrinking-ms**  (N=48 tasks)
  - Friedman χ²=59.04, p=1.511e-13 → **REJECT**  | avg ranks: Quick 1.31 · Hedgehog 1.83 · Falsify 2.85
    - Quick vs Hedgehog: median Δ=-0.15, nonzero=48/48, r=-0.481, p=0.003164, p_Holm=0.003164 **
    - Quick vs Falsify: median Δ=-3.91, nonzero=48/48, r=-0.990, p=9.948e-14, p_Holm=2.984e-13 ***
    - Hedgehog vs Falsify: median Δ=-3.76, nonzero=48/48, r=-0.957, p=6.423e-12, p_Holm=1.285e-11 ***
- **ms-per-edit**  (N=48 tasks)
  - Friedman χ²=67.79, p=1.902e-15 → **REJECT**  | avg ranks: Quick 1.23 · Hedgehog 1.88 · Falsify 2.90
    - Quick vs Hedgehog: median Δ=-0.05, nonzero=48/48, r=-0.621, p=9.943e-05, p_Holm=9.943e-05 ***
    - Quick vs Falsify: median Δ=-1.05, nonzero=48/48, r=-0.973, p=1.201e-12, p_Holm=3.602e-12 ***
    - Hedgehog vs Falsify: median Δ=-0.97, nonzero=48/48, r=-0.935, p=4.691e-11, p_Holm=9.382e-11 ***

## BST / qbe  (QuickGbE, HedgehogGbE, FalsifyGbE)

- **ted-to-gt**  (N=53 tasks)
  - Friedman χ²=41.20, p=1.131e-09 → **REJECT**  | avg ranks: QuickGbE 1.80 · HedgehogGbE 2.57 · FalsifyGbE 1.63
    - QuickGbE vs HedgehogGbE: median Δ=-1.00, nonzero=35/53, r=-0.854, p=9.52e-06, p_Holm=1.904e-05 ***
    - QuickGbE vs FalsifyGbE: median Δ=+0.00, nonzero=18/53, r=+0.363, p=0.176, p_Holm=0.176 n.s.
    - HedgehogGbE vs FalsifyGbE: median Δ=+3.00, nonzero=41/53, r=+0.869, p=1.114e-06, p_Holm=3.341e-06 ***
- **time-shrinking-ms**  (N=53 tasks)
  - Friedman χ²=98.26, p=4.594e-22 → **REJECT**  | avg ranks: QuickGbE 1.02 · HedgehogGbE 2.04 · FalsifyGbE 2.94
    - QuickGbE vs HedgehogGbE: median Δ=-0.52, nonzero=53/53, r=-1.000, p=2.386e-10, p_Holm=7.159e-10 ***
    - QuickGbE vs FalsifyGbE: median Δ=-8.97, nonzero=53/53, r=-0.999, p=2.527e-10, p_Holm=7.159e-10 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-8.55, nonzero=53/53, r=-0.980, p=5.291e-10, p_Holm=7.159e-10 ***
- **ms-per-edit**  (N=52 tasks)
  - Friedman χ²=24.50, p=4.785e-06 → **REJECT**  | avg ranks: QuickGbE 1.44 · HedgehogGbE 2.33 · FalsifyGbE 2.23
    - QuickGbE vs HedgehogGbE: median Δ=-0.04, nonzero=52/52, r=-0.875, p=3.986e-08, p_Holm=1.196e-07 ***
    - QuickGbE vs FalsifyGbE: median Δ=-0.07, nonzero=52/52, r=-0.644, p=5.267e-05, p_Holm=0.0001053 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-0.04, nonzero=52/52, r=-0.293, p=0.06583, p_Holm=0.06583 n.s.

## BST / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=53 tasks)
  - Friedman χ²=52.86, p=3.318e-12 → **REJECT**  | avg ranks: QuickCBC 1.25 · HedgehogCBC 2.25 · FalsifyCBC 2.49
    - QuickCBC vs HedgehogCBC: median Δ=-4.00, nonzero=41/53, r=-0.969, p=6.411e-08, p_Holm=1.282e-07 ***
    - QuickCBC vs FalsifyCBC: median Δ=-3.00, nonzero=44/53, r=-0.977, p=1.535e-08, p_Holm=4.606e-08 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-1.00, nonzero=48/53, r=-0.224, p=0.1768, p_Holm=0.1768 n.s.
- **time-shrinking-ms**  (N=53 tasks)
  - Friedman χ²=45.17, p=1.554e-10 → **REJECT**  | avg ranks: QuickCBC 1.38 · HedgehogCBC 1.94 · FalsifyCBC 2.68
    - QuickCBC vs HedgehogCBC: median Δ=-0.16, nonzero=53/53, r=-0.604, p=0.0001288, p_Holm=0.0001288 ***
    - QuickCBC vs FalsifyCBC: median Δ=-9.37, nonzero=53/53, r=-0.943, p=2.355e-09, p_Holm=7.066e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-8.94, nonzero=53/53, r=-0.901, p=1.159e-08, p_Holm=2.319e-08 ***
- **ms-per-edit**  (N=53 tasks)
  - Friedman χ²=61.17, p=5.214e-14 → **REJECT**  | avg ranks: QuickCBC 1.17 · HedgehogCBC 2.17 · FalsifyCBC 2.66
    - QuickCBC vs HedgehogCBC: median Δ=-0.01, nonzero=53/53, r=-0.930, p=3.827e-09, p_Holm=7.653e-09 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.11, nonzero=53/53, r=-0.944, p=2.231e-09, p_Holm=6.692e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.09, nonzero=53/53, r=-0.797, p=4.406e-07, p_Holm=4.406e-07 ***

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

- **ted-to-gt**  (N=27 tasks)
  - Friedman χ²=32.93, p=7.076e-08 → **REJECT**  | avg ranks: Quick 1.33 · Hedgehog 2.80 · Falsify 1.87
    - Quick vs Hedgehog: median Δ=-5.00, nonzero=27/27, r=-0.974, p=9.584e-06, p_Holm=2.875e-05 ***
    - Quick vs Falsify: median Δ=-0.50, nonzero=17/27, r=-0.895, p=0.001165, p_Holm=0.001165 **
    - Hedgehog vs Falsify: median Δ=+3.00, nonzero=26/27, r=+0.929, p=3.343e-05, p_Holm=6.686e-05 ***
- **time-shrinking-ms**  (N=27 tasks)
  - Friedman χ²=42.74, p=5.236e-10 → **REJECT**  | avg ranks: Quick 1.30 · Hedgehog 1.70 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.10, nonzero=27/27, r=-0.709, p=0.000744, p_Holm=0.000744 ***
    - Quick vs Falsify: median Δ=-2.81, nonzero=27/27, r=-1.000, p=1.49e-08, p_Holm=4.47e-08 ***
    - Hedgehog vs Falsify: median Δ=-2.71, nonzero=27/27, r=-1.000, p=1.49e-08, p_Holm=4.47e-08 ***
- **ms-per-edit**  (N=27 tasks)
  - Friedman χ²=44.96, p=1.724e-10 → **REJECT**  | avg ranks: Quick 1.15 · Hedgehog 1.89 · Falsify 2.96
    - Quick vs Hedgehog: median Δ=-0.02, nonzero=27/27, r=-0.820, p=5.488e-05, p_Holm=5.488e-05 ***
    - Quick vs Falsify: median Δ=-0.27, nonzero=27/27, r=-1.000, p=1.49e-08, p_Holm=4.47e-08 ***
    - Hedgehog vs Falsify: median Δ=-0.23, nonzero=27/27, r=-0.995, p=2.98e-08, p_Holm=5.96e-08 ***

## FSUB / cbc  (Correct, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=36 tasks)
  - Friedman χ²=51.59, p=6.276e-12 → **REJECT**  | avg ranks: Correct 1.06 · HedgehogCBC 2.65 · FalsifyCBC 2.29
    - Correct vs HedgehogCBC: median Δ=-64.00, nonzero=36/36, r=-0.997, p=1.827e-07, p_Holm=5.48e-07 ***
    - Correct vs FalsifyCBC: median Δ=-51.00, nonzero=36/36, r=-0.994, p=1.985e-07, p_Holm=5.48e-07 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+8.50, nonzero=33/36, r=+0.504, p=0.01145, p_Holm=0.01145 *
- **time-shrinking-ms**  (N=36 tasks)
  - Friedman χ²=61.17, p=5.222e-14 → **REJECT**  | avg ranks: Correct 1.03 · HedgehogCBC 2.11 · FalsifyCBC 2.86
    - Correct vs HedgehogCBC: median Δ=-1.55, nonzero=36/36, r=-0.952, p=4.919e-09, p_Holm=9.837e-09 ***
    - Correct vs FalsifyCBC: median Δ=-21.26, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-20.91, nonzero=36/36, r=-0.910, p=5.923e-08, p_Holm=5.923e-08 ***
- **ms-per-edit**  (N=36 tasks)
  - Friedman χ²=63.39, p=1.719e-14 → **REJECT**  | avg ranks: Correct 1.00 · HedgehogCBC 2.14 · FalsifyCBC 2.86
    - Correct vs HedgehogCBC: median Δ=-0.02, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - Correct vs FalsifyCBC: median Δ=-0.20, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.18, nonzero=36/36, r=-0.898, p=1.084e-07, p_Holm=1.084e-07 ***

