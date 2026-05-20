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
- **cex-size**  (N=48 tasks)
  - Friedman χ²=1.00, p=0.6065 → **n.s.**  | avg ranks: Quick 1.98 · Hedgehog 2.01 · Falsify 2.01
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
- **bug-finding-time-ms**  (N=48 tasks)
  - Friedman χ²=51.54, p=6.425e-12 → **REJECT**  | avg ranks: Quick 1.31 · Hedgehog 2.77 · Falsify 1.92
    - Quick vs Hedgehog: median Δ=-56.30, nonzero=48/48, r=-0.687, p=1.247e-05, p_Holm=2.495e-05 ***
    - Quick vs Falsify: median Δ=-13.63, nonzero=48/48, r=-0.803, p=1.31e-07, p_Holm=3.93e-07 ***
    - Hedgehog vs Falsify: median Δ=+16.03, nonzero=48/48, r=+0.583, p=0.0002807, p_Holm=0.0002807 ***

## BST / qbe  (QuickGbE, HedgehogGbE, FalsifyGbE)

- **ted-to-gt**  (N=53 tasks)
  - Friedman χ²=12.87, p=0.0016 → **REJECT**  | avg ranks: QuickGbE 1.85 · HedgehogGbE 2.29 · FalsifyGbE 1.86
    - QuickGbE vs HedgehogGbE: median Δ=+0.00, nonzero=25/53, r=-0.631, p=0.005601, p_Holm=0.0168 *
    - QuickGbE vs FalsifyGbE: median Δ=+0.00, nonzero=23/53, r=+0.007, p=0.9757, p_Holm=0.9757 n.s.
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.00, nonzero=30/53, r=+0.432, p=0.03797, p_Holm=0.07594 n.s.
- **cex-size**  (N=53 tasks)
  - Friedman χ²=0.11, p=0.9487 → **n.s.**  | avg ranks: QuickGbE 2.01 · HedgehogGbE 1.99 · FalsifyGbE 2.00
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
- **bug-finding-time-ms**  (N=53 tasks)
  - Friedman χ²=24.04, p=6.029e-06 → **REJECT**  | avg ranks: QuickGbE 1.57 · HedgehogGbE 2.51 · FalsifyGbE 1.92
    - QuickGbE vs HedgehogGbE: median Δ=-2.42, nonzero=53/53, r=-0.866, p=4.151e-08, p_Holm=1.245e-07 ***
    - QuickGbE vs FalsifyGbE: median Δ=-2.27, nonzero=53/53, r=-0.620, p=8.63e-05, p_Holm=0.0001726 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.14, nonzero=53/53, r=+0.052, p=0.7399, p_Holm=0.7399 n.s.

## BST / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=53 tasks)
  - Friedman χ²=54.15, p=1.743e-12 → **REJECT**  | avg ranks: QuickCBC 1.27 · HedgehogCBC 2.23 · FalsifyCBC 2.50
    - QuickCBC vs HedgehogCBC: median Δ=-5.00, nonzero=38/53, r=-0.958, p=2.596e-07, p_Holm=5.193e-07 ***
    - QuickCBC vs FalsifyCBC: median Δ=-3.00, nonzero=45/53, r=-0.979, p=1.016e-08, p_Holm=3.048e-08 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.00, nonzero=42/53, r=-0.326, p=0.06553, p_Holm=0.06553 n.s.
- **cex-size**  (N=53 tasks)
  - Friedman χ²=42.11, p=7.173e-10 → **REJECT**  | avg ranks: QuickCBC 1.44 · HedgehogCBC 2.34 · FalsifyCBC 2.22
    - QuickCBC vs HedgehogCBC: median Δ=-6.00, nonzero=33/53, r=-1.000, p=4.726e-07, p_Holm=1.418e-06 ***
    - QuickCBC vs FalsifyCBC: median Δ=+0.00, nonzero=26/53, r=-1.000, p=7.883e-06, p_Holm=1.577e-05 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.00, nonzero=31/53, r=-0.125, p=0.5393, p_Holm=0.5393 n.s.
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
- **bug-finding-time-ms**  (N=53 tasks)
  - Friedman χ²=1.85, p=0.3967 → **n.s.**  | avg ranks: QuickCBC 1.87 · HedgehogCBC 2.00 · FalsifyCBC 2.13

