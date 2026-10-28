"""
Reaction kinetics and yield calculation for radical-pair magnetoreception.

Mathematical Model:
- Haberkorn reaction master equation:
    d(rho)/dt = -i [H, rho] - (k_S/2){P_S, rho} - (k_T/2){P_T, rho} + L_decoh(rho)
- Singlet and Triplet projectors in 8D: P_S, P_T = I_8 - P_S
- Singlet reaction yield:
    Phi_S = k_S * integral_0^infinity Tr[P_S rho(t)] dt
- Conservation of reaction products:
    Phi_S + Phi_T = 1.0 (all radical pairs eventually decay to singlet or triplet products).
"""

from __future__ import annotations
import numpy as np
from src.operators import get_singlet_projector_3spin, get_triplet_projector_3spin, IDENTITY_8
from src.hamiltonian import build_total_hamiltonian
from src.decoherence import build_liouvillian_decoherence_superoperator, compute_decoherence_rhs
from src.spin_model import SpinModelConfig


def compute_haberkorn_rhs(rho: np.ndarray, config: SpinModelConfig, H: np.ndarray | None = None) -> np.ndarray:
    """
    Compute d(rho)/dt under Haberkorn kinetics + Hamiltonian + Decoherence.

    d(rho)/dt = -i[H, rho] - (k_S/2){P_S, rho} - (k_T/2){P_T, rho} + L_decoh(rho)
    """
    if H is None:
        H = build_total_hamiltonian(config)

    p_s = get_singlet_projector_3spin()
    p_t = get_triplet_projector_3spin()

    # Coherent commutator
    d_rho = -1.0j * (H @ rho - rho @ H)

    # Haberkorn recombination anticommutators
    anti_s = p_s @ rho + rho @ p_s
    anti_t = p_t @ rho + rho @ p_t
    d_rho -= 0.5 * config.k_S * anti_s
    d_rho -= 0.5 * config.k_T * anti_t

    # Decoherence
    d_rho += compute_decoherence_rhs(rho, config)

    return d_rho


def build_total_liouvillian(config: SpinModelConfig, H: np.ndarray | None = None) -> np.ndarray:
    """
    Construct the total 64x64 Liouville superoperator matrix M such that:
        vec(d(rho)/dt) = M @ vec(rho)

    Includes:
    - Commutator -i[H, rho] -> -i(I (x) H - H^T (x) I)
    - Haberkorn sink -0.5*k_S{P_S, rho} -> -0.5*k_S(I (x) P_S + P_S^T (x) I)
    - Haberkorn sink -0.5*k_T{P_T, rho} -> -0.5*k_T(I (x) P_T + P_T^T (x) I)
    - Lindblad decoherence superoperator L_decoh
    """
    if H is None:
        H = build_total_hamiltonian(config)

    I = IDENTITY_8
    p_s = get_singlet_projector_3spin()
    p_t = get_triplet_projector_3spin()

    # Commutator superoperator
    L_H = -1.0j * (np.kron(I, H) - np.kron(H.T, I))

    # Haberkorn reaction superoperators
    K_S = -0.5 * config.k_S * (np.kron(I, p_s) + np.kron(p_s.T, I))
    K_T = -0.5 * config.k_T * (np.kron(I, p_t) + np.kron(p_t.T, I))

    # Decoherence superoperator
    L_decoh = build_liouvillian_decoherence_superoperator(config)

    M = L_H + K_S + K_T + L_decoh
    return M


def calculate_yields_exact(rho_0: np.ndarray, config: SpinModelConfig, H: np.ndarray | None = None) -> tuple[float, float]:
    """
    Compute exact time-integrated singlet and triplet yields via direct Liouvillian inversion:
        rho_int = integral_0^inf rho(t) dt = -M^{-1} @ vec(rho_0)
        Phi_S = k_S * Tr[P_S rho_int]
        Phi_T = k_T * Tr[P_T rho_int]

    Assumption: The total Liouvillian M must be non-singular. This requires that all
    population eventually decays to reaction products, i.e. k_S > 0 or k_T > 0 (or
    non-zero dissipation that drives the system to a unique steady state).
    If M is near-singular (condition number > 1e12), a ValueError is raised with a
    diagnostic rather than silently returning a numerically garbage result.

    Returns:
        tuple (Phi_S, Phi_T) of floats.

    Raises:
        ValueError: If the Liouvillian is near-singular (e.g. k_S = k_T = 0 with no
            relaxation sinks), because the infinite-time integral diverges in that case.
    """
    M = build_total_liouvillian(config, H=H)
    vec_rho_0 = rho_0.flatten(order='F')  # Column-major (standard vec operation)

    # Guard against near-singular Liouvillian before attempting inversion.
    # A singular M means there is no unique steady state and the infinite-time
    # integral of rho(t) diverges. This occurs when k_S = k_T = 0 and there are
    # no relaxation channels driving the system to a unique steady state.
    cond = np.linalg.cond(M)
    if cond > 1e12:
        raise ValueError(
            f"Liouvillian matrix is near-singular (condition number = {cond:.2e}). "
            "Exact yield inversion requires a non-singular Liouvillian. "
            "Ensure k_S > 0 or k_T > 0 so that all population eventually decays to "
            "reaction products. For closed systems (k_S = k_T = 0) the infinite-time "
            "integral diverges and exact yield inversion is not applicable. "
            f"Current config: k_S={config.k_S}, k_T={config.k_T}, "
            f"gamma_dephasing={config.gamma_dephasing}, gamma_relaxation={config.gamma_relaxation}."
        )

    # Solve M @ vec_int = -vec_rho_0
    vec_int = np.linalg.solve(M, -vec_rho_0)
    rho_int = vec_int.reshape((8, 8), order='F')

    p_s = get_singlet_projector_3spin()
    p_t = get_triplet_projector_3spin()

    phi_s = float(np.real(config.k_S * np.trace(p_s @ rho_int)))
    phi_t = float(np.real(config.k_T * np.trace(p_t @ rho_int)))

    return phi_s, phi_t
