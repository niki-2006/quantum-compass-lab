"""
Metrics and sensitivity analysis for radical-pair magnetoreception.

Definitions:
- Compass Contrast:
    C = (Phi_S_max - Phi_S_min) / (Phi_S_max + Phi_S_min)
  Provides normalized directional modulation depth.
- Absolute Yield Anisotropy:
    Delta_Phi_S = Phi_S_max - Phi_S_min
  Provides raw signal magnitude.
- Operational Detectability Criterion:
    A compass signal is operationally detectable in our model if Delta_Phi_S >= threshold_yield
    (e.g., threshold_yield = 0.001 = 0.1% change in reaction yield).
    Note: This is an explicit computational/engineering threshold, not a proven biological limit.
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class CompassMetrics:
    """Quantitative directional metrics for an angular response sweep."""
    phi_s_min: float
    phi_s_max: float
    phi_s_mean: float
    theta_min_deg: float
    theta_max_deg: float
    absolute_anisotropy: float  # Delta Phi_S = max - min
    contrast: float            # (max - min) / (max + min)
    is_detectable: bool        # whether absolute anisotropy exceeds threshold
    detectability_threshold: float

    def to_dict(self) -> dict[str, float | bool]:
        return {
            "phi_s_min": self.phi_s_min,
            "phi_s_max": self.phi_s_max,
            "phi_s_mean": self.phi_s_mean,
            "theta_min_deg": self.theta_min_deg,
            "theta_max_deg": self.theta_max_deg,
            "absolute_anisotropy": self.absolute_anisotropy,
            "contrast": self.contrast,
            "is_detectable": self.is_detectable,
            "detectability_threshold": self.detectability_threshold,
        }


def calculate_compass_metrics(
    thetas_rad: np.ndarray,
    singlet_yields: np.ndarray,
    threshold: float = 0.001
) -> CompassMetrics:
    """
    Calculate compass contrast, extrema, and detectability from angular sweep results.

    Args:
        thetas_rad: 1D array of angles in radians.
        singlet_yields: 1D array of calculated singlet yields Phi_S.
        threshold: Absolute yield variation threshold for operational detectability.

    Returns:
        CompassMetrics object.
    """
    min_idx = int(np.argmin(singlet_yields))
    max_idx = int(np.argmax(singlet_yields))

    y_min = float(singlet_yields[min_idx])
    y_max = float(singlet_yields[max_idx])
    y_mean = float(np.mean(singlet_yields))

    delta_y = y_max - y_min
    denom = y_max + y_min
    contrast = float(delta_y / denom) if denom > 1e-12 else 0.0

    thetas_deg = np.rad2deg(thetas_rad)
    th_min = float(thetas_deg[min_idx])
    th_max = float(thetas_deg[max_idx])

    is_det = bool(delta_y >= threshold)

    return CompassMetrics(
        phi_s_min=y_min,
        phi_s_max=y_max,
        phi_s_mean=y_mean,
        theta_min_deg=th_min,
        theta_max_deg=th_max,
        absolute_anisotropy=delta_y,
        contrast=contrast,
        is_detectable=is_det,
        detectability_threshold=threshold,
    )
