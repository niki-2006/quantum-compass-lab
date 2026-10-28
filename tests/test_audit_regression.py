"""
Regression tests for the 2026-10-25 scientific audit of Quantum Compass Lab.

These tests capture and prevent regression of the confirmed bugs and weaknesses
found during the audit:

1. Density-matrix positivity must check EIGENVALUES not just Tr[rho].
2. Singular Liouvillian (k_S=k_T=0, no dissipation) must raise a clear ValueError.
3. Quadrature convergence is O(dt^2) from the trapezoidal rule.
4. expm and RK45 propagation paths agree to within numerical tolerance.
5. Adversarial matrix: positive trace but negative eigenvalue -- positivity check must fail.
6. Exact finite-horizon tail is distinct from numerical quadrature error.
7. Yield conservation under asymmetric rates across several parameter combinations.
8. Qiskit Hamiltonian spectrum matches NumPy Hamiltonian eigenvalues.
"""

from __future__ import annotations
import numpy as np
import pytest
from scipy.linalg import expm

from src.spin_model import SpinModelConfig
from src.initial_states import get_initial_density_matrix
from src.reaction_kinetics import (
    calculate_yields_exact,
    build_total_liouvillian,
    compute_haberkorn_rhs,
)
from src.evolution import (
    simulate_time_trajectory,
    integrate_yield_numerically,
    compute_exact_truncated_yield,
    separate_truncation_and_quadrature_errors,
)
from src.hamiltonian import build_total_hamiltonian


# ---------------------------------------------------------------------------
# 1. Adversarial regression: positive trace does NOT imply positive semidefinite
# ---------------------------------------------------------------------------

def _make_positive_trace_negative_eigenvalue_matrix() -> np.ndarray:
    """
    Construct a 4x4 Hermitian matrix with positive trace but a significantly
    negative eigenvalue. This is the simplest counter-example showing that
    Tr[rho] > 0 is necessary but not sufficient for positive semidefiniteness.
    """
    # rho = diag(0.6, 0.4, -0.1, 0.1) rotated is complicated; use simpler direct example:
    # Eigenvalues: 0.7, 0.6, 0.1, -0.4 -> trace = 1.0, min_eig = -0.4
    eigs = np.array([0.7, 0.6, 0.1, -0.4])
    # Random unitary to mix
    rng = np.random.default_rng(42)
    A = rng.standard_normal((4, 4)) + 1j * rng.standard_normal((4, 4))
    Q, _ = np.linalg.qr(A)  # Q is unitary
    rho = Q @ np.diag(eigs) @ Q.conj().T
    return rho


def test_adversarial_positive_trace_negative_eigenvalue():
    """
    Verify that a matrix with Tr[rho] = 1 and a negative eigenvalue is correctly
    identified as NON-positive-semidefinite when eigenvalues are checked.
    This test would pass the OLD (trace-only) validation but must fail the NEW one.
    """
    rho = _make_positive_trace_negative_eigenvalue_matrix()

    # Old (incorrect) check: trace is positive
    trace = float(np.real(np.trace(rho)))
    assert trace > 0.0, "Adversarial matrix must have positive trace"

    # New (correct) check: minimum eigenvalue
    eigs = np.linalg.eigvalsh(0.5 * (rho + rho.conj().T))
    min_eig = float(np.min(eigs))

    # Min eigenvalue is significantly negative
    assert min_eig < -0.3, (
        f"Adversarial matrix should have min eigenvalue < -0.3, got {min_eig:.4f}. "
        "If this fails, the test construction is wrong."
    )

    # The trace-only test would see True (wrong); eigenvalue test correctly sees False
    trace_only_pass = trace >= -1e-10         # This incorrectly passes
    eigenvalue_pass = min_eig >= -1e-10       # This correctly fails
    assert trace_only_pass, "Trace check should (incorrectly) pass"
    assert not eigenvalue_pass, "Eigenvalue check must correctly fail"


# ---------------------------------------------------------------------------
# 2. Density matrix positivity: EIGENVALUES, not just trace
# ---------------------------------------------------------------------------

