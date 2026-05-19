"""
Main training-set generator: 12,000 samples (>= 10k required) via
uniform random sampling across the operating envelope.

Output columns (kept lean for the ML model):
    x, H, d, V, r_eq, E_v
"""
import numpy as np
import pandas as pd

from analytical import (
    bundle_equivalent_radius,
    potential_coefficient_matrix,
    field_coefficient_K,
)

N_BUNDLE = 8
R_BUNDLE = 0.6
R_SUB = 0.02815

H_RANGE = (30.0, 50.0)
D_RANGE = (15.0, 30.0)
V_RANGE = (600.0, 800.0)
X_RANGE = (-150.0, 150.0)

N_SAMPLES = 12000
SEED = 7


def compute_E_v(x, H, d, V):
    r_eq = bundle_equivalent_radius(N_BUNDLE, R_SUB, R_BUNDLE)
    coords = [(-d, H), (0.0, H), (d, H)]
    P = potential_coefficient_matrix(coords, r_eq)
    M = np.linalg.inv(P)
    K = field_coefficient_K(x, coords)
    Kv = M.T @ K
    Kv1, Kv2, Kv3 = Kv
    K_v = np.sqrt(
        Kv1 ** 2 + Kv2 ** 2 + Kv3 ** 2
        - Kv1 * Kv2 - Kv2 * Kv3 - Kv3 * Kv1
    )
    return r_eq, K_v * V


def main():
    rng = np.random.default_rng(SEED)
    H = rng.uniform(*H_RANGE, N_SAMPLES)
    d = rng.uniform(*D_RANGE, N_SAMPLES)
    V = rng.uniform(*V_RANGE, N_SAMPLES)
    x = rng.uniform(*X_RANGE, N_SAMPLES)

    r_eq_arr = np.empty(N_SAMPLES)
    E_arr = np.empty(N_SAMPLES)
    for i in range(N_SAMPLES):
        r_eq_arr[i], E_arr[i] = compute_E_v(x[i], H[i], d[i], V[i])

    df = pd.DataFrame({
        "x":    x,
        "H":    H,
        "d":    d,
        "V":    V,
        "r_eq": r_eq_arr,
        "E_v":  E_arr,
    })

    df.to_csv("dataset.csv", index=False)
    print(f"Saved -> dataset.csv  ({len(df)} rows)")
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))
    print(f"\nE_v  min={df['E_v'].min():.4f}  "
          f"max={df['E_v'].max():.4f}  "
          f"mean={df['E_v'].mean():.4f}")


if __name__ == "__main__":
    main()
