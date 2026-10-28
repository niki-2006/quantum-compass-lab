"""
Time evolution algorithms for radical-pair spin dynamics.

Supports:
1. Exact unitary evolution: U(t) = exp(-i*H*t) (closed system limit).
2. Time-dependent master equation solver for rho(t) under Haberkorn kinetics and decoherence.
3. Numerical integration of reaction yields:
   Phi_S(t_max) = k_S * integral_0^{t_max} Tr[P_S rho(t)] dt
   Integration uses the composite trapezoidal rule, giving O(dt^2) global convergence.
   Note: the RK45 ODE solver has O(dt^4) accuracy for rho(t), but the final yield quadrature
   is a separate step with its own (lower) O(dt^2) convergence from numpy.trapezoid.
4. Convergence analysis with respect to time step and integration horizon.
"""


from __future__ import annotations
import numpy as np
from scipy.linalg import expm
from scipy.integrate import solve_ivp
from src.operators import get_singlet_projector_3spin
from src.hamiltonian import build_total_hamiltonian
from src.reaction_kinetics import compute_haberkorn_rhs, build_total_liouvillian
from src.spin_model import SpinModelConfig


def evolve_unitary(psi_0: np.ndarray, H: np.ndarray, t: float) -> np.ndarray:
    """
    Evolve a pure state vector under unitary evolution: |psi(t)> = exp(-i*H*t) |psi_0>.
    """
    U = expm(-1.0j * H * t)
    return U @ psi_0


def evolve_density_matrix_unitary(rho_0: np.ndarray, H: np.ndarray, t: float) -> np.ndarray:
    """
    Evolve a density matrix under unitary evolution: rho(t) = exp(-i*H*t) rho_0 exp(i*H*t).
    """
    U = expm(-1.0j * H * t)
    return U @ rho_0 @ U.conj().T


