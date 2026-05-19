"""
Train ANN, Random Forest, and SVR on the generated dataset,
report RMSE / MAE / R^2 for each, and save the best one as
best_model.pkl together with the feature ordering metadata.
"""
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


FEATURES = ["x", "H", "d", "V", "r_eq"]
TARGET = "E_v"


def evaluate(name, y_true, y_pred):
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    print(f"{name:18s}  RMSE={rmse:.4f}   MAE={mae:.4f}   R^2={r2:.5f}")
    return {"name": name, "rmse": rmse, "mae": mae, "r2": r2}


def main(csv_path="dataset.csv"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"{csv_path} not found - run dataset_generator.py first."
        )
    df = pd.read_csv(csv_path)
    X = df[FEATURES].values
    y = df[TARGET].values

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "ANN (MLP)": Pipeline([
            ("scaler", StandardScaler()),
            ("mlp", MLPRegressor(
                hidden_layer_sizes=(32, 16),
                activation="relu",
                solver="adam",
                alpha=1.0,
                max_iter=200,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=10,
                random_state=42,
            )),
        ]),
        "Random Forest": RandomForestRegressor(
            n_estimators=80, min_samples_leaf=10,
            max_depth=12, random_state=42, n_jobs=-1,
        ),
        "SVR (RBF)": Pipeline([
            ("scaler", StandardScaler()),
            ("svr", SVR(kernel="rbf", C=5.0, gamma="scale", epsilon=0.1)),
        ]),
    }

    results = []
    fitted = {}
    for name, model in models.items():
        print(f"Training {name} ...")
        model.fit(X_tr, y_tr)
        preds = model.predict(X_te)
        results.append(evaluate(name, y_te, preds))
        fitted[name] = (model, preds)

    best = max(results, key=lambda r: r["r2"])
    best_name = best["name"]
    best_model, best_preds = fitted[best_name]
    print(f"\nBest model: {best_name}  (R^2 = {best['r2']:.5f})")

    joblib.dump(
        {"model": best_model, "name": best_name, "features": FEATURES},
        "best_model.pkl",
    )
    print("Saved best_model.pkl")

    os.makedirs("plots", exist_ok=True)
    plt.figure(figsize=(7, 7))
    plt.scatter(y_te, best_preds, s=8, alpha=0.4)
    lo = float(min(y_te.min(), best_preds.min()))
    hi = float(max(y_te.max(), best_preds.max()))
    plt.plot([lo, hi], [lo, hi], "r--", lw=1.5, label="y = x")
    plt.xlabel("Actual E_v (kV/m)")
    plt.ylabel("Predicted E_v (kV/m)")
    plt.title(f"{best_name}  -  RMSE={best['rmse']:.4f}  R^2={best['r2']:.4f}")
    plt.legend()
    plt.grid(alpha=0.4)
    plt.tight_layout()
    plt.savefig("plots/predicted_vs_actual.png", dpi=120)
    plt.close()
    print("Saved plot -> plots/predicted_vs_actual.png")


if __name__ == "__main__":
    main()