## RBT / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=28 tasks)
  - Friedman χ²=6.57, p=0.03753 → **REJECT**  | avg ranks: Quick 1.84 · Hedgehog 2.25 · Falsify 1.91
    - Quick vs Hedgehog: median Δ=+0.00, nonzero=12/28, r=-0.410, p=0.205, p_Holm=0.615 n.s.
    - Quick vs Falsify: median Δ=+0.00, nonzero=7/28, r=+0.036, p=0.9324, p_Holm=1 n.s.
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=12/28, r=+0.167, p=0.6066, p_Holm=1 n.s.
- **cex-size**  (N=28 tasks)
  - Friedman χ²=0.00, p=1 → **n.s.**  | avg ranks: Quick 2.00 · Hedgehog 2.00 · Falsify 2.00
- **time-shrinking-ms**  (N=28 tasks)
  - Friedman χ²=52.29, p=4.429e-12 → **REJECT**  | avg ranks: Quick 1.00 · Hedgehog 2.07 · Falsify 2.93
    - Quick vs Hedgehog: median Δ=-0.35, nonzero=28/28, r=-1.000, p=7.451e-09, p_Holm=2.235e-08 ***
    - Quick vs Falsify: median Δ=-2.85, nonzero=28/28, r=-1.000, p=7.451e-09, p_Holm=2.235e-08 ***
    - Hedgehog vs Falsify: median Δ=-2.53, nonzero=28/28, r=-0.975, p=7.451e-08, p_Holm=7.451e-08 ***
- **ms-per-edit**  (N=28 tasks)
  - Friedman χ²=46.50, p=7.992e-11 → **REJECT**  | avg ranks: Quick 1.07 · Hedgehog 2.04 · Falsify 2.89
    - Quick vs Hedgehog: median Δ=-0.15, nonzero=28/28, r=-0.995, p=1.49e-08, p_Holm=4.47e-08 ***
    - Quick vs Falsify: median Δ=-1.45, nonzero=28/28, r=-0.995, p=1.49e-08, p_Holm=4.47e-08 ***
    - Hedgehog vs Falsify: median Δ=-1.29, nonzero=28/28, r=-0.946, p=4.098e-07, p_Holm=4.098e-07 ***
- **bug-finding-time-ms**  (N=28 tasks)
  - Friedman χ²=38.79, p=3.783e-09 → **REJECT**  | avg ranks: Quick 1.32 · Hedgehog 2.93 · Falsify 1.75
    - Quick vs Hedgehog: median Δ=-173.14, nonzero=28/28, r=-0.862, p=1.105e-05, p_Holm=3.315e-05 ***
    - Quick vs Falsify: median Δ=-16.52, nonzero=28/28, r=-0.744, p=0.0002735, p_Holm=0.0002735 ***
    - Hedgehog vs Falsify: median Δ=+76.69, nonzero=28/28, r=+0.862, p=1.105e-05, p_Holm=3.315e-05 ***

## RBT / qbe  (QuickGbE, HedgehogGbE, FalsifyGbE)

- **ted-to-gt**  (N=34 tasks)
  - Friedman χ²=1.76, p=0.415 → **n.s.**  | avg ranks: QuickGbE 2.13 · HedgehogGbE 1.99 · FalsifyGbE 1.88
- **cex-size**  (N=56 tasks)
  - Friedman χ²=13.50, p=0.001171 → **REJECT**  | avg ranks: QuickGbE 2.08 · HedgehogGbE 1.76 · FalsifyGbE 2.16
    - QuickGbE vs HedgehogGbE: median Δ=+0.00, nonzero=16/56, r=+0.412, p=0.1457, p_Holm=0.1457 n.s.
    - QuickGbE vs FalsifyGbE: median Δ=+0.00, nonzero=23/56, r=-0.435, p=0.06639, p_Holm=0.1328 n.s.
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.00, nonzero=19/56, r=-0.895, p=0.0005814, p_Holm=0.001744 **
- **time-shrinking-ms**  (N=56 tasks)
  - Friedman χ²=110.04, p=1.277e-24 → **REJECT**  | avg ranks: QuickGbE 1.00 · HedgehogGbE 2.02 · FalsifyGbE 2.98
    - QuickGbE vs HedgehogGbE: median Δ=-1.44, nonzero=56/56, r=-1.000, p=7.547e-11, p_Holm=2.264e-10 ***
    - QuickGbE vs FalsifyGbE: median Δ=-48.86, nonzero=56/56, r=-1.000, p=7.547e-11, p_Holm=2.264e-10 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-47.94, nonzero=56/56, r=-0.990, p=1.163e-10, p_Holm=2.264e-10 ***
