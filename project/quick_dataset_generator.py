"""
Quick 1000-sample dataset for fast ML prototyping.
Stores intermediate quantities (P11, P12, P13, Kv1, Kv2, Kv3, K_v)
so the data is also useful for feature-importance studies later.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
X_RANGE = (-100.0, 100.0)

N_SAMPLES = 1000
SEED = 42


def compute_sample(x, H, d, V):
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
    E_v = K_v * V
    return r_eq, P, Kv, K_v, E_v


def main():
    rng = np.random.default_rng(SEED)
    H = rng.uniform(*H_RANGE, N_SAMPLES)
    d = rng.uniform(*D_RANGE, N_SAMPLES)
    V = rng.uniform(*V_RANGE, N_SAMPLES)
    x = rng.uniform(*X_RANGE, N_SAMPLES)

    rows = []
    for i in range(N_SAMPLES):
        r_eq, P, Kv, K_v, E_v = compute_sample(x[i], H[i], d[i], V[i])
        rows.append({
            "x":    x[i],
            "H":    H[i],
            "d":    d[i],
            "V":    V[i],
            "r_eq": r_eq,
            "P11":  P[0, 0],
            "P12":  P[0, 1],
            "P13":  P[0, 2],
            "Kv1":  Kv[0],
            "Kv2":  Kv[1],
            "Kv3":  Kv[2],
            "K_v":  K_v,
            "E_v":  E_v,
        })

    df = pd.DataFrame(rows)

    out_csv = "quick_dataset.csv"
    df.to_csv(out_csv, index=False)
    print(f"Saved -> {out_csv}  ({len(df)} rows, {len(df.columns)} cols)")

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    print("\nBasic statistics (mean / min / max / std):")
    stats = df.describe().T[["mean", "min", "max", "std"]]
    print(stats.to_string())

    above = int((df["E_v"] > 5.0).sum())
    print(
        f"\nSamples with E_v > 5 kV/m (above WHO limit): "
        f"{above}  ({100.0 * above / len(df):.1f}%)"
    )

    os.makedirs("plots", exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.hist(df["E_v"], bins=50, color="#3a7bd5", edgecolor="black")
    plt.axvline(5.0, color="red", ls="--", lw=1.5, label="WHO limit (5 kV/m)")
    plt.xlabel("E_v (kV/m)")
    plt.ylabel("Count")
    plt.title("E_v distribution - quick 1000-sample dataset")
    plt.legend()
    plt.grid(alpha=0.4)
    plt.tight_layout()
    plt.savefig("plots/Ev_distribution.png", dpi=120)
    plt.close()
    print("Saved plot -> plots/Ev_distribution.png")


if __name__ == "__main__":
    main()
