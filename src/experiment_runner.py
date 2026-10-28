"""
Scientific experiment runner for radical-pair magnetoreception.

Executes and coordinates the standardized experiment suite:
- Experiment 1: Angular Response Sweep across Earth's field range (25 - 65 uT).
- Experiment 2: Decoherence & Coherence-Time (T2) Analysis.
- Experiment 3: Hyperfine Anisotropy Sensitivity.
- Experiment 4: Reaction Kinetics Sensitivity (k_S vs k_T).
- Experiment 5: Numerical Convergence Verification (Trotter steps & integration bounds).
- Experiment 6: Isotropic vs Anisotropic Model Comparison (Rotational symmetry validation).
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
import json
import numpy as np
import pandas as pd
from pathlib import Path

from src.spin_model import SpinModelConfig
from src.initial_states import get_initial_density_matrix, get_pure_singlet_nuclear_states
from src.reaction_kinetics import calculate_yields_exact
from src.evolution import simulate_time_trajectory, integrate_yield_numerically, evolve_unitary
from src.hamiltonian import build_total_hamiltonian
from src.operators import get_singlet_projector_3spin
from src.qiskit_backend import simulate_qiskit_evolution
from src.metrics import calculate_compass_metrics, CompassMetrics
from src.plotting import (
    plot_angular_response,
    plot_decoherence_comparison,
    plot_contrast_decay,
    apply_research_theme
)
import matplotlib.pyplot as plt


@dataclass
class AngularSweepResult:
    thetas_deg: list[float]
    singlet_yields: list[float]
    triplet_yields: list[float]
    metrics: CompassMetrics
    config: SpinModelConfig

    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame({
            "theta_deg": self.thetas_deg,
            "singlet_yield": self.singlet_yields,
            "triplet_yield": self.triplet_yields,
        })
        return df


def run_angular_sweep(
    config: SpinModelConfig,
    num_angles: int = 73,  # 0 to 180 degrees in 2.5 deg steps
    theta_max_deg: float = 180.0
) -> AngularSweepResult:
    """
    Execute angular sweep of field orientation theta and compute exact reaction yields.
    """
    thetas_deg = np.linspace(0.0, theta_max_deg, num_angles)
    thetas_rad = np.deg2rad(thetas_deg)
    rho_0 = get_initial_density_matrix()

    phi_s_list: list[float] = []
    phi_t_list: list[float] = []

    for th in thetas_rad:
        cfg = SpinModelConfig(
            B_magnitude=config.B_magnitude,
            theta=th,
            phi=config.phi,
            A_xx=config.A_xx,
            A_yy=config.A_yy,
            A_zz=config.A_zz,
            k_S=config.k_S,
            k_T=config.k_T,
            gamma_dephasing=config.gamma_dephasing,
            gamma_relaxation=config.gamma_relaxation,
            dephasing_model=config.dephasing_model,
            include_nuclear_zeeman=config.include_nuclear_zeeman
        )
        ys, yt = calculate_yields_exact(rho_0, cfg)
        phi_s_list.append(ys)
        phi_t_list.append(yt)

    yields_s = np.array(phi_s_list)
    metrics = calculate_compass_metrics(thetas_rad, yields_s)

    return AngularSweepResult(
        thetas_deg=thetas_deg.tolist(),
        singlet_yields=phi_s_list,
        triplet_yields=phi_t_list,
        metrics=metrics,
        config=config
    )


def run_experiment_1_angular_response(results_dir: Path | str = "results") -> dict:
    """
    Experiment 1: Angular response at 50 uT (Earth field) and 25 uT, 65 uT.
    """
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fields_ut = [25.0, 50.0, 65.0]
    sweep_results: dict[float, AngularSweepResult] = {}

    for b in fields_ut:
        cfg = SpinModelConfig(B_magnitude=b, A_xx=5.0, A_yy=5.0, A_zz=20.0, k_S=1.0, k_T=1.0)
        res = run_angular_sweep(cfg, num_angles=91, theta_max_deg=180.0)
        sweep_results[b] = res

    # Plot 50 uT main result
    res_50 = sweep_results[50.0]
    fig = plot_angular_response(
        np.array(res_50.thetas_deg),
        np.array(res_50.singlet_yields),
        res_50.metrics,
        title="Experiment 1: Radical-Pair Singlet Yield vs Field Angle (B = 50 uT)",
        field_label="B = 50 uT"
    )
    fig.savefig(out_dir / "angular_response.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Save CSV
    df = res_50.to_dataframe()
    df["B_uT"] = 50.0
    for b in [25.0, 65.0]:
        df_b = sweep_results[b].to_dataframe()
        df_b["B_uT"] = b
        df = pd.concat([df, df_b], ignore_index=True)
    df.to_csv(out_dir / "experiment_1_angular_response.csv", index=False)

    return {
        "sweep_50uT": res_50.metrics.to_dict(),
        "sweep_25uT": sweep_results[25.0].metrics.to_dict(),
        "sweep_65uT": sweep_results[65.0].metrics.to_dict(),
    }


def run_experiment_2_decoherence(results_dir: Path | str = "results") -> dict:
    """
    Experiment 2: Decoherence sweep from ideal (gamma=0) to strong dephasing.
    """
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Coherence times T2 from 20 us down to 0.05 us (gamma = 0.05 to 20 us^-1)
    gammas = [0.0, 0.1, 0.5, 2.0, 10.0]
    labels = ["Ideal (T2 = inf)", "T2 = 10 us", "T2 = 2 us", "T2 = 0.5 us", "T2 = 0.1 us"]
    yields_dict: dict[str, np.ndarray] = {}

    thetas_deg: np.ndarray | None = None
    for gamma, label in zip(gammas, labels):
        cfg = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0, gamma_dephasing=gamma)
        res = run_angular_sweep(cfg, num_angles=61)
        thetas_deg = np.array(res.thetas_deg)
        yields_dict[label] = np.array(res.singlet_yields)

    fig = plot_decoherence_comparison(thetas_deg, yields_dict, title="Experiment 2: Compass Response vs Decoherence Rate")
    fig.savefig(out_dir / "decoherence_comparison.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Fine sweep of contrast and absolute anisotropy vs coherence time
    coherence_times = np.logspace(-1.5, 1.3, 30)  # ~0.03 us to ~20 us
    contrasts = []
    anisotropies = []
    for t2 in coherence_times:
        gamma = 1.0 / t2
        cfg = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0, gamma_dephasing=gamma)
        res = run_angular_sweep(cfg, num_angles=25)
        contrasts.append(res.metrics.contrast)
        anisotropies.append(res.metrics.absolute_anisotropy)

    # Compute model-dependent computational thresholds
    thresh_anisotropy = 0.001  # 0.1% absolute yield change
    thresh_contrast = 0.01    # 1.0% normalized contrast
    t2_thresh_aniso = None
    t2_thresh_contrast = None

    for t2, aniso, c in zip(coherence_times, anisotropies, contrasts):
        if aniso >= thresh_anisotropy and t2_thresh_aniso is None:
            t2_thresh_aniso = float(t2)
        if c >= thresh_contrast and t2_thresh_contrast is None:
            t2_thresh_contrast = float(t2)

    fig2 = plot_contrast_decay(coherence_times, np.array(contrasts))
    fig2.savefig(out_dir / "contrast_sweep.png", dpi=300, bbox_inches="tight")
    plt.close(fig2)

    return {
        "coherence_times_explored_us": [float(t) for t in coherence_times],
        "contrasts": contrasts,
        "anisotropies": anisotropies,
        "computational_threshold_T2_anisotropy_us": t2_thresh_aniso,
        "computational_threshold_T2_contrast_us": t2_thresh_contrast,
        "threshold_criterion": "Model-dependent computational threshold (Delta_Phi_S >= 0.001, C >= 0.01), not a biological threshold."
    }


def run_experiment_3_hyperfine_sensitivity(results_dir: Path | str = "results") -> dict:
    """
    Experiment 3: Varying hyperfine anisotropy ratio A_zz / A_xx.
    """
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    anisotropy_ratios = [1.0, 2.0, 4.0, 8.0]
    res_dict: dict[str, np.ndarray] = {}
    thetas_deg: np.ndarray | None = None

    for ratio in anisotropy_ratios:
        a_xx = 5.0
        a_zz = 5.0 * ratio
        cfg = SpinModelConfig(B_magnitude=50.0, A_xx=a_xx, A_yy=a_xx, A_zz=a_zz)
        res = run_angular_sweep(cfg, num_angles=61)
        thetas_deg = np.array(res.thetas_deg)
        label = f"Isotropic (A_zz/A_xx=1)" if ratio == 1.0 else f"A_zz/A_xx = {ratio:.0f}"
        res_dict[label] = np.array(res.singlet_yields)

    fig, ax = plt.subplots(figsize=(8.5, 5.0), dpi=150)
    apply_research_theme(fig, ax)
    colors = ["#94A3B8", "#38BDF8", "#34D399", "#FB7185"]
    for idx, (lbl, y) in enumerate(res_dict.items()):
        ax.plot(thetas_deg, y, color=colors[idx % len(colors)], linewidth=2.2, label=lbl)

    ax.set_xlabel("Polar Angle $\\theta$ (degrees)", fontsize=11)
    ax.set_ylabel("Integrated Singlet Yield $\\Phi_S$", fontsize=11)
    ax.set_title("Experiment 3: Directional Response vs Hyperfine Anisotropy Ratio", fontsize=12, fontweight="bold", pad=12)
    ax.legend(facecolor="#0B1120", edgecolor="#334155", labelcolor="#F8FAFC")
    fig.tight_layout()
    fig.savefig(out_dir / "hyperfine_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    return {"ratios": anisotropy_ratios}


def run_experiment_5_convergence(results_dir: Path | str = "results") -> dict:
    """
    Experiment 5: Numerical convergence of time integration and Trotter decomposition.
    Separates time-domain truncation error from numerical quadrature error,
    and measures full state norm error and unitary operator error for Trotter evolution.
    """
    from src.evolution import compute_exact_truncated_yield, separate_truncation_and_quadrature_errors
    from src.qiskit_backend import compute_trotter_convergence_metrics

    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = SpinModelConfig(B_magnitude=50.0, theta=np.pi / 4.0, A_xx=5.0, A_yy=5.0, A_zz=20.0)
    rho_0 = get_initial_density_matrix()

    # 1. Horizon truncation tails
    t_horizons = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0]
    phi_s_exact, _ = calculate_yields_exact(rho_0, cfg)
    truncation_tails = []
    for t_max in t_horizons:
        phi_trunc = compute_exact_truncated_yield(rho_0, cfg, t_max)
        truncation_tails.append(abs(phi_s_exact - phi_trunc))

    # 2. Quadrature error vs time step resolution dt (at fixed t_max = 5.0 us)
    fixed_t_max = 5.0
    phi_fixed_exact = compute_exact_truncated_yield(rho_0, cfg, fixed_t_max)
    dt_resolutions = [0.2, 0.1, 0.05, 0.02, 0.01, 0.005]
    quadrature_errors = []
    for dt in dt_resolutions:
        n_pts = int(np.round(fixed_t_max / dt)) + 1
        times, p_s, _ = simulate_time_trajectory(rho_0, cfg, t_span=(0.0, fixed_t_max), num_points=n_pts)
        phi_num = integrate_yield_numerically(times, p_s, cfg.k_S)
        quadrature_errors.append(abs(phi_num - phi_fixed_exact))

    # 3. Trotter convergence on noncommuting Hamiltonian
    reps_list = [1, 2, 4, 8, 16, 32]
    trotter_results_t05 = compute_trotter_convergence_metrics(cfg, times=[0.5], reps_list=reps_list)
    trotter_results_t10 = compute_trotter_convergence_metrics(cfg, times=[1.0], reps_list=reps_list)

    # Plot 3-panel convergence figure
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.6), dpi=150)
    apply_research_theme(fig, [ax1, ax2, ax3])

    # Panel 1: Exact Finite-Horizon Tail Difference
    # NOTE: This is the EXACT finite-horizon tail difference computed via Liouvillian matrix
    # integration: |Phi_S(inf) - Phi_S(t_max)|. This is NOT an analytical upper bound.
    ax1.semilogy(t_horizons, truncation_tails, color="#38BDF8", marker="o", linewidth=2.0)
    ax1.set_xlabel("Integration Horizon $t_{\\mathrm{max}}$ ($\\mu$s)", fontsize=10)
    ax1.set_ylabel("Exact Finite-Horizon Tail $|\\Phi_S(\\infty) - \\Phi_S^{\\mathrm{exact}}(t_{\\mathrm{max}})|$", fontsize=10)
    ax1.set_title("1. Finite-Horizon Tail Difference (Exact)", fontsize=11, fontweight="bold")

    # Panel 2: Numerical Quadrature Error (Trapezoidal Rule, O(dt^2))
    # The yield is integrated using numpy.trapezoid (composite trapezoidal rule).
    # This gives O(dt^2) global convergence, NOT O(dt^4). The O(dt^4) accuracy of the
    # RK45 solver applies only to the ODE solution for rho(t), not to the final quadrature.
    ax2.loglog(dt_resolutions, quadrature_errors, color="#34D399", marker="^", linewidth=2.0)
    ax2.set_xlabel("Time Step Resolution $\\Delta t$ ($\\mu$s)", fontsize=10)
    ax2.set_ylabel("Quadrature Error $|\\Phi_S^{\\mathrm{num}} - \\Phi_S^{\\mathrm{exact}}(t_{\\mathrm{max}})|$", fontsize=10)
    ax2.set_title("2. Trapezoidal Quadrature Convergence ($O(\\Delta t^2)$)", fontsize=11, fontweight="bold")

    # Panel 3: Lie-Trotter Operator & State Error
    ax3.loglog(reps_list, trotter_results_t05["state_norm_error"], color="#A78BFA", marker="s", linewidth=2.0, label=r"State Err ($t=0.5\ \mu$s)")
    ax3.loglog(reps_list, trotter_results_t10["state_norm_error"], color="#FB7185", marker="d", linewidth=2.0, label=r"State Err ($t=1.0\ \mu$s)")
    ax3.loglog(reps_list, trotter_results_t05["unitary_error"], color="#FBBF24", linestyle="--", linewidth=1.8, label=r"Unitary $\|U-U_{\mathrm{ex}}\|_F$")
    ax3.set_xlabel("Trotter Repetitions $r$", fontsize=10)
    ax3.set_ylabel("Discretization Error", fontsize=10)
    ax3.set_title("3. Lie-Trotter Convergence ($O(1/r)$)", fontsize=11, fontweight="bold")
    ax3.legend(facecolor="#0B1120", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8.5)

    fig.tight_layout()
    fig.savefig(out_dir / "convergence.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    return {
        "phi_s_exact_inf": phi_s_exact,
        "t_horizons": t_horizons,
        "truncation_tails": truncation_tails,
        "dt_resolutions": dt_resolutions,
        "quadrature_errors": quadrature_errors,
        "trotter_reps": reps_list,
        "trotter_state_errors_t05": trotter_results_t05["state_norm_error"],
        "trotter_state_errors_t10": trotter_results_t10["state_norm_error"],
        "trotter_unitary_errors_t05": trotter_results_t05["unitary_error"],
    }


def run_experiment_6_symmetry_comparison(results_dir: Path | str = "results") -> dict:
    """
    Experiment 6: Direct proof of rotational symmetry in isotropic vs anisotropic model.
    """
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg_iso = SpinModelConfig(B_magnitude=50.0, A_xx=10.0, A_yy=10.0, A_zz=10.0)
    res_iso = run_angular_sweep(cfg_iso, num_angles=45)

    cfg_aniso = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0)
    res_aniso = run_angular_sweep(cfg_aniso, num_angles=45)

    return {
        "isotropic_contrast": res_iso.metrics.contrast,
        "isotropic_anisotropy": res_iso.metrics.absolute_anisotropy,
        "anisotropic_contrast": res_aniso.metrics.contrast,
        "anisotropic_anisotropy": res_aniso.metrics.absolute_anisotropy,
    }


def run_all_experiments(results_dir: Path | str = "results") -> dict:
    """Run full experimental pipeline and save consolidated data."""
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "experiment_1": run_experiment_1_angular_response(out_dir),
        "experiment_2": run_experiment_2_decoherence(out_dir),
        "experiment_3": run_experiment_3_hyperfine_sensitivity(out_dir),
        "experiment_5": run_experiment_5_convergence(out_dir),
        "experiment_6": run_experiment_6_symmetry_comparison(out_dir),
    }

    with open(out_dir / "experiment_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary
