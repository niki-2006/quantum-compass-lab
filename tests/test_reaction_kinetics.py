"""Tests for Haberkorn reaction kinetics, yield integration, and conservation."""

import numpy as np
import pytest
from src.spin_model import SpinModelConfig
from src.initial_states import get_initial_density_matrix
from src.reaction_kinetics import calculate_yields_exact, build_total_liouvillian


def test_yield_conservation_equal_rates():
    """Verify Phi_S + Phi_T = 1.0 for k_S = k_T."""
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.8, k_S=1.0, k_T=1.0)
    rho_0 = get_initial_density_matrix()

    phi_s, phi_t = calculate_yields_exact(rho_0, cfg)

    assert 0.0 <= phi_s <= 1.0
    assert 0.0 <= phi_t <= 1.0
    assert np.isclose(phi_s + phi_t, 1.0, atol=1e-10)


def test_yield_conservation_differential_rates():
    """Verify Phi_S + Phi_T = 1.0 for k_S != k_T."""
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.5, k_S=2.5, k_T=0.5)
    rho_0 = get_initial_density_matrix()

    phi_s, phi_t = calculate_yields_exact(rho_0, cfg)

    assert 0.0 <= phi_s <= 1.0
    assert 0.0 <= phi_t <= 1.0
    assert np.isclose(phi_s + phi_t, 1.0, atol=1e-10)


def test_liouvillian_superoperator_dimension():
    """Verify Liouvillian superoperator M is 64x64."""
    cfg = SpinModelConfig(B_magnitude=50.0)
    M = build_total_liouvillian(cfg)

    assert M.shape == (64, 64)
    # Recombination sinks ensure negative real parts for eigenvalues
    eigs = np.linalg.eigvals(M)
    assert all(np.real(e) < 0.0 for e in eigs)


@pytest.mark.parametrize("k_s, k_t", [(1.0, 1.0), (2.5, 0.5), (0.6, 1.8)])
@pytest.mark.parametrize("theta", [0.0, np.pi / 4.0, np.pi / 2.0])
@pytest.mark.parametrize("gamma", [0.0, 1.0, 5.0])
def test_exact_yield_vs_numerical_integration_parameter_grid(k_s, k_t, theta, gamma):
    """
    Rigorously validate exact Liouvillian inversion against direct numerical
    integration of the same Haberkorn master equation on finite horizon [0, t_max].
    """
    from src.evolution import simulate_time_trajectory, integrate_yield_numerically, compute_exact_truncated_yield

    cfg = SpinModelConfig(
        B_magnitude=50.0,
        theta=theta,
        A_xx=5.0,
        A_yy=5.0,
        A_zz=20.0,
        k_S=k_s,
        k_T=k_t,
        gamma_dephasing=gamma
    )
    rho_0 = get_initial_density_matrix()

    # 1. Exact infinite horizon yield conservation
    phi_s_inf, phi_t_inf = calculate_yields_exact(rho_0, cfg)
    assert np.isclose(phi_s_inf + phi_t_inf, 1.0, atol=1e-10), f"Conservation failed: {phi_s_inf + phi_t_inf}"
    assert 0.0 <= phi_s_inf <= 1.0
    assert 0.0 <= phi_t_inf <= 1.0

    # 2. Compare exact truncated yield with numerical integration on [0, t_max]
    t_max = 6.0
    phi_s_trunc_exact = compute_exact_truncated_yield(rho_0, cfg, t_max)

    # Numerical integration with dt = 0.005 us (1201 points)
    times, p_s, _ = simulate_time_trajectory(rho_0, cfg, t_span=(0.0, t_max), num_points=1201)
    phi_s_num = integrate_yield_numerically(times, p_s, cfg.k_S)

    quadrature_discrepancy = abs(phi_s_num - phi_s_trunc_exact)
    # Numerical quadrature with dt = 0.005 us must match exact truncated yield within 1e-4
    assert quadrature_discrepancy < 1e-4, f"Quadrature discrepancy too large: {quadrature_discrepancy:.2e}"

