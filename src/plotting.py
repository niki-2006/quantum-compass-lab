"""
Publication-quality scientific visualization for Quantum Compass Lab.

Aesthetic Guidelines:
- Professional scientific styling matching dark laboratory UI (#0B132B / #1C2541).
- Crisp cyan (#00F0FF / #38BDF8) and violet (#A78BFA) accents.
- Clear physical units, readable legends, high DPI exports.
"""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from src.metrics import CompassMetrics


# Professional dark research theme palette
STYLE_CONFIG = {
    "bg_dark": "#0B1120",
    "bg_card": "#1E293B",
    "text_main": "#F8FAFC",
    "text_muted": "#94A3B8",
    "grid_color": "#334155",
    "cyan_primary": "#38BDF8",
    "violet_accent": "#A78BFA",
    "emerald_green": "#34D399",
    "rose_accent": "#FB7185",
    "amber_accent": "#FBBF24",
}


def apply_research_theme(fig: Figure, ax: plt.Axes | list[plt.Axes]) -> None:
    """Apply unified dark scientific theme to figure and axes."""
    fig.patch.set_facecolor(STYLE_CONFIG["bg_dark"])
    axes = [ax] if not isinstance(ax, (list, np.ndarray)) else np.ravel(ax)

    for a in axes:
        a.set_facecolor(STYLE_CONFIG["bg_card"])
        a.tick_params(colors=STYLE_CONFIG["text_muted"], labelsize=10)
        a.xaxis.label.set_color(STYLE_CONFIG["text_main"])
        a.yaxis.label.set_color(STYLE_CONFIG["text_main"])
        a.title.set_color(STYLE_CONFIG["text_main"])
        for spine in a.spines.values():
            spine.set_color(STYLE_CONFIG["grid_color"])
            spine.set_linewidth(1.0)
        a.grid(True, linestyle="--", alpha=0.35, color=STYLE_CONFIG["grid_color"])


def plot_angular_response(
    thetas_deg: np.ndarray,
    yields: np.ndarray,
    metrics: CompassMetrics,
    title: str = "Radical-Pair Compass Angular Response",
    field_label: str = "B = 50 uT"
) -> Figure:
    """
    Plot singlet reaction yield Phi_S versus magnetic-field orientation theta.
    """
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
    apply_research_theme(fig, ax)

    ax.plot(
        thetas_deg, yields,
        color=STYLE_CONFIG["cyan_primary"],
        linewidth=2.5,
        label=f"Singlet Yield $\\Phi_S$ ({field_label})"
    )

    # Highlight Extrema
    ax.scatter(
        [metrics.theta_max_deg], [metrics.phi_s_max],
        color=STYLE_CONFIG["emerald_green"], s=80, zorder=5,
        label=f"Max: {metrics.phi_s_max:.4f} @ {metrics.theta_max_deg:.0f}°"
    )
    ax.scatter(
        [metrics.theta_min_deg], [metrics.phi_s_min],
        color=STYLE_CONFIG["rose_accent"], s=80, zorder=5,
        label=f"Min: {metrics.phi_s_min:.4f} @ {metrics.theta_min_deg:.0f}°"
    )

    ax.set_xlabel("Magnetic Field Polar Angle $\\theta$ (degrees)", fontsize=11, fontweight="medium")
    ax.set_ylabel("Integrated Singlet Yield $\\Phi_S$", fontsize=11, fontweight="medium")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    # Info box for contrast
    contrast_text = (
        f"Contrast $C$: {metrics.contrast * 100:.2f}%\n"
        f"$\\Delta\\Phi_S$: {metrics.absolute_anisotropy:.4f}\n"
        f"Status: {'Detectable' if metrics.is_detectable else 'Sub-threshold'}"
    )
    ax.text(
        0.03, 0.05, contrast_text,
        transform=ax.transAxes,
        fontsize=9.5,
        color=STYLE_CONFIG["text_main"],
        bbox=dict(boxstyle="round,pad=0.5", facecolor=STYLE_CONFIG["bg_dark"], edgecolor=STYLE_CONFIG["grid_color"], alpha=0.9)
    )

    ax.legend(facecolor=STYLE_CONFIG["bg_dark"], edgecolor=STYLE_CONFIG["grid_color"], labelcolor=STYLE_CONFIG["text_main"])
    fig.tight_layout()
    return fig