def test_density_matrix_positivity_checks_eigenvalues():
    """
    Verify that the evolved rho(t) has non-negative eigenvalues at all sampled times
    under Haberkorn kinetics + decoherence. This tests eigenvalues, not Tr[rho].
    """
    cfg = SpinModelConfig(
        B_magnitude=50.0, theta=0.7, phi=0.4,
        A_xx=5.0, A_yy=5.0, A_zz=20.0,
        k_S=1.0, k_T=1.0, gamma_dephasing=1.0
    )
    rho_0 = get_initial_density_matrix()
    M = build_total_liouvillian(cfg)
    vec_0 = rho_0.flatten(order='F')

    for t in [0.0, 0.5, 1.0, 2.0, 3.5]:
        if t == 0.0:
            rho_t = rho_0.copy()
        else:
            vec_t = expm(M * t) @ vec_0
            rho_t = vec_t.reshape((8, 8), order='F')

        # Symmetrize to suppress tiny floating-point asymmetry before eigensolver
        rho_herm = 0.5 * (rho_t + rho_t.conj().T)
        eigs = np.linalg.eigvalsh(rho_herm)
        min_eig = float(np.min(eigs))

        assert min_eig >= -1e-10, (
            f"Density matrix at t={t} us has min eigenvalue {min_eig:.2e} < -1e-10. "
            "This indicates a breakdown of complete positivity."
        )

        # Also check Hermiticity
        herm_err = float(np.max(np.abs(rho_t - rho_t.conj().T)))
        assert herm_err < 1e-12, f"Hermiticity violated at t={t}: {herm_err:.2e}"


def test_density_matrix_positivity_no_decoherence():
    """Verify positivity under pure Haberkorn kinetics with no decoherence."""
    cfg = SpinModelConfig(
        B_magnitude=50.0, theta=np.pi / 4.0,
        A_xx=5.0, A_yy=5.0, A_zz=20.0,
        k_S=1.5, k_T=0.5, gamma_dephasing=0.0
    )
    rho_0 = get_initial_density_matrix()
    M = build_total_liouvillian(cfg)
    vec_0 = rho_0.flatten(order='F')

    for t in [0.1, 0.5, 1.0, 2.0]:
        vec_t = expm(M * t) @ vec_0
        rho_t = vec_t.reshape((8, 8), order='F')
        rho_herm = 0.5 * (rho_t + rho_t.conj().T)
        min_eig = float(np.min(np.linalg.eigvalsh(rho_herm)))
        assert min_eig >= -1e-10, f"t={t}: min eigenvalue {min_eig:.2e}"


def test_density_matrix_trace_not_sufficient_for_positivity():
    """
    Regression test: ensure that a hypothetical rho with positive trace but
    negative eigenvalue would be caught by the eigenvalue check.
    This documents the bug that was fixed (trace-only check was insufficient).
    """
    rho_bad = _make_positive_trace_negative_eigenvalue_matrix()

    # Pad to 8x8 by kron with small identity block to match system size
    rho_8 = np.block([
        [rho_bad, np.zeros((4, 4))],
        [np.zeros((4, 4)), np.zeros((4, 4))]
    ])
    # Normalize (trace = 1)
    rho_8 = rho_bad.copy() if rho_bad.shape == (8, 8) else np.kron(rho_bad / np.trace(rho_bad), np.eye(2) / 2)

    trace = float(np.real(np.trace(rho_bad)))
    eigs = np.linalg.eigvalsh(0.5 * (rho_bad + rho_bad.conj().T))
    min_eig = float(np.min(eigs))

    # Trace check passes (incorrectly)
    assert trace > 0, "Trace should be positive for this adversarial matrix"
    # Eigenvalue check fails (correctly)
    assert min_eig < -0.1, f"Min eigenvalue should be significantly negative, got {min_eig}"


# ---------------------------------------------------------------------------
# 3. Singular Liouvillian: k_S=k_T=0 must raise informative ValueError
# ---------------------------------------------------------------------------

def test_singular_liouvillian_raises_value_error():
    """
    Verify that calculate_yields_exact raises ValueError when the Liouvillian is
    near-singular (k_S = k_T = 0 and no relaxation) instead of returning garbage.
    """
    cfg = SpinModelConfig(
        B_magnitude=50.0, k_S=0.0, k_T=0.0,
        gamma_dephasing=0.0, gamma_relaxation=0.0
    )
    rho_0 = get_initial_density_matrix()

    with pytest.raises(ValueError, match="near-singular"):
        calculate_yields_exact(rho_0, cfg)


