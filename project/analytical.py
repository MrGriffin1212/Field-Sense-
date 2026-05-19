"""
Analytical engine for the ground-level electric field beneath a
3-phase UHV AC transmission line, using Maxwell's potential
coefficient matrix method with image charges.
"""
import os
import numpy as np
import matplotlib.pyplot as plt


def bundle_equivalent_radius(N, r, R):
    """r_eq = (N * r * R^(N-1))^(1/N)

    N : sub-conductors per bundle
    r : sub-conductor radius (m)
    R : bundle radius (m)
    """
    return (N * r * R ** (N - 1)) ** (1.0 / N)


def potential_coefficient_matrix(coords, r_eq):
    """Maxwell's potential coefficient matrix [P] (n x n).

    Diagonal:    P_ii = ln(2 * H_i / r_eq)
    Off-diag:    P_ij = ln(I_ij / A_ij)
        A_ij = direct distance conductor i to conductor j
        I_ij = distance conductor i to image of conductor j (below ground)
    """
    n = len(coords)
    P = np.zeros((n, n))
    for i in range(n):
        xi, yi = coords[i]
        for j in range(n):
            xj, yj = coords[j]
            if i == j:
                P[i, j] = np.log(2.0 * yi / r_eq)
            else:
                A_ij = np.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                I_ij = np.sqrt((xi - xj) ** 2 + (yi + yj) ** 2)
                P[i, j] = np.log(I_ij / A_ij)
    return P


def field_coefficient_K(x_eval, coords):
    """Geometric coefficient vector K at the ground point (x_eval, 0).

    At y = 0 the real and image contributions add and the horizontal
    components cancel, leaving the vertical field proportional to:
        K_i = -2 * y_i / ((x - x_i)^2 + y_i^2)
    """
    n = len(coords)
    K = np.zeros(n)
    for i in range(n):
        xi, yi = coords[i]
        K[i] = -2.0 * yi / ((x_eval - xi) ** 2 + yi ** 2)
    return K


def electric_field_at_ground(x_eval, coords, M, V_phase_rms):
    """RMS vertical ground-level field for balanced 3-phase voltages.

    M           : inverse of P (n x n)
    V_phase_rms : line-to-ground rms voltage (kV here)
    """
    K = field_coefficient_K(x_eval, coords)
    Kv = M.T @ K
    Kv1, Kv2, Kv3 = Kv[0], Kv[1], Kv[2]
    K_v = np.sqrt(
        Kv1 ** 2 + Kv2 ** 2 + Kv3 ** 2
        - Kv1 * Kv2 - Kv2 * Kv3 - Kv3 * Kv1
    )
    return K_v * V_phase_rms


def line_to_ground_rms(V_line_to_line):
    return V_line_to_line / np.sqrt(3.0)


def validate_1200kV():
    print("=" * 72)
    print(" 1200 kV UHV AC line  -  analytical engine validation ")
    print("=" * 72)

    N, R, r = 8, 0.6, 0.02815
    H = 37.0
    d = 24.0
    V_ll = 1200.0
    V = line_to_ground_rms(V_ll)

    coords = [(-d, H), (0.0, H), (d, H)]

    r_eq = bundle_equivalent_radius(N, r, R)
    P = potential_coefficient_matrix(coords, r_eq)
    M = np.linalg.inv(P)

    print(f"\nr_eq                  : {r_eq:.6f} m")
    print(f"V_phase_rms           : {V:.4f} kV")

    print("\nComputed [P] matrix:")
    print(np.array_str(P, precision=4, suppress_small=True))

    print("\nComputed [M] = [P]^-1:")
    print(np.array_str(M, precision=4, suppress_small=True))

    P_ref = np.array([[4.5414, 0.8147, 0.3528],
                      [0.8147, 4.5414, 0.8147],
                      [0.3528, 0.8147, 4.5414]])
    M_ref = np.array([[ 0.2280, -0.0390, -0.0107],
                      [-0.0390,  0.2342, -0.0390],
                      [-0.0107, -0.0390,  0.2280]])

    print("\nReference [P] from problem statement:")
    print(P_ref)
    print("\nReference [M] from problem statement:")
    print(M_ref)

    print("\nMax |dP|              :", np.max(np.abs(P - P_ref)))
    print("Max |dM|              :", np.max(np.abs(M - M_ref)))

    E0 = electric_field_at_ground(0.0, coords, M, V)
    E_below_phase = electric_field_at_ground(d, coords, M, V)
    print(f"\nE_v at x = 0 m        : {E0:.4f} kV/m")
    print(f"E_v at x = {d:.1f} m (under outer phase): {E_below_phase:.4f} kV/m")

    return coords, M, V


def plot_field_profile(coords, M, V,
                       x_min=-100.0, x_max=100.0, n=801,
                       out_path="plots/efield_profile.png"):
    xs = np.linspace(x_min, x_max, n)
    Es = np.array([electric_field_at_ground(x, coords, M, V) for x in xs])

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.plot(xs, Es, lw=2, color="#1f4eb6")
    plt.axhline(5.0, color="red", ls="--", lw=1, label="WHO limit (5 kV/m)")
    plt.xlabel("Lateral distance x (m)")
    plt.ylabel("Ground level electric field E_v (kV/m)")
    plt.title("1200 kV UHV AC line - ground level E-field profile")
    plt.legend()
    plt.grid(alpha=0.4)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"Saved plot -> {out_path}")


if __name__ == "__main__":
    coords, M, V = validate_1200kV()
    plot_field_profile(coords, M, V)
