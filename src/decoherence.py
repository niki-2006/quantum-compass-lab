"""
Decoherence models and Lindblad dissipators for radical-pair spin dynamics.

Models:
1. Pure Dephasing (T2 decay):
   Fluctuating local fields cause loss of transverse coherence.
   Jump operators: L_z1 = S1z, L_z2 = S2z with rate gamma_dephasing.
   In terms of Pauli Z: rate = gamma_dephasing / 4 (since S_z = sigma_z / 2).
2. Isotropic Dephasing:
   Isotropic environmental fluctuations acting symmetrically on all spin coordinates:
   L_alpha,j = S_j,alpha for alpha in {x, y, z}, j in {1, 2}.
3. Superoperator construction in Liouville-Fock space:
   vec(rho) where vec(A rho B) = (B^T (x) A) vec(rho).
"""

from __future__ import annotations
import numpy as np
from src.operators import get_spin_operators_3spin, IDENTITY_8
from src.spin_model import SpinModelConfig


def get_lindblad_dissipators(config: SpinModelConfig) -> list[tuple[np.ndarray, float]]:
    """
    Return list of (jump_operator, rate) tuples for the specified decoherence model.
    Jump operators act in 8D Hilbert space.
    """
    ops = get_spin_operators_3spin()
    dissipators: list[tuple[np.ndarray, float]] = []

    # Dephasing on Electron 1 and Electron 2
    if config.gamma_dephasing > 1e-12:
        rate = config.gamma_dephasing
        model = config.dephasing_model.lower()
        if model in ("pure_dephasing", "axial_z", "phase_damping"):
            # Pure Phase Damping (Dephasing along z):
            # Jump operators: L = sigma_z = 2 * S_z.
            # Master equation term: Gamma_z * D[sigma_z](rho).
            # d(rho_01)/dt = -2 * Gamma_z * rho_01.
            # Setting Gamma_z = gamma / 2 ensures transverse coherence decays as:
            # rho_01(t) = rho_01(0) * exp(-gamma * t), giving exactly T2 = 1 / gamma.
            # Populations are strictly conserved (T1 -> infinity).
            dissipators.append((2.0 * ops["S1z"], rate / 2.0))
            dissipators.append((2.0 * ops["S2z"], rate / 2.0))
        elif model in ("isotropic_depolarizing", "isotropic", "depolarizing"):
            # Isotropic Depolarizing Noise:
            # Environmental isotropic fluctuations along x, y, z coordinates.
            # Jump operators: L_alpha = sigma_alpha = 2 * S_alpha for alpha in {x, y, z}.
            # Master equation: sum_{alpha} Gamma_iso * D[sigma_alpha](rho) = 4 * Gamma_iso * (I/2 - rho).
            # d(rho_01)/dt = -4 * Gamma_iso * rho_01.
            # Setting Gamma_iso = gamma / 4 ensures transverse coherence decays as:
            # rho_01(t) = rho_01(0) * exp(-gamma * t), giving exactly T2 = T1 = 1 / gamma.
            iso_rate = rate / 4.0
            for op_name in ["S1x", "S1y", "S1z", "S2x", "S2y", "S2z"]:
                dissipators.append((2.0 * ops[op_name], iso_rate))
        else:
            raise ValueError(
                f"Unknown dephasing model '{config.dephasing_model}'. "
                "Supported: 'pure_dephasing' (or 'axial_z') and 'isotropic_depolarizing' (or 'isotropic')."
            )

    # Relaxation (T1) if specified
    if config.gamma_relaxation > 1e-12:
        rate = config.gamma_relaxation
        # Lowering operators: S_- = S_x - i S_y
        s1_minus = ops["S1x"] - 1.0j * ops["S1y"]
        s2_minus = ops["S2x"] - 1.0j * ops["S2y"]
        dissipators.append((s1_minus, rate))
        dissipators.append((s2_minus, rate))

    return dissipators


def lindblad_dissipator_action(rho: np.ndarray, L: np.ndarray) -> np.ndarray:
    """
    Calculate D[L](rho) = L rho L^dag - 0.5 * {L^dag L, rho}.
    """
    L_dag = L.conj().T
    L_dag_L = L_dag @ L
    return L @ rho @ L_dag - 0.5 * (L_dag_L @ rho + rho @ L_dag_L)


def compute_decoherence_rhs(rho: np.ndarray, config: SpinModelConfig) -> np.ndarray:
    """
    Compute total Lindblad decoherence contribution d(rho)/dt|_decoh = sum_k gamma_k D[L_k](rho).
    """
    dissipators = get_lindblad_dissipators(config)
    d_rho = np.zeros_like(rho, dtype=complex)
    for L, rate in dissipators:
        d_rho += rate * lindblad_dissipator_action(rho, L)
    return d_rho


def build_liouvillian_decoherence_superoperator(config: SpinModelConfig) -> np.ndarray:
    """
    Construct the 64x64 superoperator matrix L_decoh such that:
        vec(d(rho)/dt|_decoh) = L_decoh @ vec(rho)
    using the identity vec(A rho B) = (B^T (x) A) vec(rho).
    """
    dissipators = get_lindblad_dissipators(config)
    super_op = np.zeros((64, 64), dtype=complex)
    I = IDENTITY_8

    for L, rate in dissipators:
        L_dag = L.conj().T
        L_dag_L = L_dag @ L

        term1 = np.kron(L.conj(), L)
        term2 = 0.5 * np.kron(I, L_dag_L)
        term3 = 0.5 * np.kron(L_dag_L.T, I)

        super_op += rate * (term1 - term2 - term3)

    return super_op