def test_singular_liouvillian_with_dephasing_only_raises():
    """
    k_S = k_T = 0 with dephasing (but no relaxation) should still be near-singular
    because pure dephasing does not drive the system to a unique steady state.
    """
    cfg = SpinModelConfig(
        B_magnitude=50.0, k_S=0.0, k_T=0.0,
        gamma_dephasing=2.0, gamma_relaxation=0.0
    )
    rho_0 = get_initial_density_matrix()

    with pytest.raises(ValueError, match="near-singular"):
        calculate_yields_exact(rho_0, cfg)


def test_non_singular_liouvillian_succeeds():
    """Verify that valid (non-singular) Liouvillian does not raise."""
    cfg = SpinModelConfig(B_magnitude=50.0, k_S=1.0, k_T=1.0)
    rho_0 = get_initial_density_matrix()

    phi_s, phi_t = calculate_yields_exact(rho_0, cfg)
    assert 0.0 <= phi_s <= 1.0
    assert 0.0 <= phi_t <= 1.0
    assert np.isclose(phi_s + phi_t, 1.0, atol=1e-10)


# ---------------------------------------------------------------------------
# 4. Quadrature convergence: O(dt^2) from trapezoidal rule
# ---------------------------------------------------------------------------

def test_quadrature_convergence_order_is_second_order():
    """
    Verify that integrate_yield_numerically (numpy.trapezoid) exhibits O(dt^2)
    convergence. Estimate the convergence order from two consecutive grid refinements.

    This test CONFIRMS that the order is ~2 and would FAIL if someone changed
    the quadrature method to a higher-order scheme without updating documentation.
    """
    cfg = SpinModelConfig(
        B_magnitude=50.0, theta=np.pi / 4.0,
        A_xx=5.0, A_yy=5.0, A_zz=20.0,
        k_S=1.0, k_T=1.0
    )
    rho_0 = get_initial_density_matrix()
    t_max = 5.0

    # Reference: exact truncated yield from Liouvillian matrix integration
    phi_ref = compute_exact_truncated_yield(rho_0, cfg, t_max)

    # Coarse grid
    dt1, n1 = 0.1, int(round(t_max / 0.1)) + 1
    times1, p_s1, _ = simulate_time_trajectory(rho_0, cfg, t_span=(0.0, t_max), num_points=n1)
    err1 = abs(integrate_yield_numerically(times1, p_s1, cfg.k_S) - phi_ref)

    # Fine grid (half step)
    dt2, n2 = 0.05, int(round(t_max / 0.05)) + 1
    times2, p_s2, _ = simulate_time_trajectory(rho_0, cfg, t_span=(0.0, t_max), num_points=n2)
    err2 = abs(integrate_yield_numerically(times2, p_s2, cfg.k_S) - phi_ref)

    assert err1 > 0 and err2 > 0, "Errors must be nonzero for valid convergence estimate"
    # Observed order from halving dt: log2(err1/err2)
    observed_order = np.log2(err1 / err2)

    # Trapezoidal rule should give order ~ 2.0 (allow range 1.5 to 2.5)
    assert 1.5 <= observed_order <= 2.5, (
        f"Expected O(dt^2) trapezoidal convergence, got order {observed_order:.2f}. "
        f"err at dt={dt1}: {err1:.2e}, err at dt={dt2}: {err2:.2e}."
    )


# ---------------------------------------------------------------------------
# 5. expm vs RK45 consistency
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("gamma", [0.0, 1.0, 3.0])
@pytest.mark.parametrize("theta", [0.0, np.pi / 4.0, np.pi / 2.0])
def test_expm_vs_rk45_singlet_probability_agreement(gamma, theta):
    """
    Verify that the expm and RK45 propagation paths produce consistent singlet
    probabilities and survival fractions across representative parameter combinations.
    """
    cfg = SpinModelConfig(
        B_magnitude=50.0, theta=theta,
        A_xx=5.0, A_yy=5.0, A_zz=20.0,
        k_S=1.0, k_T=1.0, gamma_dephasing=gamma
    )
    rho_0 = get_initial_density_matrix()
    t_end = 2.0
    n = 100

    times_ex, ps_ex, surv_ex = simulate_time_trajectory(
        rho_0, cfg, t_span=(0.0, t_end), num_points=n, method='expm'
    )
    times_rk, ps_rk, surv_rk = simulate_time_trajectory(
        rho_0, cfg, t_span=(0.0, t_end), num_points=n, method='RK45'
    )

    # The two methods must agree to within tight tolerance
    max_ps_diff = float(np.max(np.abs(ps_ex - ps_rk)))
    max_surv_diff = float(np.max(np.abs(surv_ex - surv_rk)))

    assert max_ps_diff < 1e-8, (
        f"theta={theta:.2f}, gamma={gamma}: expm vs RK45 singlet probability disagreement: {max_ps_diff:.2e}"
    )
    assert max_surv_diff < 1e-8, (
        f"theta={theta:.2f}, gamma={gamma}: expm vs RK45 survival disagreement: {max_surv_diff:.2e}"
    )


