"""
Generate user-requested high-resolution plots for Quantum Compass Lab.

1. angular_sweep.png:
   - 6x4 inches, 300 DPI, large readable fonts
   - 91-point sweep of singlet yield Phi_S vs field angle theta
   - Labeled max (0.4872 at 0 deg) and min (0.3726 at 32 deg)
   - Dashed flat line for isotropic-hyperfine control (Phi_S = 0.4595)

2. contrast_vs_decoherence.png:
   - 6x4 inches, 300 DPI, large readable fonts
   - Directional contrast C = (max - min) / (max + min) vs decoherence rate gamma (log scale x-axis)
   - Threshold markers and clear scientific styling
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.spin_model import SpinModelConfig
from src.initial_states import get_initial_density_matrix
from src.reaction_kinetics import calculate_yields_exact
from src.metrics import calculate_compass_metrics


def generate_plots():
    # ---------------------------------------------------------
    # 1. ANGULAR SWEEP PLOT (6x4 inches, 300 dpi)
    # ---------------------------------------------------------
    csv_path = PROJECT_ROOT / "results" / "experiment_1_angular_response.csv"
    df = pd.read_csv(csv_path)
    df_50 = df[df["B_uT"] == 50.0].sort_values("theta_deg")

    thetas_deg = df_50["theta_deg"].values
    thetas_rad = np.deg2rad(thetas_deg)
    singlet_50 = df_50["singlet_yield"].values

    metrics = calculate_compass_metrics(thetas_rad, singlet_50)

    # Compute exact isotropic control yield
    cfg_iso = SpinModelConfig(B_magnitude=50.0, A_xx=10.0, A_yy=10.0, A_zz=10.0, k_S=1.0, k_T=1.0)
    rho_0 = get_initial_density_matrix()
    iso_ys, _ = calculate_yields_exact(rho_0, cfg_iso)

    # Clean publication style with large fonts
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]

    fig1, ax1 = plt.subplots(figsize=(6.0, 4.0), dpi=300)
    fig1.patch.set_facecolor("#FFFFFF")
    ax1.set_facecolor("#FFFFFF")

    # Main anisotropic curve
    ax1.plot(
        thetas_deg, singlet_50,
        color="#0284C7", linewidth=2.5,
        label=r"Anisotropic $\mathbf{A} = [5, 5, 20]\ \mathrm{rad}/\mu\mathrm{s}$",
        zorder=3
    )

    # Dashed flat line for isotropic control
    ax1.axhline(
        iso_ys,
        color="#64748B", linestyle="--", linewidth=1.8,
        label=f"Isotropic Control ($A = 10\\ \\mathrm{{rad}}/\\mu\\mathrm{{s}}$, $\\Phi_S = {iso_ys:.4f}$)",
        zorder=2
    )

    # Extrema markers
    ax1.scatter([metrics.theta_max_deg], [metrics.phi_s_max], color="#059669", s=90, zorder=5, edgecolors="#000000", linewidth=1.0)
    ax1.scatter([metrics.theta_min_deg], [metrics.phi_s_min], color="#DC2626", s=90, zorder=5, edgecolors="#000000", linewidth=1.0)

    # Callout labels for max and min
    ax1.annotate(
        f"Max: {metrics.phi_s_max:.4f}\nat {metrics.theta_max_deg:.0f}°",
        xy=(metrics.theta_max_deg, metrics.phi_s_max),
        xytext=(metrics.theta_max_deg + 14, metrics.phi_s_max - 0.020),
        arrowprops=dict(arrowstyle="->", color="#059669", lw=1.5),
        fontsize=10, fontweight="bold", color="#059669",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#F0FDF4", edgecolor="#059669", lw=1.0)
    )

    ax1.annotate(
        f"Min: {metrics.phi_s_min:.4f}\nat {metrics.theta_min_deg:.0f}°",
        xy=(metrics.theta_min_deg, metrics.phi_s_min),
        xytext=(metrics.theta_min_deg + 15, metrics.phi_s_min - 0.025),
        arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5),
        fontsize=10, fontweight="bold", color="#DC2626",
        bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF2F2", edgecolor="#DC2626", lw=1.0)
    )

    # Shaded anisotropic variation region
    ax1.fill_between(thetas_deg, metrics.phi_s_min, singlet_50, color="#0284C7", alpha=0.08, zorder=1)

    ax1.set_xlim(-5, 185)
    ax1.set_ylim(0.33, 0.52)
    ax1.set_xticks(np.arange(0, 181, 30))

    ax1.set_xlabel(r"Field Angle $\theta$ (degrees)", fontsize=11, fontweight="bold", labelpad=6)
    ax1.set_ylabel(r"Singlet Yield $\Phi_S$", fontsize=11, fontweight="bold", labelpad=6)
    ax1.set_title(r"Radical-Pair Singlet Yield vs Field Angle ($B = 50\ \mu\mathrm{T}$)", fontsize=11.5, fontweight="bold", pad=8)

    ax1.tick_params(axis="both", labelsize=10)
    ax1.grid(True, linestyle=":", alpha=0.5, color="#94A3B8")
    ax1.legend(loc="upper right", fontsize=8.5, framealpha=0.95, edgecolor="#CBD5E1")

    fig1.tight_layout()

    # Save angular sweep plot
    for dest in [PROJECT_ROOT / "angular_sweep.png", PROJECT_ROOT / "results" / "angular_sweep.png", PROJECT_ROOT / "docs" / "figures" / "angular_sweep.png"]:
        fig1.savefig(dest, dpi=300, bbox_inches="tight")
    plt.close(fig1)
    print("Saved angular_sweep.png (6x4 inches, 300 DPI)")

    # ---------------------------------------------------------
    # 2. CONTRAST VS DECOHERENCE RATE PLOT (6x4 inches, 300 dpi)
    # ---------------------------------------------------------
    json_path = PROJECT_ROOT / "results" / "experiment_results.json"
    with open(json_path, "r", encoding="utf-8") as f:
        exp_res = json.load(f)

    coherence_times = np.array(exp_res["experiment_2"]["coherence_times_explored_us"])
    contrasts = np.array(exp_res["experiment_2"]["contrasts"]) * 100.0  # as percentage
    decoherence_rates = 1.0 / coherence_times  # gamma in us^-1

    # Sort in ascending order of decoherence rate gamma
    sort_idx = np.argsort(decoherence_rates)
    gamma_sorted = decoherence_rates[sort_idx]
    contrast_sorted = contrasts[sort_idx]

    fig2, ax2 = plt.subplots(figsize=(6.0, 4.0), dpi=300)
    fig2.patch.set_facecolor("#FFFFFF")
    ax2.set_facecolor("#FFFFFF")

    # Main contrast curve vs decoherence rate (log scale x-axis)
    ax2.plot(
        gamma_sorted, contrast_sorted,
        color="#7C3AED", linewidth=2.4, marker="o", markersize=4.5,
        label=r"Directional Contrast $C$ (%)",
        zorder=3
    )

    # Operational detectability threshold (1.0% contrast)
    ax2.axhline(
        1.0,
        color="#DC2626", linestyle="--", linewidth=1.5,
        label=r"Operational Threshold ($C = 1.0\%$)",
        zorder=2
    )

    # Highlight threshold decoherence rate (where C ~ 1%)
    # C crosses 1% near gamma ~ 2.74 us^-1 (T2 ~ 0.36 us)
    crit_gamma = 1.0 / exp_res["experiment_2"]["computational_threshold_T2_contrast_us"]
    ax2.axvline(
        crit_gamma,
        color="#0284C7", linestyle=":", linewidth=1.5,
        label=rf"Critical Rate $\gamma \approx {crit_gamma:.2f}\ \mu\mathrm{{s}}^{{-1}}$",
        zorder=2
    )

    ax2.set_xscale("log")
    ax2.set_xlabel(r"Decoherence Rate $\gamma = 1/T_2$ ($\mu\mathrm{s}^{-1}$)", fontsize=11, fontweight="bold", labelpad=6)
    ax2.set_ylabel(r"Directional Contrast $C = \frac{\Delta\Phi_S}{\Phi_{S,\mathrm{max}}+\Phi_{S,\mathrm{min}}}$ (%)", fontsize=11, fontweight="bold", labelpad=6)
    ax2.set_title(r"Compass Contrast vs Decoherence Rate ($B = 50\ \mu\mathrm{T}$)", fontsize=11.5, fontweight="bold", pad=8)

    ax2.tick_params(axis="both", labelsize=10)
    ax2.grid(True, which="both", linestyle=":", alpha=0.5, color="#94A3B8")
    ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.95, edgecolor="#CBD5E1")

    # Callout text box
    ax2.text(
        0.05, 0.15,
        "Coherent Limit ($\\gamma \\to 0$): $C = 13.32\\%$\n"
        "Strong Decoherence ($\\gamma > 10\\ \\mu\\mathrm{s}^{-1}$): $C < 0.1\\%$\n"
        f"Critical Lifetime: $T_2 \\geq 0.36\\ \\mu$s for $C \\geq 1.0\\%$",
        transform=ax2.transAxes,
        fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#F8FAFC", edgecolor="#CBD5E1", alpha=0.95)
    )

    fig2.tight_layout()

    # Save contrast vs decoherence plot
    for dest in [PROJECT_ROOT / "contrast_vs_decoherence.png", PROJECT_ROOT / "results" / "contrast_vs_decoherence.png", PROJECT_ROOT / "docs" / "figures" / "contrast_vs_decoherence.png"]:
        fig2.savefig(dest, dpi=300, bbox_inches="tight")
    plt.close(fig2)
    print("Saved contrast_vs_decoherence.png (6x4 inches, 300 DPI)")


if __name__ == "__main__":
    generate_plots()
