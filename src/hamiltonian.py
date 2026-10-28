"""
Hamiltonian construction for the 3-spin radical-pair system.

The total Hamiltonian is:
    H = H_Z + H_hf

Where:
    H_Z = omega_0 * b . (S1 + S2) [+ omega_N * b . I]
    H_hf = S1 . A . I = A_xx * S1x * Ix + A_yy * S1y * Iy + A_zz * S1z * Iz

All operators act in the 8-dimensional Hilbert space (Electron 1 (x) Electron 2 (x) Nuclear spin).
Units: hbar = 1, frequencies in rad/microsecond.
"""

from __future__ import annotations
import numpy as np
from src.operators import get_spin_operators_3spin, is_hermitian
from src.spin_model import SpinModelConfig, GAMMA_N_PROTON_RAD_PER_US_PER_UT


def build_zeeman_hamiltonian(config: SpinModelConfig) -> np.ndarray:
    """
    Construct the Zeeman Hamiltonian H_Z in rad/us.

    H_Z = omega_0 * [ b_x (S1x + S2x) + b_y (S1y + S2y) + b_z (S1z + S2z) ]
          [+ omega_N * b . I if enabled]

    Returns:
        8x8 complex Hermitian matrix.
    """
    ops = get_spin_operators_3spin()
    bx, by, bz = config.field_unit_vector
    omega_0 = config.zeeman_omega

    hz = omega_0 * (
        bx * (ops["S1x"] + ops["S2x"]) +
        by * (ops["S1y"] + ops["S2y"]) +
        bz * (ops["S1z"] + ops["S2z"])
    )

    if config.include_nuclear_zeeman:
        omega_N = GAMMA_N_PROTON_RAD_PER_US_PER_UT * config.B_magnitude
        hz += omega_N * (bx * ops["Ix"] + by * ops["Iy"] + bz * ops["Iz"])

    return hz


def build_hyperfine_hamiltonian(config: SpinModelConfig) -> np.ndarray:
    """
    Construct the Hyperfine Hamiltonian H_hf in rad/us.

    H_hf = A_xx * S1x * Ix + A_yy * S1y * Iy + A_zz * S1z * Iz

    Returns:
        8x8 complex Hermitian matrix.
    """
    ops = get_spin_operators_3spin()
    hhf = (
        config.A_xx * (ops["S1x"] @ ops["Ix"]) +
        config.A_yy * (ops["S1y"] @ ops["Iy"]) +
        config.A_zz * (ops["S1z"] @ ops["Iz"])
    )
    return hhf


def build_total_hamiltonian(config: SpinModelConfig) -> np.ndarray:
    """
    Construct total Hamiltonian H = H_Z + H_hf.

    Returns:
        8x8 complex Hermitian matrix.
    """
    h_tot = build_zeeman_hamiltonian(config) + build_hyperfine_hamiltonian(config)
    if not is_hermitian(h_tot):
        raise ValueError("Constructed Hamiltonian is not Hermitian!")
    return h_tot