def simulate_time_trajectory(
    rho_0: np.ndarray,
    config: SpinModelConfig,
    t_span: tuple[float, float] = (0.0, 5.0),
    num_points: int = 500,
    method: str = "expm"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate radical pair dynamics over time interval t_span.

    Args:
        rho_0: Initial 8x8 density matrix.
        config: SpinModelConfig with Hamiltonian, kinetics, and decoherence.
        t_span: (t_start, t_end) in microseconds.
        num_points: Number of evaluation points.
        method: 'expm' (exact matrix exponential of Liouvillian) or 'RK45' (scipy solve_ivp).

    Returns:
        times: 1D array of time points (microseconds).
        p_singlet: 1D array of instantaneous singlet probabilities Tr[P_S rho(t)].
        surviving_fraction: 1D array of Tr[rho(t)] (surviving radical pair fraction).
    """
    t_start, t_end = t_span
    times = np.linspace(t_start, t_end, num_points)
    p_s = get_singlet_projector_3spin()

    if method == "expm":
        # Vectorized Liouville evolution: vec(rho(t)) = expm(M * t) @ vec(rho_0)
        M = build_total_liouvillian(config)
        vec_0 = rho_0.flatten(order='F')

        p_singlet = np.zeros(num_points, dtype=float)
        surviving = np.zeros(num_points, dtype=float)

        dt = times[1] - times[0] if num_points > 1 else 0.0
        prop_dt = expm(M * dt) if num_points > 1 else np.eye(64, dtype=complex)

        curr_vec = vec_0.copy()
        for idx in range(num_points):
            rho_t = curr_vec.reshape((8, 8), order='F')
            p_singlet[idx] = float(np.real(np.trace(p_s @ rho_t)))
            surviving[idx] = float(np.real(np.trace(rho_t)))
            if idx < num_points - 1:
                curr_vec = prop_dt @ curr_vec

        return times, p_singlet, surviving

    elif method == "RK45":
        # ODE system for real and imaginary parts of rho elements
        H = build_total_hamiltonian(config)

        def rhs(t: float, y: np.ndarray) -> np.ndarray:
            rho_complex = (y[:64] + 1.0j * y[64:]).reshape((8, 8))
            d_rho = compute_haberkorn_rhs(rho_complex, config, H=H)
            d_flat = d_rho.flatten()
            return np.concatenate([np.real(d_flat), np.imag(d_flat)])

        y0 = np.concatenate([np.real(rho_0.flatten()), np.imag(rho_0.flatten())])
        sol = solve_ivp(rhs, t_span, y0, t_eval=times, method='RK45', rtol=1e-8, atol=1e-10)

        p_singlet = np.zeros(len(sol.t), dtype=float)
        surviving = np.zeros(len(sol.t), dtype=float)

        for idx in range(len(sol.t)):
            y_col = sol.y[:, idx]
            rho_t = (y_col[:64] + 1.0j * y_col[64:]).reshape((8, 8))
            p_singlet[idx] = float(np.real(np.trace(p_s @ rho_t)))
            surviving[idx] = float(np.real(np.trace(rho_t)))

        return sol.t, p_singlet, surviving

    else:
        raise ValueError(f"Unknown method '{method}'. Choose 'expm' or 'RK45'.")


def integrate_yield_numerically(
    times: np.ndarray,
    p_singlet: np.ndarray,
    k_S: float
) -> float:
    """
    Compute Phi_S(t_max) = k_S * integral_0^{t_max} p_singlet(t) dt.

    Method: Composite trapezoidal rule (numpy.trapezoid), giving O(dt^2) global convergence.
    Note: This is the accuracy of the quadrature step alone. The underlying ODE solver
    (RK45) has higher O(dt^4) accuracy, but the integration of the resulting scalar
    p_singlet(t) curve here is a separate step and is limited to O(dt^2).
    """
    integral = np.trapezoid(p_singlet, times)
    return float(k_S * integral)



def compute_exact_truncated_yield(
    rho_0: np.ndarray,
    config: SpinModelConfig,
    t_max: float
) -> float:
    """
    Compute exact truncated singlet yield on finite horizon [0, t_max] via Liouvillian integration:
        integral_0^{t_max} exp(M * t) dt = M^{-1} (exp(M * t_max) - I)
        Phi_S(t_max) = k_S * Tr[P_S unvec( M^{-1} (exp(M*t_max) - I) vec(rho_0) )]
    """
    M = build_total_liouvillian(config)
    vec_0 = rho_0.flatten(order='F')
    exp_M_tmax = expm(M * t_max)
    vec_int = np.linalg.solve(M, (exp_M_tmax - np.eye(64, dtype=complex)) @ vec_0)
    rho_int = vec_int.reshape((8, 8), order='F')
    p_s = get_singlet_projector_3spin()
    return float(np.real(config.k_S * np.trace(p_s @ rho_int)))


def compute_yield_tail(
    rho_0: np.ndarray,
    config: SpinModelConfig,
    t_max: float
) -> float:
    """
    Compute the remaining tail integral from t_max to infinity:
        Delta_tail = Phi_S(infinity) - Phi_S(t_max)
    """
    from src.reaction_kinetics import calculate_yields_exact
    phi_s_inf, _ = calculate_yields_exact(rho_0, config)
    phi_s_trunc = compute_exact_truncated_yield(rho_0, config, t_max)
    return float(phi_s_inf - phi_s_trunc)


def separate_truncation_and_quadrature_errors(
    rho_0: np.ndarray,
    config: SpinModelConfig,
    t_max: float,
    num_points: int
) -> dict[str, float]:
    """
    Decompose total yield error into two independent contributions:

        Total Error     = |Phi_S_num(t_max) - Phi_S_exact(inf)|
        Truncation Tail = |Phi_S_exact(inf) - Phi_S_exact(t_max)|  [exact finite-horizon difference]
        Quadrature Error = |Phi_S_num(t_max) - Phi_S_exact(t_max)| [O(dt^2) from trapezoidal rule]

    Both Phi_S_exact(inf) and Phi_S_exact(t_max) are computed exactly via Liouvillian inversion
    or matrix exponential integration. The 'Truncation Tail' is therefore an exact finite-horizon
    difference, NOT an analytical upper bound. Do not label it as an analytical bound.

    The total error is not necessarily equal to the sum of the individual errors (it is bounded
    by the triangle inequality: Total <= Truncation Tail + Quadrature Error).
    """

    from src.reaction_kinetics import calculate_yields_exact
    phi_s_inf, _ = calculate_yields_exact(rho_0, config)
    phi_s_trunc_exact = compute_exact_truncated_yield(rho_0, config, t_max)

    times, p_s, _ = simulate_time_trajectory(rho_0, config, t_span=(0.0, t_max), num_points=num_points)
    phi_s_num = integrate_yield_numerically(times, p_s, config.k_S)

    truncation_tail = abs(phi_s_inf - phi_s_trunc_exact)
    quadrature_error = abs(phi_s_num - phi_s_trunc_exact)
    total_error = abs(phi_s_num - phi_s_inf)

    return {
        "phi_s_inf": phi_s_inf,
        "phi_s_trunc_exact": phi_s_trunc_exact,
        "phi_s_numerical": phi_s_num,
        "truncation_tail": truncation_tail,
        "quadrature_error": quadrature_error,
        "total_error": total_error,
    }