- **ms-per-edit**  (N=34 tasks)
  - Friedman χ²=25.94, p=2.328e-06 → **REJECT**  | avg ranks: QuickGbE 1.29 · HedgehogGbE 2.44 · FalsifyGbE 2.26
    - QuickGbE vs HedgehogGbE: median Δ=-0.11, nonzero=34/34, r=-0.990, p=5.821e-10, p_Holm=1.746e-09 ***
    - QuickGbE vs FalsifyGbE: median Δ=-0.03, nonzero=34/34, r=-0.711, p=0.0001379, p_Holm=0.0002758 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=-0.01, nonzero=34/34, r=-0.176, p=0.3787, p_Holm=0.3787 n.s.
- **bug-finding-time-ms**  (N=56 tasks)
  - Friedman χ²=54.32, p=1.6e-12 → **REJECT**  | avg ranks: QuickGbE 1.30 · HedgehogGbE 2.70 · FalsifyGbE 2.00
    - QuickGbE vs HedgehogGbE: median Δ=-32.25, nonzero=56/56, r=-0.975, p=2.207e-10, p_Holm=6.62e-10 ***
    - QuickGbE vs FalsifyGbE: median Δ=-42.58, nonzero=56/56, r=-0.845, p=3.844e-08, p_Holm=7.688e-08 ***
    - HedgehogGbE vs FalsifyGbE: median Δ=+0.31, nonzero=56/56, r=+0.289, p=0.05953, p_Holm=0.05953 n.s.

## RBT / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=30 tasks)
  - Friedman χ²=21.38, p=2.272e-05 → **REJECT**  | avg ranks: QuickCBC 1.45 · HedgehogCBC 2.07 · FalsifyCBC 2.48
    - QuickCBC vs HedgehogCBC: median Δ=-0.50, nonzero=20/30, r=-0.567, p=0.02546, p_Holm=0.03774 *
    - QuickCBC vs FalsifyCBC: median Δ=-1.50, nonzero=23/30, r=-0.797, p=0.0007837, p_Holm=0.002351 **
    - HedgehogCBC vs FalsifyCBC: median Δ=-1.00, nonzero=22/30, r=-0.569, p=0.01887, p_Holm=0.03774 *
- **cex-size**  (N=42 tasks)
  - Friedman χ²=9.69, p=0.007882 → **REJECT**  | avg ranks: QuickCBC 1.79 · HedgehogCBC 2.08 · FalsifyCBC 2.13
    - QuickCBC vs HedgehogCBC: median Δ=+0.00, nonzero=13/42, r=-0.549, p=0.07784, p_Holm=0.1557 n.s.
    - QuickCBC vs FalsifyCBC: median Δ=+0.00, nonzero=11/42, r=-0.818, p=0.01491, p_Holm=0.04474 *
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.00, nonzero=12/42, r=-0.154, p=0.6326, p_Holm=0.6326 n.s.
- **time-shrinking-ms**  (N=42 tasks)
  - Friedman χ²=34.48, p=3.263e-08 → **REJECT**  | avg ranks: QuickCBC 1.48 · HedgehogCBC 1.81 · FalsifyCBC 2.71
    - QuickCBC vs HedgehogCBC: median Δ=-0.35, nonzero=42/42, r=+0.115, p=0.5156, p_Holm=0.5156 n.s.
    - QuickCBC vs FalsifyCBC: median Δ=-5.04, nonzero=42/42, r=-0.945, p=4.111e-10, p_Holm=1.233e-09 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-4.99, nonzero=42/42, r=-0.876, p=2.92e-08, p_Holm=5.84e-08 ***
