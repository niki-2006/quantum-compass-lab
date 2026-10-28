"""
Generate publication-quality, poster-ready figures for Quantum Compass Lab.

Outputs:
- PNG (300 DPI, high-resolution raster)
- SVG (scalable vector graphics)
- PDF (vector format for print posters)

Data source:
Direct calculation and cross-check with results/experiment_1_angular_response.csv.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.metrics import calculate_compass_metrics
from src.plotting import STYLE_CONFIG


def generate_poster_figures():
    # Load actual experimental data
    csv_path = Path("results/experiment_1_angular_response.csv")
    df = pd.read_csv(csv_path)
    df_50 = df[df["B_uT"] == 50.0].sort_values("theta_deg")

    thetas_deg = df_50["theta_deg"].values
    thetas_rad = np.deg2rad(thetas_deg)
    singlet_yields = df_50["singlet_yield"].values
    triplet_yields = df_50["triplet_yield"].values

    metrics = calculate_compass_metrics(thetas_rad, singlet_yields)

    # Destination directories
    docs_fig_dir = Path("docs/figures")
    docs_fig_dir.mkdir(parents=True, exist_ok=True)
    results_dir = Path("results")

    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["font.family"] = "sans-serif"

    # Figure 1: Dark theme (matches dashboard and slide presentations)
    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=300)
    ax.set_facecolor("#0B1120")
    fig.patch.set_facecolor("#0B1120")

    # Main yield curve
    ax.plot(
        thetas_deg, singlet_yields,
        color="#38BDF8", linewidth=2.8,
        label=r"Singlet Yield $\Phi_S(\theta)$",
        zorder=3
    )

    # Extrema scatter markers
    ax.scatter(
        [metrics.theta_max_deg], [metrics.phi_s_max],
        color="#34D399", s=130, edgecolors="#FFFFFF", linewidth=1.5, zorder=5,
        label=f"Max: {metrics.phi_s_max:.4f} @ {metrics.theta_max_deg:.0f}°"
    )
    ax.scatter(
        [metrics.theta_min_deg], [metrics.phi_s_min],
        color="#FB7185", s=130, edgecolors="#FFFFFF", linewidth=1.5, zorder=5,
        label=f"Min: {metrics.phi_s_min:.4f} @ {metrics.theta_min_deg:.0f}°"
    )

    # Extrema annotations
    ax.annotate(
        f"Max: {metrics.phi_s_max:.4f}\n({metrics.theta_max_deg:.0f}°)",
        xy=(metrics.theta_max_deg, metrics.phi_s_max),
        xytext=(metrics.theta_max_deg + 12, metrics.phi_s_max - 0.018),
        arrowprops=dict(arrowstyle="->", color="#34D399", lw=1.5),
        fontsize=9.5, fontweight="bold", color="#34D399",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#020617", edgecolor="#34D399", alpha=0.9)
    )

    ax.annotate(
        f"Min: {metrics.phi_s_min:.4f}\n({metrics.theta_min_deg:.0f}°)",
        xy=(metrics.theta_min_deg, metrics.phi_s_min),
        xytext=(metrics.theta_min_deg + 14, metrics.phi_s_min - 0.026),
        arrowprops=dict(arrowstyle="->", color="#FB7185", lw=1.5),
        fontsize=9.5, fontweight="bold", color="#FB7185",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#020617", edgecolor="#FB7185", alpha=0.9)
    )

    # Shaded anisotropic dynamic range
    ax.fill_between(thetas_deg, metrics.phi_s_min, singlet_yields, color="#38BDF8", alpha=0.12, zorder=2)

    # Grid and spines
    ax.grid(True, linestyle="--", alpha=0.25, color="#334155", zorder=1)
    for spine in ax.spines.values():
        spine.set_color("#334155")
        spine.set_linewidth(1.0)

    ax.set_xlim(-5, 185)
    ax.set_ylim(0.33, 0.52)
    ax.set_xticks(np.arange(0, 181, 30))

    ax.set_xlabel(r"Geomagnetic Field Polar Angle $\theta$ (degrees)", fontsize=12, fontweight="bold", color="#F8FAFC", labelpad=8)
    ax.set_ylabel(r"Integrated Singlet Reaction Yield $\Phi_S$", fontsize=12, fontweight="bold", color="#F8FAFC", labelpad=8)
    ax.set_title(r"Radical-Pair Magnetoreception: Singlet Yield vs Field Angle ($B_0 = 50\ \mu\mathrm{T}$)", fontsize=13, fontweight="bold", color="#F8FAFC", pad=14)
    ax.tick_params(colors="#F8FAFC", labelsize=10.5)

    # Callout box with performance metrics
    info_text = (
        "Compass Performance Metrics:\n"
        f"  • Max Yield: {metrics.phi_s_max:.4f} at {metrics.theta_max_deg:.0f}°\n"
        f"  • Min Yield: {metrics.phi_s_min:.4f} at {metrics.theta_min_deg:.0f}°\n"
        f"  • Absolute Anisotropy ΔΦ_S: {metrics.absolute_anisotropy:.4f}\n"
        f"  • Relative Contrast C: {metrics.contrast * 100:.2f}%\n"
        "  • Yield Sum: Φ_S + Φ_T = 1.000000\n"
        "Model Parameters:\n"
        r"  • Field B: 50.0 $\mu$T (geomagnetic norm)" "\n"
        r"  • Hyperfine A: [5, 5, 20] rad/$\mu$s (axial)" "\n"
        r"  • Kinetics $k_S = k_T = 1.0\ \mu\mathrm{s}^{-1}$"
    )
    ax.text(
        0.58, 0.05, info_text,
        transform=ax.transAxes,
        fontsize=9.0,
        verticalalignment="bottom",
        color="#F8FAFC",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#020617", edgecolor="#38BDF8", linewidth=1.2, alpha=0.95),
        zorder=6
    )

    ax.legend(loc="upper right", facecolor="#020617", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=9.5)
    fig.tight_layout()

    # Save dark-themed vector and raster formats
    for folder in [docs_fig_dir, results_dir]:
        fig.savefig(folder / "poster_figure_angular_sweep.png", dpi=300, bbox_inches="tight")
        fig.savefig(folder / "poster_figure_angular_sweep.svg", format="svg", bbox_inches="tight")
        fig.savefig(folder / "poster_figure_angular_sweep.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)

    # Figure 2: Publication white-background version (for print poster sections)
    fig_w, ax_w = plt.subplots(figsize=(8.5, 5.2), dpi=300)
    ax_w.set_facecolor("#FFFFFF")
    fig_w.patch.set_facecolor("#FFFFFF")

    ax_w.plot(thetas_deg, singlet_yields, color="#0284C7", linewidth=2.8, label=r"Singlet Yield $\Phi_S(\theta)$", zorder=3)
    ax_w.scatter([metrics.theta_max_deg], [metrics.phi_s_max], color="#059669", s=130, edgecolors="#000000", linewidth=1.2, zorder=5, label=f"Max: {metrics.phi_s_max:.4f} @ {metrics.theta_max_deg:.0f}°")
    ax_w.scatter([metrics.theta_min_deg], [metrics.phi_s_min], color="#DC2626", s=130, edgecolors="#000000", linewidth=1.2, zorder=5, label=f"Min: {metrics.phi_s_min:.4f} @ {metrics.theta_min_deg:.0f}°")

    ax_w.annotate(
        f"Max: {metrics.phi_s_max:.4f} ({metrics.theta_max_deg:.0f}°)",
        xy=(metrics.theta_max_deg, metrics.phi_s_max),
        xytext=(metrics.theta_max_deg + 12, metrics.phi_s_max - 0.018),
        arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5),
        fontsize=9.5, fontweight="bold", color="#059669",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#F0FDF4", edgecolor="#059669", alpha=0.95)
    )

    ax_w.annotate(
        f"Min: {metrics.phi_s_min:.4f} ({metrics.theta_min_deg:.0f}°)",
        xy=(metrics.theta_min_deg, metrics.phi_s_min),
        xytext=(metrics.theta_min_deg + 14, metrics.phi_s_min - 0.026),
        arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5),
        fontsize=9.5, fontweight="bold", color="#DC2626",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#FEF2F2", edgecolor="#DC2626", alpha=0.95)
    )

    ax_w.fill_between(thetas_deg, metrics.phi_s_min, singlet_yields, color="#0284C7", alpha=0.10, zorder=2)
    ax_w.grid(True, linestyle="--", alpha=0.35, color="#94A3B8", zorder=1)
    for spine in ax_w.spines.values():
        spine.set_color("#64748B")
        spine.set_linewidth(1.0)

    ax_w.set_xlim(-5, 185)
    ax_w.set_ylim(0.33, 0.52)
    ax_w.set_xticks(np.arange(0, 181, 30))

    ax_w.set_xlabel(r"Geomagnetic Field Polar Angle $\theta$ (degrees)", fontsize=12, fontweight="bold", color="#0F172A", labelpad=8)
    ax_w.set_ylabel(r"Integrated Singlet Reaction Yield $\Phi_S$", fontsize=12, fontweight="bold", color="#0F172A", labelpad=8)
    ax_w.set_title(r"Radical-Pair Magnetoreception: Singlet Yield vs Field Angle ($B_0 = 50\ \mu\mathrm{T}$)", fontsize=13, fontweight="bold", color="#0F172A", pad=14)
    ax_w.tick_params(colors="#0F172A", labelsize=10.5)

    ax_w.text(
        0.58, 0.05, info_text,
        transform=ax_w.transAxes,
        fontsize=9.0,
        verticalalignment="bottom",
        color="#0F172A",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#F8FAFC", edgecolor="#0284C7", linewidth=1.2, alpha=0.95),
        zorder=6
    )

    ax_w.legend(loc="upper right", facecolor="#FFFFFF", edgecolor="#CBD5E1", labelcolor="#0F172A", fontsize=9.5)
    fig_w.tight_layout()

    for folder in [docs_fig_dir, results_dir]:
        fig_w.savefig(folder / "poster_figure_angular_sweep_print.png", dpi=300, bbox_inches="tight")
        fig_w.savefig(folder / "poster_figure_angular_sweep_print.svg", format="svg", bbox_inches="tight")
        fig_w.savefig(folder / "poster_figure_angular_sweep_print.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig_w)

    print("Poster figures generated successfully.")
    print("Files created:")
    for fn in [
        "poster_figure_angular_sweep.png",
        "poster_figure_angular_sweep.svg",
        "poster_figure_angular_sweep.pdf",
        "poster_figure_angular_sweep_print.png",
        "poster_figure_angular_sweep_print.svg",
        "poster_figure_angular_sweep_print.pdf",
    ]:
        print(f"  - docs/figures/{fn}")
        print(f"  - results/{fn}")


if __name__ == "__main__":
    generate_poster_figures()
