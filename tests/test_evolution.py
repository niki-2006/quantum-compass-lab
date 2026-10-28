"""Tests for unitary and master equation time evolution."""

import numpy as np
import pytest
from src.spin_model import SpinModelConfig
from src.initial_states import get_pure_singlet_nuclear_states, get_initial_density_matrix
from src.hamiltonian import build_total_hamiltonian
from src.evolution import (
    evolve_unitary,
    evolve_density_matrix_unitary,
    simulate_time_trajectory,
)


def test_unitary_norm_conservation():
    """Verify state vector remains normalized for arbitrary t."""
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.4, phi=0.1)
    H = build_total_hamiltonian(cfg)
    psi0, _ = get_pure_singlet_nuclear_states()

    for t in [0.1, 1.0, 5.0]:
        psi_t = evolve_unitary(psi0, H, t)
        norm = np.real(np.vdot(psi_t, psi_t))
        assert np.isclose(norm, 1.0, atol=1e-12)


def test_unitary_density_matrix_trace_and_hermiticity():
    """Verify rho(t) under unitary evolution preserves trace and remains Hermitian."""
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.4, phi=0.1)
    H = build_total_hamiltonian(cfg)
    rho_0 = get_initial_density_matrix()

    for t in [0.5, 2.0]:
        rho_t = evolve_density_matrix_unitary(rho_0, H, t)
        assert np.isclose(np.trace(rho_t), 1.0, atol=1e-12)
        assert np.allclose(rho_t, rho_t.conj().T, atol=1e-12)


def test_time_trajectory_decay():
    """Verify that with non-zero reaction rates, surviving fraction Tr[rho(t)] decays monotonically."""
    cfg = SpinModelConfig(B_magnitude=50.0, k_S=1.0, k_T=1.0)
    rho_0 = get_initial_density_matrix()

    times, p_s, surviving = simulate_time_trajectory(rho_0, cfg, t_span=(0.0, 4.0), num_points=50)

    assert np.isclose(surviving[0], 1.0)
    assert surviving[-1] < 0.05  # after 4 lifetimes, e^(-4) ~ 0.018
    # Monotonically non-increasing
    diffs = np.diff(surviving)
    assert all(d <= 1e-6 for d in diffs)


def test_trace_preserving_lindblad_physicality():
    """
    Verify trace preservation (Tr[rho(t)] = 1.0), Hermiticity, and eigenvalue positivity
    under pure Lindblad open-system evolution without reaction sinks (k_S = k_T = 0).
    """
    from scipy.linalg import expm
    from src.reaction_kinetics import build_total_liouvillian

    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.6, phi=0.3, k_S=0.0, k_T=0.0, gamma_dephasing=2.5)
    rho_0 = get_initial_density_matrix()
    vec_0 = rho_0.flatten(order='F')
    M = build_total_liouvillian(cfg)

    for t in [0.5, 1.0, 2.0, 4.0]:
        vec_t = expm(M * t) @ vec_0
        rho_t = vec_t.reshape((8, 8), order='F')

        # Trace preservation
        trace_val = float(np.real(np.trace(rho_t)))
        assert np.isclose(trace_val, 1.0, atol=1e-12), f"Trace violation at t={t}: {trace_val}"

        # Hermiticity
        herm_err = float(np.max(np.abs(rho_t - rho_t.conj().T)))
        assert herm_err < 1e-12, f"Hermiticity violation at t={t}: {herm_err}"

        # Positivity
        min_eig = float(np.min(np.linalg.eigvalsh(rho_t)))
        assert min_eig >= -1e-12, f"Eigenvalue positivity violation at t={t}: {min_eig}"


def test_haberkorn_analytical_trace_decay():
    """
    Verify exact analytical trace decay Tr[rho(t)] = exp(-k*t) for equal recombination rates k_S = k_T = k,
    along with Hermiticity and positivity.
    """
    from scipy.linalg import expm
    from src.reaction_kinetics import build_total_liouvillian

    k_rate = 1.4
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.7, k_S=k_rate, k_T=k_rate, gamma_dephasing=1.0)
    rho_0 = get_initial_density_matrix()
    vec_0 = rho_0.flatten(order='F')
    M = build_total_liouvillian(cfg)

    for t in [0.2, 0.8, 1.5, 3.0]:
        vec_t = expm(M * t) @ vec_0
        rho_t = vec_t.reshape((8, 8), order='F')

        expected_trace = np.exp(-k_rate * t)
        actual_trace = float(np.real(np.trace(rho_t)))
        assert np.isclose(actual_trace, expected_trace, atol=1e-11), f"Trace decay mismatch: {actual_trace} vs {expected_trace}"

        herm_err = float(np.max(np.abs(rho_t - rho_t.conj().T)))
        assert herm_err < 1e-12

        min_eig = float(np.min(np.linalg.eigvalsh(rho_t)))
        assert min_eig >= -1e-12