- **ms-per-edit**  (N=30 tasks)
  - Friedman χ²=39.47, p=2.691e-09 → **REJECT**  | avg ranks: QuickCBC 1.07 · HedgehogCBC 2.53 · FalsifyCBC 2.40
    - QuickCBC vs HedgehogCBC: median Δ=-0.17, nonzero=30/30, r=-0.884, p=2.349e-06, p_Holm=4.698e-06 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.10, nonzero=30/30, r=-0.987, p=9.313e-09, p_Holm=2.794e-08 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.05, nonzero=30/30, r=-0.265, p=0.2129, p_Holm=0.2129 n.s.
- **bug-finding-time-ms**  (N=42 tasks)
  - Friedman χ²=54.14, p=1.75e-12 → **REJECT**  | avg ranks: QuickCBC 1.31 · HedgehogCBC 2.88 · FalsifyCBC 1.81
    - QuickCBC vs HedgehogCBC: median Δ=-60.12, nonzero=42/42, r=-0.984, p=8.64e-12, p_Holm=2.592e-11 ***
    - QuickCBC vs FalsifyCBC: median Δ=-26.04, nonzero=42/42, r=-0.878, p=2.601e-08, p_Holm=2.601e-08 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+42.64, nonzero=42/42, r=+0.938, p=6.744e-10, p_Holm=1.349e-09 ***

## STLC / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=16 tasks)
  - Friedman χ²=14.47, p=0.0007193 → **REJECT**  | avg ranks: Quick 1.31 · Hedgehog 2.59 · Falsify 2.09
    - Quick vs Hedgehog: median Δ=-2.50, nonzero=16/16, r=-0.779, p=0.005797, p_Holm=0.01739 *
    - Quick vs Falsify: median Δ=-1.00, nonzero=14/16, r=-0.562, p=0.0585, p_Holm=0.117 n.s.
    - Hedgehog vs Falsify: median Δ=+1.00, nonzero=13/16, r=+0.538, p=0.08619, p_Holm=0.117 n.s.
- **cex-size**  (N=16 tasks)
  - Friedman χ²=8.15, p=0.01699 → **REJECT**  | avg ranks: Quick 1.56 · Hedgehog 2.34 · Falsify 2.09
    - Quick vs Hedgehog: median Δ=-2.00, nonzero=11/16, r=-0.879, p=0.007949, p_Holm=0.02385 *
    - Quick vs Falsify: median Δ=+0.00, nonzero=7/16, r=-0.786, p=0.05367, p_Holm=0.1073 n.s.
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=10/16, r=+0.527, p=0.1332, p_Holm=0.1332 n.s.
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
- **bug-finding-time-ms**  (N=16 tasks)
  - Friedman χ²=1.62, p=0.4437 → **n.s.**  | avg ranks: Quick 2.06 · Hedgehog 2.19 · Falsify 1.75

## STLC / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=20 tasks)
  - Friedman χ²=14.66, p=0.0006562 → **REJECT**  | avg ranks: QuickCBC 2.05 · HedgehogCBC 2.58 · FalsifyCBC 1.38
    - QuickCBC vs HedgehogCBC: median Δ=-4.50, nonzero=20/20, r=+0.000, p=1, p_Holm=1 n.s.
    - QuickCBC vs FalsifyCBC: median Δ=+5.00, nonzero=20/20, r=+0.543, p=0.03322, p_Holm=0.06643 n.s.
    - HedgehogCBC vs FalsifyCBC: median Δ=+7.75, nonzero=19/20, r=+1.000, p=0.000131, p_Holm=0.000393 ***
- **cex-size**  (N=20 tasks)
  - Friedman χ²=14.71, p=0.0006392 → **REJECT**  | avg ranks: QuickCBC 2.08 · HedgehogCBC 2.55 · FalsifyCBC 1.38
    - QuickCBC vs HedgehogCBC: median Δ=-4.25, nonzero=19/20, r=+0.011, p=0.9679, p_Holm=0.9679 n.s.
    - QuickCBC vs FalsifyCBC: median Δ=+5.75, nonzero=18/20, r=+0.614, p=0.02218, p_Holm=0.04437 *
    - HedgehogCBC vs FalsifyCBC: median Δ=+7.75, nonzero=19/20, r=+1.000, p=0.0001308, p_Holm=0.0003924 ***