def plot_decoherence_comparison(
    thetas_deg: np.ndarray,
    yields_dict: dict[str, np.ndarray],
    title: str = "Compass Response Under Progressive Decoherence"
) -> Figure:
    """
    Plot angular response curves for varying decoherence rates.
    """
    fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=150)
    apply_research_theme(fig, ax)

    colors = [
        STYLE_CONFIG["cyan_primary"],
        STYLE_CONFIG["emerald_green"],
        STYLE_CONFIG["amber_accent"],
        STYLE_CONFIG["rose_accent"],
        STYLE_CONFIG["violet_accent"]
    ]

    for idx, (label, y_vals) in enumerate(yields_dict.items()):
        color = colors[idx % len(colors)]
        style = "-" if "Ideal" in label or idx == 0 else "--"
        ax.plot(thetas_deg, y_vals, color=color, linestyle=style, linewidth=2.2, label=label)

    ax.set_xlabel("Magnetic Field Polar Angle $\\theta$ (degrees)", fontsize=11)
    ax.set_ylabel("Integrated Singlet Yield $\\Phi_S$", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    ax.legend(facecolor=STYLE_CONFIG["bg_dark"], edgecolor=STYLE_CONFIG["grid_color"], labelcolor=STYLE_CONFIG["text_main"])
    fig.tight_layout()
    return fig


def plot_contrast_decay(
    coherence_times_us: np.ndarray,
    contrasts: np.ndarray,
    threshold: float = 0.001
) -> Figure:
    """
    Plot compass contrast C versus spin coherence time T2.
    """
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
    apply_research_theme(fig, ax)

    ax.plot(
        coherence_times_us, contrasts * 100.0,
        color=STYLE_CONFIG["violet_accent"],
        marker="o", markersize=5, linewidth=2.2,
        label="Compass Contrast $C$ (%)"
    )

    ax.set_xlabel("Coherence Time $T_2$ ($\\mu$s)", fontsize=11)
    ax.set_ylabel("Compass Contrast (%)", fontsize=11)
    ax.set_title("Compass Contrast vs. Spin Coherence Lifetime", fontsize=12, fontweight="bold", pad=12)
    ax.legend(facecolor=STYLE_CONFIG["bg_dark"], edgecolor=STYLE_CONFIG["grid_color"], labelcolor=STYLE_CONFIG["text_main"])
    fig.tight_layout()
    return fig


def plot_time_dynamics(
    times_us: np.ndarray,
    p_singlet: np.ndarray,
    surviving_fraction: np.ndarray,
    title: str = "Radical-Pair Time Dynamics & Recombination"
) -> Figure:
    """
    Plot instantaneous singlet probability p_S(t) and surviving radical pair population.
    """
    fig, ax1 = plt.subplots(figsize=(8.5, 4.8), dpi=150)
    apply_research_theme(fig, ax1)

    line1 = ax1.plot(times_us, p_singlet, color=STYLE_CONFIG["cyan_primary"], linewidth=2.2, label="$p_S(t)$ Singlet Probability")
    ax1.set_xlabel("Time $t$ ($\\mu$s)", fontsize=11)
    ax1.set_ylabel("Singlet Probability $p_S(t)$", color=STYLE_CONFIG["cyan_primary"], fontsize=11)

    ax2 = ax1.twinx()
    line2 = ax2.plot(times_us, surviving_fraction, color=STYLE_CONFIG["amber_accent"], linestyle="--", linewidth=2.0, label="$\\mathrm{Tr}[\\rho(t)]$ Surviving Fraction")
    ax2.set_ylabel("Surviving Fraction $\\mathrm{Tr}[\\rho(t)]$", color=STYLE_CONFIG["amber_accent"], fontsize=11)
    ax2.tick_params(colors=STYLE_CONFIG["text_muted"], labelsize=10)
    for spine in ax2.spines.values():
        spine.set_color(STYLE_CONFIG["grid_color"])

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", facecolor=STYLE_CONFIG["bg_dark"], edgecolor=STYLE_CONFIG["grid_color"], labelcolor=STYLE_CONFIG["text_main"])
    ax1.set_title(title, fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    return fig
