"""
Interactive prediction interface for the trained regression model.

Usage:
    python predict.py                       # interactive prompts
    python predict.py <x> <H> <d> <V_phase> # one-shot CLI mode
"""
import sys
import joblib
import numpy as np

from analytical import bundle_equivalent_radius

N_BUNDLE = 8
R_BUNDLE = 0.6
R_SUB = 0.02815

MODEL_PATH = "best_model.pkl"


def load_model(path=MODEL_PATH):
    bundle = joblib.load(path)
    return bundle["model"], bundle["name"], bundle["features"]


def predict_E(model, features, x, H, d, V):
    r_eq = bundle_equivalent_radius(N_BUNDLE, R_SUB, R_BUNDLE)
    row = {"x": x, "H": H, "d": d, "V": V, "r_eq": r_eq}
    X = np.array([[row[f] for f in features]])
    return float(model.predict(X)[0]), r_eq


def _ask(prompt, default):
    raw = input(f"{prompt} [default {default}]: ").strip()
    return float(raw) if raw else float(default)


def _show(model_name, x, H, d, V, r_eq, E_pred):
    print()
    print("-" * 60)
    print(f" Model         : {model_name}")
    print(f" x (lateral)   : {x:>10.3f} m")
    print(f" H (height)    : {H:>10.3f} m")
    print(f" d (spacing)   : {d:>10.3f} m")
    print(f" V (phase rms) : {V:>10.3f} kV")
    print(f" r_eq          : {r_eq:>10.6f} m")
    print("-" * 60)
    print(f" Predicted E_v : {E_pred:.4f} kV/m")
    flag = "  ABOVE WHO 5 kV/m limit" if E_pred > 5.0 else "  within WHO limit"
    print(f"                {flag}")
    print("-" * 60)


def run_cli():
    x, H, d, V = (float(a) for a in sys.argv[1:5])
    model, name, features = load_model()
    E, r_eq = predict_E(model, features, x, H, d, V)
    _show(name, x, H, d, V, r_eq, E)


def run_interactive():
    model, name, features = load_model()
    print("=" * 60)
    print(" UHV AC line  -  E_v prediction (ML regression) ")
    print("=" * 60)
    print(f" Loaded model: {name}")
    print(" Training ranges:  H 30-50 m   d 15-30 m   "
          "V 600-800 kV   x -150..150 m")
    print(" Press Ctrl+C (or just Enter at x) to quit.\n")

    defaults = {"x": 0.0, "H": 37.0, "d": 24.0,
                "V": round(1200.0 / np.sqrt(3.0), 4)}

    while True:
        try:
            raw = input(f"x (m) [default {defaults['x']}, blank to quit]: ").strip()
            if raw == "":
                print("Bye.")
                return
            x = float(raw)
            H = _ask("H (m)",   defaults["H"])
            d = _ask("d (m)",   defaults["d"])
            V = _ask("V (kV)",  defaults["V"])
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            return
        except ValueError:
            print("  ! Invalid number, try again.\n")
            continue

        E, r_eq = predict_E(model, features, x, H, d, V)
        _show(name, x, H, d, V, r_eq, E)

        defaults.update({"x": x, "H": H, "d": d, "V": V})
        print()


if __name__ == "__main__":
    if len(sys.argv) == 5:
        run_cli()
    else:
        run_interactive()