- **time-shrinking-ms**  (N=20 tasks)
  - Friedman χ²=40.00, p=2.061e-09 → **REJECT**  | avg ranks: QuickCBC 1.00 · HedgehogCBC 2.00 · FalsifyCBC 3.00
    - QuickCBC vs HedgehogCBC: median Δ=-0.65, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - QuickCBC vs FalsifyCBC: median Δ=-6.50, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-5.88, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
- **ms-per-edit**  (N=20 tasks)
  - Friedman χ²=36.40, p=1.247e-08 → **REJECT**  | avg ranks: QuickCBC 1.10 · HedgehogCBC 1.90 · FalsifyCBC 3.00
    - QuickCBC vs HedgehogCBC: median Δ=-0.01, nonzero=20/20, r=-0.952, p=1.907e-05, p_Holm=1.907e-05 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.32, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.30, nonzero=20/20, r=-1.000, p=1.907e-06, p_Holm=5.722e-06 ***
- **bug-finding-time-ms**  (N=20 tasks)
  - Friedman χ²=24.10, p=5.845e-06 → **REJECT**  | avg ranks: QuickCBC 1.20 · HedgehogCBC 2.75 · FalsifyCBC 2.05
    - QuickCBC vs HedgehogCBC: median Δ=-4.09, nonzero=20/20, r=-0.990, p=3.815e-06, p_Holm=1.144e-05 ***
    - QuickCBC vs FalsifyCBC: median Δ=-1.46, nonzero=20/20, r=-0.943, p=2.67e-05, p_Holm=5.341e-05 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.88, nonzero=20/20, r=+0.419, p=0.1054, p_Holm=0.1054 n.s.

## FSUB / vanilla  (Quick, Hedgehog, Falsify)

- **ted-to-gt**  (N=26 tasks)
  - Friedman χ²=12.45, p=0.001977 → **REJECT**  | avg ranks: Quick 1.50 · Hedgehog 2.33 · Falsify 2.17
    - Quick vs Hedgehog: median Δ=-2.50, nonzero=21/26, r=-0.883, p=0.0003839, p_Holm=0.001152 **
    - Quick vs Falsify: median Δ=-2.25, nonzero=21/26, r=-0.814, p=0.001068, p_Holm=0.002136 **
    - Hedgehog vs Falsify: median Δ=+0.00, nonzero=20/26, r=+0.448, p=0.07869, p_Holm=0.07869 n.s.
- **cex-size**  (N=26 tasks)
  - Friedman χ²=29.51, p=3.901e-07 → **REJECT**  | avg ranks: Quick 1.35 · Hedgehog 2.62 · Falsify 2.04
    - Quick vs Hedgehog: median Δ=-3.00, nonzero=21/26, r=-0.957, p=0.0001088, p_Holm=0.0003264 ***
    - Quick vs Falsify: median Δ=-2.25, nonzero=17/26, r=-0.941, p=0.0005241, p_Holm=0.001048 **
    - Hedgehog vs Falsify: median Δ=+0.50, nonzero=15/26, r=+0.883, p=0.002397, p_Holm=0.002397 **
- **time-shrinking-ms**  (N=26 tasks)
  - Friedman χ²=52.00, p=5.109e-12 → **REJECT**  | avg ranks: Quick 1.00 · Hedgehog 2.00 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.20, nonzero=26/26, r=-1.000, p=2.98e-08, p_Holm=8.941e-08 ***
    - Quick vs Falsify: median Δ=-2.72, nonzero=26/26, r=-1.000, p=2.98e-08, p_Holm=8.941e-08 ***
    - Hedgehog vs Falsify: median Δ=-2.47, nonzero=26/26, r=-1.000, p=2.98e-08, p_Holm=8.941e-08 ***
- **ms-per-edit**  (N=26 tasks)
  - Friedman χ²=48.31, p=3.237e-11 → **REJECT**  | avg ranks: Quick 1.08 · Hedgehog 1.92 · Falsify 3.00
    - Quick vs Hedgehog: median Δ=-0.02, nonzero=26/26, r=-0.915, p=4.083e-06, p_Holm=4.083e-06 ***
    - Quick vs Falsify: median Δ=-0.29, nonzero=26/26, r=-1.000, p=2.98e-08, p_Holm=8.941e-08 ***
    - Hedgehog vs Falsify: median Δ=-0.25, nonzero=26/26, r=-1.000, p=2.98e-08, p_Holm=8.941e-08 ***
