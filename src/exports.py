"""
Reproducibility and artifact export manager for Quantum Compass Lab.

Generates:
- Experiment CSV tables.
- JSON configuration snapshots.
- LaTeX / Markdown mathematical model equations.
- Validation audit reports.
- Comprehensive experiment summary reports.
"""

from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from src.spin_model import SpinModelConfig
from src.experiment_runner import AngularSweepResult
from src.validation import ValidationSuite, ValidationTestResult


def export_experiment_csv(sweep_result: AngularSweepResult, filepath: Path | str) -> Path:
    """Export angular sweep data to CSV."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = sweep_result.to_dataframe()
    df["B_uT"] = sweep_result.config.B_magnitude
    df["gamma_dephasing_us"] = sweep_result.config.gamma_dephasing
    df.to_csv(path, index=False)
    return path


def export_config_json(config: SpinModelConfig, filepath: Path | str) -> Path:
    """Export experiment configuration to JSON."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    cfg_dict = {
        "B_magnitude_uT": config.B_magnitude,
        "theta_rad": config.theta,
        "phi_rad": config.phi,
        "A_xx_rad_per_us": config.A_xx,
        "A_yy_rad_per_us": config.A_yy,
        "A_zz_rad_per_us": config.A_zz,
        "k_S_per_us": config.k_S,
        "k_T_per_us": config.k_T,
        "gamma_dephasing_per_us": config.gamma_dephasing,
        "gamma_relaxation_per_us": config.gamma_relaxation,
        "include_nuclear_zeeman": config.include_nuclear_zeeman,
        "zeeman_omega_rad_per_us": config.zeeman_omega,
        "coherence_time_T2_us": config.coherence_time_T2,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg_dict, f, indent=2)
    return path


def export_validation_report_json(results: list[ValidationTestResult], filepath: Path | str) -> Path:
    """Export test suite audit results to JSON."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "name": r.name,
            "passed": r.passed,
            "description": r.description,
            "numerical_metric": r.numerical_metric,
            "tolerance": r.tolerance,
            "details": r.details,
        }
        for r in results
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def generate_experiment_report_md(sweep_result: AngularSweepResult) -> str:
    """Generate a clean markdown report of the simulation run."""
    m = sweep_result.metrics
    cfg = sweep_result.config

    report = f"""# Quantum Compass Lab — Experiment Summary Report

## System Parameters
- **External Magnetic Field ($B$):** {cfg.B_magnitude:.1f} $\\mu$T
- **Zeeman Frequency ($\\omega_0$):** {cfg.zeeman_omega:.3f} rad/$\\mu$s
- **Hyperfine Tensor:** $\\mathbf{{A}} = \\mathrm{{diag}}({cfg.A_xx:.1f}, {cfg.A_yy:.1f}, {cfg.A_zz:.1f})$ rad/$\\mu$s
- **Recombination Rates:** $k_S = {cfg.k_S:.2f}\\ \\mu\\mathrm{{s}}^{{-1}}$, $k_T = {cfg.k_T:.2f}\\ \\mu\\mathrm{{s}}^{{-1}}$
- **Spin Dephasing Rate ($\\gamma$):** {cfg.gamma_dephasing:.3f} $\\mu\\mathrm{{s}}^{{-1}}$ (Coherence Time $T_2$: {f'{cfg.coherence_time_T2:.2f} us' if cfg.coherence_time_T2 else 'Infinite'})

## Computed Directional Metrics
- **Minimum Singlet Yield ($\\Phi_{{S,\\mathrm{{min}}}}$):** {m.phi_s_min:.5f} at $\\theta = {m.theta_min_deg:.1f}^\\circ$
- **Maximum Singlet Yield ($\\Phi_{{S,\\mathrm{{max}}}}$):** {m.phi_s_max:.5f} at $\\theta = {m.theta_max_deg:.1f}^\\circ$
- **Mean Singlet Yield ($\\bar{{\\Phi}}_S$):** {m.phi_s_mean:.5f}
- **Absolute Anisotropy ($\\Delta\\Phi_S$):** {m.absolute_anisotropy:.5f}
- **Normalized Compass Contrast ($C$):** {m.contrast * 100.0:.2f}%
- **Operational Detectability Status:** {'DETECTABLE' if m.is_detectable else 'BELOW THRESHOLD'} (Threshold: {m.detectability_threshold:.4f})

## Scientific Interpretation
The simulation evaluates the 3-spin radical pair $[S_1, S_2, I]$ starting in an unpolarized nuclear ensemble with initial electron singlet character.
The anisotropic hyperfine coupling breaks spherical rotational symmetry, causing orientation-dependent singlet-triplet interconversion.
"""
    return report


def get_model_equations_markdown() -> str:
    """Return documented model equations in LaTeX/Markdown."""
    return r"""
### Radical-Pair Spin Hamiltonian
$$H = H_Z + H_{\mathrm{hf}}$$

$$H_Z = \omega_0 \mathbf{b} \cdot (\mathbf{S}_1 + \mathbf{S}_2) = \gamma_e B \left[ \sin\theta\cos\phi (S_{1x}+S_{2x}) + \sin\theta\sin\phi (S_{1y}+S_{2y}) + \cos\theta (S_{1z}+S_{2z}) \right]$$

$$H_{\mathrm{hf}} = \mathbf{S}_1 \cdot \mathbf{A} \cdot \mathbf{I} = A_{xx} S_{1x} I_x + A_{yy} S_{1y} I_y + A_{zz} S_{1z} I_z$$

### Haberkorn Reaction Master Equation
$$\frac{d\rho}{dt} = -i[H, \rho] - \frac{k_S}{2}\{P_S, \rho\} - \frac{k_T}{2}\{P_T, \rho\} + \mathcal{L}_{\mathrm{decoh}}(\rho)$$

### Singlet Reaction Yield
$$\Phi_S = k_S \int_0^\infty \mathrm{Tr}[P_S \rho(t)] \, dt = -k_S \mathrm{Tr}\left[ P_S \mathcal{M}^{-1} \rho(0) \right]$$

### Compass Contrast Metric
$$C = \frac{\Phi_{S,\mathrm{max}} - \Phi_{S,\mathrm{min}}}{\Phi_{S,\mathrm{max}} + \Phi_{S,\mathrm{min}}}$$
"""
