"""
Plot analytical vs ML-predicted ground-level E_v profile for the
1200 kV case study, with RMSE and R^2 annotated on the figure.
"""
import os
import joblib
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error, r2_score

from analytical import (
    bundle_equivalent_radius,
    potential_coefficient_matrix,
    electric_field_at_ground,
    line_to_ground_rms,
)

N_BUNDLE = 8
R_BUNDLE = 0.6
R_SUB = 0.02815

H = 37.0
d = 24.0
V_LL = 1200.0
V_PH = line_to_ground_rms(V_LL)


def main():
    bundle = joblib.load("best_model.pkl")
    model = bundle["model"]
    features = bundle["features"]
    model_name = bundle["name"]

    r_eq = bundle_equivalent_radius(N_BUNDLE, R_SUB, R_BUNDLE)
    coords = [(-d, H), (0.0, H), (d, H)]
    P = potential_coefficient_matrix(coords, r_eq)
    M = np.linalg.inv(P)

    xs = np.linspace(-100.0, 100.0, 401)
    E_an = np.array(
        [electric_field_at_ground(xi, coords, M, V_PH) for xi in xs]
    )

    feat_lookup = {
        "x":    xs,
        "H":    np.full_like(xs, H),
        "d":    np.full_like(xs, d),
        "V":    np.full_like(xs, V_PH),
        "r_eq": np.full_like(xs, r_eq),
    }
    X = np.column_stack([feat_lookup[f] for f in features])
    E_ml = model.predict(X)

    rmse = float(np.sqrt(mean_squared_error(E_an, E_ml)))
    r2 = float(r2_score(E_an, E_ml))

    os.makedirs("plots", exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(xs, E_an, "b-",  lw=2.0, label="Analytical (ground truth)")
    plt.plot(xs, E_ml, "r--", lw=2.0, label=f"ML - {model_name}")
    plt.xlabel("Lateral distance x (m)")
    plt.ylabel("E_v (kV/m)")
    plt.title("1200 kV case study - Analytical vs ML prediction")
    plt.text(
        0.02, 0.95,
        f"RMSE = {rmse:.4f} kV/m\nR^2  = {r2:.5f}",
        transform=plt.gca().transAxes, va="top", ha="left",
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="gray"),
    )
    plt.legend()
    plt.grid(alpha=0.4)
    plt.tight_layout()
    plt.savefig("plots/comparison.png", dpi=120)
    plt.close()

    print(f"RMSE (analytical vs ML): {rmse:.6f} kV/m")
    print(f"R^2                    : {r2:.6f}")
    print("Saved plot -> plots/comparison.png")


if __name__ == "__main__":
    main()