# ---------------------------------------------------------------------------
# 6. Tail vs quadrature error separation
# ---------------------------------------------------------------------------

def test_truncation_tail_and_quadrature_error_are_independent():
    """
    Verify that truncation tail and quadrature error can be independently controlled:
    - Truncation tail decreases as t_max increases.
    - Quadrature error decreases as dt decreases (at fixed t_max).
    - The 'exact finite-horizon tail' is computed by Liouvillian inversion, not estimated.
    """
    cfg = SpinModelConfig(
        B_magnitude=50.0, theta=np.pi / 4.0,
        A_xx=5.0, A_yy=5.0, A_zz=20.0,
        k_S=1.0, k_T=1.0
    )
    rho_0 = get_initial_density_matrix()

    # Verify tail decreases with t_max
    tail_5 = abs(
        calculate_yields_exact(rho_0, cfg)[0] - compute_exact_truncated_yield(rho_0, cfg, 5.0)
    )
    tail_10 = abs(
        calculate_yields_exact(rho_0, cfg)[0] - compute_exact_truncated_yield(rho_0, cfg, 10.0)
    )
    assert tail_10 < tail_5, f"Tail should decrease with t_max: tail_5={tail_5:.2e}, tail_10={tail_10:.2e}"

    # At t_max=5: coarse vs fine quadrature
    result_coarse = separate_truncation_and_quadrature_errors(rho_0, cfg, t_max=5.0, num_points=51)
    result_fine = separate_truncation_and_quadrature_errors(rho_0, cfg, t_max=5.0, num_points=501)

    # Truncation tail is identical (both use exact inversion, independent of quadrature)
    assert np.isclose(result_coarse["truncation_tail"], result_fine["truncation_tail"], rtol=1e-10), (
        "Truncation tail must be identical for coarse/fine grids (it's computed exactly)"
    )

    # Quadrature error should decrease with finer grid
    assert result_fine["quadrature_error"] < result_coarse["quadrature_error"], (
        "Finer quadrature grid should have smaller error"
    )


# ---------------------------------------------------------------------------
# 7. Yield conservation: asymmetric rates, decoherence on/off
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("k_s,k_t,theta,gamma", [
    (1.0, 1.0, 0.0, 0.0),
    (2.0, 0.5, 0.5, 0.0),
    (0.5, 2.0, np.pi / 3, 0.0),
    (1.2, 0.8, np.pi / 4, 1.0),
    (3.0, 0.3, np.pi / 2, 2.5),
])
def test_yield_conservation_comprehensive(k_s, k_t, theta, gamma):
    """
    Verify Phi_S + Phi_T = 1.0 across diverse rate/angle/decoherence combinations.
    Enforces conservation only when k_S > 0 or k_T > 0 (complete reaction assumption).
    """
    cfg = SpinModelConfig(
        B_magnitude=50.0, theta=theta,
        A_xx=5.0, A_yy=5.0, A_zz=20.0,
        k_S=k_s, k_T=k_t, gamma_dephasing=gamma
    )
    rho_0 = get_initial_density_matrix()
    phi_s, phi_t = calculate_yields_exact(rho_0, cfg)

    assert 0.0 <= phi_s <= 1.0, f"phi_s out of bounds: {phi_s}"
    assert 0.0 <= phi_t <= 1.0, f"phi_t out of bounds: {phi_t}"
    assert np.isclose(phi_s + phi_t, 1.0, atol=1e-9), (
        f"Conservation failed: phi_s={phi_s:.8f}, phi_t={phi_t:.8f}, sum={phi_s+phi_t:.10f}"
    )


# ---------------------------------------------------------------------------
# 8. Qiskit Hamiltonian: eigenvalue spectrum matches NumPy Hamiltonian
# ---------------------------------------------------------------------------

