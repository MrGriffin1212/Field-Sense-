"""
Flask web application for UHV AC line E-field prediction.
Exposes the ML model and analytical engine through a web interface.
"""
import os
import json
import joblib
import numpy as np

from flask import Flask, render_template, request, jsonify

from analytical import (
    bundle_equivalent_radius,
    potential_coefficient_matrix,
    electric_field_at_ground,
    line_to_ground_rms,
)

# ── constants (same as predict.py) ──────────────────────────────────
N_BUNDLE = 8
R_BUNDLE = 0.6
R_SUB    = 0.02815
MODEL_PATH = "best_model.pkl"

app = Flask(__name__)

# ── load model once at startup ──────────────────────────────────────
bundle   = joblib.load(MODEL_PATH)
ml_model = bundle["model"]
ml_name  = bundle["name"]
ml_feats = bundle["features"]


def _predict(x, H, d, V):
    """Return dict with ML prediction, analytical prediction, and profile."""
    r_eq = bundle_equivalent_radius(N_BUNDLE, R_SUB, R_BUNDLE)

    # ── ML prediction ───────────────────────────────────────────────
    row = {"x": x, "H": H, "d": d, "V": V, "r_eq": r_eq}
    X = np.array([[row[f] for f in ml_feats]])
    E_ml = float(ml_model.predict(X)[0])

    # ── Analytical prediction ───────────────────────────────────────
    coords = [(-d, H), (0.0, H), (d, H)]
    P = potential_coefficient_matrix(coords, r_eq)
    M = np.linalg.inv(P)
    E_an = float(electric_field_at_ground(x, coords, M, V))

    # ── Lateral profile (for chart) ─────────────────────────────────
    xs = np.linspace(-150.0, 150.0, 301)
    profile_an = []
    profile_ml = []
    feat_lookup = {
        "x":    xs,
        "H":    np.full_like(xs, H),
        "d":    np.full_like(xs, d),
        "V":    np.full_like(xs, V),
        "r_eq": np.full_like(xs, r_eq),
    }
    X_profile = np.column_stack([feat_lookup[f] for f in ml_feats])
    ml_preds = ml_model.predict(X_profile)

    for i, xi in enumerate(xs):
        e_an = float(electric_field_at_ground(xi, coords, M, V))
        profile_an.append(round(e_an, 5))
        profile_ml.append(round(float(ml_preds[i]), 5))

    return {
        "ml_name":    ml_name,
        "E_ml":       round(E_ml, 5),
        "E_an":       round(E_an, 5),
        "r_eq":       round(r_eq, 6),
        "who_limit":  5.0,
        "safe_ml":    E_ml <= 5.0,
        "safe_an":    E_an <= 5.0,
        "profile_x":  [round(float(v), 2) for v in xs],
        "profile_an": profile_an,
        "profile_ml": profile_ml,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        x = float(data["x"])
        H = float(data["H"])
        d = float(data["d"])
        V = float(data["V"])
        result = _predict(x, H, d, V)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
