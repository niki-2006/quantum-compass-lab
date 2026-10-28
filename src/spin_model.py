"""
SpinModel configuration and parameters for radical-pair simulation.

Provides a clean, strongly typed configuration dataclass capturing:
- Magnetic field vector B (magnitude, polar angle theta, azimuthal angle phi).
- Hyperfine tensor A (diagonal components A_xx, A_yy, A_zz in rad/microsecond).
- Recombination rates k_S and k_T (in 1/microsecond).
- Decoherence rates (dephasing gamma_deph, relaxation gamma_rel).
"""

from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

# Physical constant: Electron gyromagnetic ratio
# gamma_e = g * mu_B / hbar ~ 176.08 rad / (microsecond * mT) = 0.17608 rad / (microsecond * microTesla)
GAMMA_E_RAD_PER_US_PER_UT: float = 0.17608596  # rad / (us * uT)
GAMMA_N_PROTON_RAD_PER_US_PER_UT: float = 0.0002675  # ~ 658 times smaller


@dataclass
class SpinModelConfig:
    """
    Configuration parameters for 3-spin radical pair system.

    Units:
        B_magnitude: microTesla (uT). Typical Earth field = 25 to 65 uT (default 50 uT).
        theta: polar angle in radians [0, pi] (angle between B and z-axis).
        phi: azimuthal angle in radians [0, 2*pi] (angle in xy-plane).
        A_xx, A_yy, A_zz: Hyperfine tensor diagonal elements in rad/microsecond.
        k_S: Singlet recombination rate in 1/microsecond (default 1.0 us^-1, lifetime ~ 1 us).
        k_T: Triplet recombination rate in 1/microsecond (default 1.0 us^-1).
        gamma_dephasing: Spin dephasing rate in 1/microsecond (default 0.0, coherence time T2 = 1/gamma).
        gamma_relaxation: Spin relaxation rate in 1/microsecond (default 0.0, T1 = 1/gamma).
        dephasing_model: 'isotropic_depolarizing' (isotropic 3D noise, T1=T2=1/gamma) or
                         'pure_dephasing' (axial phase damping along z, T1=inf, T2=1/gamma).
        include_nuclear_zeeman: whether to include the tiny nuclear Zeeman term (default False).
    """
    B_magnitude: float = 50.0  # uT (Earth's magnetic field)
    theta: float = 0.0         # radians
    phi: float = 0.0           # radians

    # Hyperfine tensor (rad/us)
    # Default is an anisotropic axial tensor characteristic of organic radicals
    A_xx: float = 5.0          # rad/us
    A_yy: float = 5.0          # rad/us
    A_zz: float = 20.0         # rad/us

    # Reaction kinetics (1/us)
    k_S: float = 1.0           # 1/us
    k_T: float = 1.0           # 1/us

    # Decoherence parameters (1/us)
    gamma_dephasing: float = 0.0   # 1/us
    gamma_relaxation: float = 0.0  # 1/us
    dephasing_model: str = "isotropic_depolarizing"  # 'isotropic_depolarizing' or 'pure_dephasing'

    include_nuclear_zeeman: bool = False

    @property
    def zeeman_omega(self) -> float:
        """Electron Zeeman angular frequency in rad/microsecond."""
        return GAMMA_E_RAD_PER_US_PER_UT * self.B_magnitude

    @property
    def field_unit_vector(self) -> np.ndarray:
        """Unit vector b = [sin(theta)cos(phi), sin(theta)sin(phi), cos(theta)]."""
        st = np.sin(self.theta)
        ct = np.cos(self.theta)
        sp = np.sin(self.phi)
        cp = np.cos(self.phi)
        return np.array([st * cp, st * sp, ct], dtype=float)

    @property
    def B_vector(self) -> np.ndarray:
        """Magnetic field vector B in microTesla."""
        return self.B_magnitude * self.field_unit_vector

    @property
    def is_isotropic_hyperfine(self) -> bool:
        """Check if hyperfine tensor is isotropic (A_xx == A_yy == A_zz)."""
        return bool(np.isclose(self.A_xx, self.A_yy) and np.isclose(self.A_yy, self.A_zz))

    @property
    def coherence_time_T2(self) -> float | None:
        """Transverse coherence time T2 = 1 / gamma_dephasing in microseconds (None if gamma=0)."""
        if self.gamma_dephasing > 1e-12:
            return 1.0 / self.gamma_dephasing
        return None