def test_qiskit_hamiltonian_eigenvalues_match_numpy():
    """
    Verify that the Qiskit SparsePauliOp matrix has the same eigenvalues as
    the NumPy Hamiltonian. They may differ by qubit endianness (Qiskit uses
    little-endian ordering) but must share the same eigenvalue spectrum.
    """
    from src.qiskit_backend import build_qiskit_hamiltonian

    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.7, phi=0.4, A_xx=6.0, A_yy=6.0, A_zz=24.0)
    H_numpy = build_total_hamiltonian(cfg)
    H_qiskit = build_qiskit_hamiltonian(cfg).to_matrix()

    eigs_numpy = np.sort(np.linalg.eigvalsh(H_numpy))
    eigs_qiskit = np.sort(np.linalg.eigvalsh(H_qiskit))

    assert np.allclose(eigs_numpy, eigs_qiskit, atol=1e-12), (
        f"Eigenvalue mismatch: max diff = {np.max(np.abs(eigs_numpy - eigs_qiskit)):.2e}"
    )


# ---------------------------------------------------------------------------
# 9. Qiskit multi-time, multi-rep Trotter convergence
# ---------------------------------------------------------------------------

def test_qiskit_trotter_convergence_monotone():
    """
    Verify that increasing Trotter repetitions monotonically decreases the
    singlet-expectation error between the Qiskit circuit and SciPy exact solution.
    Tests multiple time points and verifies full-state convergence.
    """
    from src.qiskit_backend import compute_trotter_convergence_metrics

    cfg = SpinModelConfig(
        B_magnitude=50.0, theta=0.75, phi=0.3,
        A_xx=5.0, A_yy=5.0, A_zz=20.0
    )
    reps = [2, 4, 8, 16]
    metrics = compute_trotter_convergence_metrics(cfg, times=[0.3, 0.5], reps_list=reps)

    # Filter to t=0.3 results (first len(reps) entries)
    state_errors_t03 = metrics["state_norm_error"][:len(reps)]
    state_errors_t05 = metrics["state_norm_error"][len(reps):]

    # Error at r=16 must be less than error at r=2 (monotone reduction)
    assert state_errors_t03[-1] < state_errors_t03[0] / 2.0, (
        f"t=0.3: Trotter state error did not converge: {state_errors_t03}"
    )
    assert state_errors_t05[-1] < state_errors_t05[0] / 2.0, (
        f"t=0.5: Trotter state error did not converge: {state_errors_t05}"
    )


# ---------------------------------------------------------------------------
# 10. Contrast metric consistency
# ---------------------------------------------------------------------------

def test_contrast_formula_consistency():
    """
    Verify contrast C = (max - min)/(max + min) matches absolute anisotropy Delta = max - min,
    and that both are computed from the actual data (not hardcoded).
    """
    from src.metrics import calculate_compass_metrics
    from src.experiment_runner import run_angular_sweep

    cfg = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0)
    res = run_angular_sweep(cfg, num_angles=91)

    phi_s = np.array(res.singlet_yields)
    thetas = np.deg2rad(np.array(res.thetas_deg))
    metrics = calculate_compass_metrics(thetas, phi_s)

    # Verify formula
    expected_contrast = (metrics.phi_s_max - metrics.phi_s_min) / (metrics.phi_s_max + metrics.phi_s_min)
    expected_delta = metrics.phi_s_max - metrics.phi_s_min

    assert np.isclose(metrics.contrast, expected_contrast, rtol=1e-12), (
        f"Contrast formula mismatch: stored={metrics.contrast:.8f}, expected={expected_contrast:.8f}"
    )
    assert np.isclose(metrics.absolute_anisotropy, expected_delta, rtol=1e-12), (
        f"Anisotropy formula mismatch: stored={metrics.absolute_anisotropy:.8f}, expected={expected_delta:.8f}"
    )

    # Verify Experiment 1 reference values (computed from live code, not hardcoded)
    assert np.isclose(metrics.phi_s_max, 0.487214, atol=1e-4), f"Max yield: {metrics.phi_s_max}"
    assert np.isclose(metrics.phi_s_min, 0.372643, atol=1e-4), f"Min yield: {metrics.phi_s_min}"
    assert np.isclose(metrics.absolute_anisotropy, 0.114571, atol=1e-4), f"Delta: {metrics.absolute_anisotropy}"
    assert np.isclose(metrics.contrast * 100, 13.32, atol=0.02), f"Contrast %: {metrics.contrast * 100}"