- **bug-finding-time-ms**  (N=26 tasks)
  - Friedman χ²=46.69, p=7.259e-11 → **REJECT**  | avg ranks: Quick 1.12 · Hedgehog 3.00 · Falsify 1.88
    - Quick vs Hedgehog: median Δ=-1055.23, nonzero=26/26, r=-1.000, p=2.98e-08, p_Holm=8.941e-08 ***
    - Quick vs Falsify: median Δ=-115.35, nonzero=26/26, r=-0.886, p=1.106e-05, p_Holm=1.106e-05 ***
    - Hedgehog vs Falsify: median Δ=+776.83, nonzero=26/26, r=+1.000, p=2.98e-08, p_Holm=8.941e-08 ***

## FSUB / cbc  (QuickCBC, HedgehogCBC, FalsifyCBC)

- **ted-to-gt**  (N=36 tasks)
  - Friedman χ²=56.00, p=6.914e-13 → **REJECT**  | avg ranks: QuickCBC 1.00 · HedgehogCBC 2.67 · FalsifyCBC 2.33
    - QuickCBC vs HedgehogCBC: median Δ=-60.25, nonzero=36/36, r=-1.000, p=1.678e-07, p_Holm=5.028e-07 ***
    - QuickCBC vs FalsifyCBC: median Δ=-52.00, nonzero=36/36, r=-1.000, p=1.676e-07, p_Holm=5.028e-07 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+7.25, nonzero=36/36, r=+0.402, p=0.03525, p_Holm=0.03525 *
- **cex-size**  (N=36 tasks)
  - Friedman χ²=56.00, p=6.914e-13 → **REJECT**  | avg ranks: QuickCBC 1.00 · HedgehogCBC 2.67 · FalsifyCBC 2.33
    - QuickCBC vs HedgehogCBC: median Δ=-46.00, nonzero=36/36, r=-1.000, p=1.677e-07, p_Holm=5.017e-07 ***
    - QuickCBC vs FalsifyCBC: median Δ=-39.50, nonzero=36/36, r=-1.000, p=1.672e-07, p_Holm=5.017e-07 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=+5.25, nonzero=36/36, r=+0.395, p=0.03879, p_Holm=0.03879 *
- **time-shrinking-ms**  (N=36 tasks)
  - Friedman χ²=62.00, p=3.442e-14 → **REJECT**  | avg ranks: QuickCBC 1.00 · HedgehogCBC 2.17 · FalsifyCBC 2.83
    - QuickCBC vs HedgehogCBC: median Δ=-1.59, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - QuickCBC vs FalsifyCBC: median Δ=-21.75, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-19.73, nonzero=36/36, r=-0.919, p=3.67e-08, p_Holm=3.67e-08 ***
- **ms-per-edit**  (N=36 tasks)
  - Friedman χ²=68.22, p=1.534e-15 → **REJECT**  | avg ranks: QuickCBC 1.00 · HedgehogCBC 2.06 · FalsifyCBC 2.94
    - QuickCBC vs HedgehogCBC: median Δ=-0.02, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.20, nonzero=36/36, r=-1.000, p=2.91e-11, p_Holm=8.731e-11 ***
    - HedgehogCBC vs FalsifyCBC: median Δ=-0.18, nonzero=36/36, r=-0.955, p=3.987e-09, p_Holm=3.987e-09 ***
- **bug-finding-time-ms**  (N=36 tasks)
  - Friedman χ²=14.89, p=0.0005847 → **REJECT**  | avg ranks: QuickCBC 1.61 · HedgehogCBC 2.50 · FalsifyCBC 1.89
    - QuickCBC vs HedgehogCBC: median Δ=-2.08, nonzero=36/36, r=-0.748, p=3.05e-05, p_Holm=9.149e-05 ***
    - QuickCBC vs FalsifyCBC: median Δ=-0.68, nonzero=36/36, r=-0.592, p=0.001446, p_Holm=0.002892 **
    - HedgehogCBC vs FalsifyCBC: median Δ=+0.40, nonzero=36/36, r=+0.486, p=0.009959, p_Holm=0.009959 **

