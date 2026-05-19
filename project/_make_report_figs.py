"""
Generate the extra figures needed by the project report:
  - tower_schematic.png      (3-phase + image charges)
  - bundle_geometry.png      (N-conductor bundle close-up)
  - methodology_flow.png     (block diagram analytical -> ML -> webapp)
  - who_bar.png              (E_v across voltage levels vs 5 kV/m limit)
  - webapp_mock.png          (matrix-themed calculator mock)
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.patches import FancyArrowPatch

from analytical import (
    bundle_equivalent_radius,
    potential_coefficient_matrix,
    electric_field_at_ground,
    line_to_ground_rms,
)

OUT = r"C:\Users\saket\project\plots"
os.makedirs(OUT, exist_ok=True)


# ---------------------------------------------------------------- 1
def tower_schematic():
    fig, ax = plt.subplots(figsize=(9, 7))
    H = 37.0
    d = 24.0
    R = 0.6
    N = 8
    coords = [(-d, H), (0.0, H), (d, H)]
    labels = ["Phase A", "Phase B", "Phase C"]
    cols   = ["#d62728", "#1f77b4", "#2ca02c"]

    ax.axhspan(-6, 0, color="#c7a17a", alpha=0.5)
    ax.axhline(0, color="black", lw=1.5)
    ax.text(60, -3, "GROUND PLANE  (y = 0)", fontsize=9, ha="right",
            style="italic", color="#333")

    for (x, y), lab, c in zip(coords, labels, cols):
        ax.scatter(x, y, s=600, marker="o", facecolor=c,
                   edgecolor="black", lw=1.2, zorder=5)
        ang = np.linspace(0, 2 * np.pi, N, endpoint=False)
        for a in ang:
            ax.scatter(x + R * np.cos(a) * 4, y + R * np.sin(a) * 4,
                       s=18, marker="o", facecolor="white",
                       edgecolor=c, lw=1.0, zorder=6)
        ax.text(x, y + 4.0, lab, ha="center", fontsize=10,
                color=c, fontweight="bold")
        ax.text(x, y - 5.0, f"H = {H} m", ha="center", fontsize=8,
                color="#444")

        ax.scatter(x, -y, s=600, marker="o",
                   facecolor=c, alpha=0.25,
                   edgecolor="black", linestyle="--", lw=1.0, zorder=4)
        ax.text(x, -y - 3.0, "image", ha="center", fontsize=8,
                color=c, style="italic")
        ax.plot([x, x], [y, -y], color=c, lw=0.6, linestyle=":", alpha=0.6)

    ax.annotate("", xy=(0, H), xytext=(d, H),
                arrowprops=dict(arrowstyle="<->", color="#555"))
    ax.text(d / 2, H + 1.6, f"d = {d} m", ha="center", fontsize=9, color="#555")
    ax.annotate("", xy=(-d, H), xytext=(0, H),
                arrowprops=dict(arrowstyle="<->", color="#555"))
    ax.text(-d / 2, H + 1.6, f"d = {d} m", ha="center", fontsize=9, color="#555")

    xs = np.linspace(-60, 60, 121)
    coords = [(-d, H), (0.0, H), (d, H)]
    r_eq = bundle_equivalent_radius(N, 0.02815, R)
    P = potential_coefficient_matrix(coords, r_eq)
    M = np.linalg.inv(P)
    V_PH = line_to_ground_rms(1200.0)
    E = np.array([electric_field_at_ground(xi, coords, M, V_PH) for xi in xs])

    ax2 = ax.twinx()
    ax2.plot(xs, -E - 6.5, color="#ff7f0e", lw=2.0, alpha=0.9)
    ax2.fill_between(xs, -E - 6.5, -6.5, color="#ff7f0e", alpha=0.2)
    ax2.set_ylim(-15, 50)
    ax2.set_yticks([])
    ax2.text(0, -E.max() - 5.0, "ground-level $E_v(x)$ profile",
             ha="center", fontsize=8, color="#b35900", style="italic")

    ax.axhline(-6.5, xmin=0.02, xmax=0.98, color="#ff7f0e",
               linestyle=(0, (3, 3)), lw=0.6, alpha=0.6)
    ax.set_xlim(-60, 60)
    ax.set_ylim(-15, 50)
    ax.set_xlabel("Lateral distance x (m)")
    ax.set_ylabel("Height y (m)")
    ax.set_title("1200 kV three-phase UHV AC line – conductors, image charges,\n"
                 "and resulting ground-level field profile",
                 fontsize=11)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "tower_schematic.png"), dpi=150)
    plt.close()
    print("saved tower_schematic.png")


# ---------------------------------------------------------------- 2
def bundle_geometry():
    fig, ax = plt.subplots(figsize=(6, 6))
    N, R, r = 8, 0.6, 0.02815
    ang = np.linspace(0, 2 * np.pi, N, endpoint=False)

    circ = plt.Circle((0, 0), R, fill=False, color="#666",
                      linestyle="--", lw=1.0)
    ax.add_patch(circ)
    ax.plot(0, 0, marker="+", color="#666", ms=12, mew=1.5)

    for a in ang:
        x, y = R * np.cos(a), R * np.sin(a)
        c = plt.Circle((x, y), r * 10, color="#1f77b4", alpha=0.85, zorder=5)
        ax.add_patch(c)
        ax.annotate("", xy=(x, y), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color="#888", lw=0.8))

    ax.annotate("R = 0.6 m", xy=(R * np.cos(np.pi / 4) / 2,
                                 R * np.sin(np.pi / 4) / 2),
                xytext=(0.15, 0.18), fontsize=10, color="#444")

    a0 = ang[0]
    x0, y0 = R * np.cos(a0), R * np.sin(a0)
    ax.annotate("r = 0.02815 m\n(sub-conductor)",
                xy=(x0 + r * 10, y0),
                xytext=(x0 + 0.20, y0 - 0.20), fontsize=9,
                color="#1f4d80",
                arrowprops=dict(arrowstyle="->", color="#1f4d80", lw=0.8))

    ax.text(0, -1.0, "N = 8  sub-conductors", ha="center",
            fontsize=11, color="#333", fontweight="bold")
    ax.text(0, -1.18,
            r"$r_{eq}=\left(N\,r\,R^{N-1}\right)^{1/N}\approx 0.531$ m",
            ha="center", fontsize=11, color="#b35900")

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.3, 1.1)
    ax.set_aspect("equal")
    ax.set_title("Bundle conductor geometry (N = 8)", fontsize=11)
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "bundle_geometry.png"), dpi=150)
    plt.close()
    print("saved bundle_geometry.png")


# ---------------------------------------------------------------- 3
def methodology_flow():
    fig, ax = plt.subplots(figsize=(11, 4.6))
    blocks = [
        ("Geometry +\nVoltage Inputs\n(x, H, d, V)", "#cfe2ff"),
        ("Bundle r_eq\n& Potential\nMatrix [P]", "#d4edda"),
        ("[M] = [P]⁻¹\nField Coeffs\nKᵢ(x)", "#fff3cd"),
        ("Three-phase\nRMS\nE_v(x)", "#f8d7da"),
        ("12 000-sample\nDataset CSV", "#e2e3e5"),
        ("Train ANN / RF / SVR\nSelect best (R² = 0.999)", "#d1ecf1"),
        ("FieldSense\nWeb Calculator\n(WHO check)", "#c3e6cb"),
    ]
    w, h = 1.35, 1.0
    y = 0
    xs = np.linspace(0, 13.5, len(blocks))
    for (label, color), x in zip(blocks, xs):
        ax.add_patch(mp.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.06,rounding_size=0.1",
            facecolor=color, edgecolor="#333", lw=1.0))
        ax.text(x, y, label, ha="center", va="center", fontsize=8.2)
    for i in range(len(blocks) - 1):
        ax.annotate("", xy=(xs[i + 1] - w / 2, y),
                    xytext=(xs[i] + w / 2, y),
                    arrowprops=dict(arrowstyle="->", lw=1.4, color="#555"))

    ax.text((xs[0] + xs[3]) / 2, -1.0,
            "Analytical engine (Maxwell + Images)",
            ha="center", fontsize=10, color="#444",
            fontweight="bold")
    ax.plot([xs[0] - w / 2, xs[3] + w / 2], [-0.75, -0.75],
            color="#aaa", lw=1.2)

    ax.text((xs[4] + xs[5]) / 2, -1.0,
            "Machine Learning",
            ha="center", fontsize=10, color="#444", fontweight="bold")
    ax.plot([xs[4] - w / 2, xs[5] + w / 2], [-0.75, -0.75],
            color="#aaa", lw=1.2)

    ax.text(xs[6], -1.0, "Deployment", ha="center", fontsize=10,
            color="#444", fontweight="bold")
    ax.plot([xs[6] - w / 2, xs[6] + w / 2], [-0.75, -0.75],
            color="#aaa", lw=1.2)

    ax.set_xlim(-0.8, 14.3)
    ax.set_ylim(-1.4, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("FieldSense methodology pipeline", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "methodology_flow.png"), dpi=150)
    plt.close()
    print("saved methodology_flow.png")


# ---------------------------------------------------------------- 4
def who_bar():
    voltages = [220, 400, 765, 1000, 1200]
    H, d, N, R, r = 37.0, 24.0, 8, 0.6, 0.02815
    r_eq = bundle_equivalent_radius(N, r, R)
    P = potential_coefficient_matrix([(-d, H), (0, H), (d, H)], r_eq)
    M = np.linalg.inv(P)
    Es = []
    for v in voltages:
        Vph = line_to_ground_rms(v)
        Es.append(electric_field_at_ground(0.0, [(-d, H), (0, H), (d, H)],
                                           M, Vph))

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar([str(v) + " kV" for v in voltages], Es,
                  color=["#5cb85c" if e <= 5.0 else "#d9534f" for e in Es],
                  edgecolor="black", lw=0.8)
    ax.axhline(5.0, color="#d9534f", linestyle="--", lw=1.6,
               label="WHO public exposure limit (5 kV/m)")
    for b, e in zip(bars, Es):
        ax.text(b.get_x() + b.get_width() / 2, e + 0.08,
                f"{e:.2f}", ha="center", fontsize=10, color="#333")
    ax.set_ylabel("E_v at ground (kV/m), beneath centre phase")
    ax.set_xlabel("Line-to-line voltage")
    ax.set_title("Ground-level field at centre phase vs WHO limit\n"
                 "(H = 37 m,  d = 24 m,  N = 8 × 0.02815 m bundle)",
                 fontsize=11)
    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.35)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "who_bar.png"), dpi=150)
    plt.close()
    print("saved who_bar.png")


# ---------------------------------------------------------------- 5
def webapp_mock():
    fig = plt.figure(figsize=(11, 6.5), facecolor="#000")
    gs = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.30)

    GREEN  = "#00FF41"
    DIM    = "#008F11"
    BG     = "#000000"
    BG2    = "#001a07"

    for ax in [fig.add_subplot(gs[0, 0]),
               fig.add_subplot(gs[1, 0])]:
        ax.set_facecolor(BG2)
        ax.tick_params(colors=GREEN, labelsize=7)
        for s in ax.spines.values():
            s.set_color(DIM)
    ax_inputs = fig.axes[0]
    ax_matrix = fig.axes[1]
    ax_plot   = fig.add_subplot(gs[0:, 1:])
    ax_plot.set_facecolor(BG2)
    for s in ax_plot.spines.values():
        s.set_color(DIM)
    ax_plot.tick_params(colors=GREEN, labelsize=8)

    rows = [("x (lateral)", "0.0 m"),
            ("H (height)",  "37.0 m"),
            ("d (spacing)", "24.0 m"),
            ("V (LL rms)",  "1200 kV"),
            ("N · r · R",   "8 · 0.02815 · 0.6")]
    ax_inputs.axis("off")
    ax_inputs.text(0.02, 0.95, "[ FIELDSENSE INPUTS ]",
                   color=GREEN, fontsize=11, fontweight="bold",
                   family="monospace", transform=ax_inputs.transAxes)
    for i, (k, v) in enumerate(rows):
        y = 0.82 - i * 0.13
        ax_inputs.text(0.02, y, k, color=DIM, family="monospace",
                       fontsize=9, transform=ax_inputs.transAxes)
        ax_inputs.text(0.55, y, v, color=GREEN, family="monospace",
                       fontsize=9, transform=ax_inputs.transAxes)

    ax_matrix.axis("off")
    ax_matrix.text(0.02, 0.92, "[ POTENTIAL  MATRIX  [P] ]",
                   color=GREEN, family="monospace",
                   fontsize=10, fontweight="bold",
                   transform=ax_matrix.transAxes)
    Pmat = [[4.937, 1.121, 0.501],
            [1.121, 4.937, 1.121],
            [0.501, 1.121, 4.937]]
    for i, row in enumerate(Pmat):
        for j, v in enumerate(row):
            ax_matrix.text(0.15 + j * 0.28, 0.65 - i * 0.18,
                           f"{v:6.3f}", color=GREEN, family="monospace",
                           fontsize=10, transform=ax_matrix.transAxes)

    xs = np.linspace(-100, 100, 401)
    H, d, V = 37.0, 24.0, 1200.0
    coords = [(-d, H), (0, H), (d, H)]
    r_eq = bundle_equivalent_radius(8, 0.02815, 0.6)
    P = potential_coefficient_matrix(coords, r_eq)
    M = np.linalg.inv(P)
    Vph = line_to_ground_rms(V)
    Es = np.array([electric_field_at_ground(xi, coords, M, Vph) for xi in xs])
    ax_plot.plot(xs, Es, color=GREEN, lw=2.0)
    ax_plot.fill_between(xs, Es, color=GREEN, alpha=0.10)
    ax_plot.axhline(5.0, color="#ff3366", linestyle="--", lw=1.4)
    ax_plot.text(80, 5.18, "WHO 5 kV/m", color="#ff3366",
                 family="monospace", fontsize=8)
    ax_plot.scatter([0], [Es[200]], color="white", s=60, zorder=5,
                    edgecolor=GREEN)
    ax_plot.text(2, Es[200] + 0.25, f"E_v(0) = {Es[200]:.3f} kV/m",
                 color="white", family="monospace", fontsize=9)
    ax_plot.set_title("> GROUND-LEVEL E_v PROFILE  (kV/m)",
                      color=GREEN, family="monospace", fontsize=11, loc="left")
    ax_plot.set_xlabel("x (m)", color=GREEN, family="monospace")
    ax_plot.grid(alpha=0.2, color=DIM)
    ax_plot.set_ylim(0, max(6.5, Es.max() * 1.2))

    fig.suptitle("FieldSense  —  Real-Time UHV E-Field Calculator",
                 color=GREEN, family="monospace", fontsize=14,
                 fontweight="bold", y=0.99)
    plt.savefig(os.path.join(OUT, "webapp_mock.png"), dpi=150,
                facecolor=BG)
    plt.close()
    print("saved webapp_mock.png")


# ---------------------------------------------------------------- 6
def phasor_diagram():
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="polar")
    ang = [0, -120, 120]
    cols = ["#d62728", "#1f77b4", "#2ca02c"]
    labs = [r"$V_A \angle 0\degree$",
            r"$V_B \angle -120\degree$",
            r"$V_C \angle +120\degree$"]
    for a, c, l in zip(ang, cols, labs):
        ax.annotate("", xy=(np.radians(a), 1.0), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color=c, lw=2.4))
        ax.text(np.radians(a), 1.15, l, color=c, ha="center",
                fontsize=11, fontweight="bold")
    ax.set_rticks([])
    ax.set_rmax(1.3)
    ax.grid(alpha=0.4)
    ax.set_title("Three-phase voltage phasors\n"
                 r"($120\degree$ apart, equal magnitude $V_{ph}$)",
                 pad=22, fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "phasor_diagram.png"), dpi=150)
    plt.close()
    print("saved phasor_diagram.png")


# ---------------------------------------------------------------- 7
def sensitivity_heatmap():
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    Hs = np.linspace(20, 60, 45)
    Vs = np.linspace(200, 1300, 55)
    Hg, Vg = np.meshgrid(Hs, Vs)
    E = np.zeros_like(Hg)
    N, R, r, d = 8, 0.6, 0.02815, 24.0
    r_eq = bundle_equivalent_radius(N, r, R)
    for i, h in enumerate(Hs):
        coords = [(-d, h), (0.0, h), (d, h)]
        P = potential_coefficient_matrix(coords, r_eq)
        M = np.linalg.inv(P)
        for j, v in enumerate(Vs):
            Vph = line_to_ground_rms(v)
            E[j, i] = electric_field_at_ground(0.0, coords, M, Vph)
    cf = ax.contourf(Hg, Vg, E, levels=22, cmap="RdYlGn_r")
    cb = plt.colorbar(cf, ax=ax)
    cb.set_label("$E_v$ at $x=0$  (kV/m)", fontsize=11)
    cs = ax.contour(Hg, Vg, E, levels=[5.0],
                    colors=["white"], linewidths=2.4, linestyles="--")
    ax.clabel(cs, fmt="WHO 5 kV/m", fontsize=9, colors="white")
    ax.set_xlabel("Line height $H$ (m)", fontsize=11)
    ax.set_ylabel("Line-to-line voltage (kV)", fontsize=11)
    ax.set_title("Sensitivity of centre-phase $E_v$ to height "
                 "and operating voltage\n"
                 r"($d = 24$ m, $N = 8 \times 0.02815$ m bundle)",
                 fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "sensitivity_heatmap.png"), dpi=150)
    plt.close()
    print("saved sensitivity_heatmap.png")


if __name__ == "__main__":
    tower_schematic()
    bundle_geometry()
    methodology_flow()
    who_bar()
    webapp_mock()
    phasor_diagram()
    sensitivity_heatmap()
    print("ALL DONE")
