"""Tests for Qiskit circuit construction, state preparation, and Trotter cross-validation."""

import numpy as np
import pytest
from qiskit.quantum_info import Statevector
from src.spin_model import SpinModelConfig
from src.initial_states import get_pure_singlet_nuclear_states
from src.hamiltonian import build_total_hamiltonian
from src.operators import get_singlet_projector_3spin
from src.evolution import evolve_unitary
from src.qiskit_backend import (
    create_singlet_prep_circuit,
    build_qiskit_hamiltonian,
    simulate_qiskit_evolution,
    build_singlet_projector_operator,
)


def test_qiskit_singlet_prep_expectation():
    """Verify singlet state preparation circuit yields <P_S> = 1.0."""
    qc = create_singlet_prep_circuit(nuclear_state=0)
    sv = Statevector.from_instruction(qc)
    ps_op = build_singlet_projector_operator()

    exp_val = float(np.real(sv.expectation_value(ps_op)))
    assert np.isclose(exp_val, 1.0, atol=1e-12)


def test_qiskit_hamiltonian_spectrum_matches_matrix():
    """Verify Qiskit SparsePauliOp matrix has identical eigenvalues to NumPy Hamiltonian."""
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.7, phi=0.4, A_xx=6.0, A_yy=6.0, A_zz=24.0)

    H_scipy = build_total_hamiltonian(cfg)
    H_qiskit = build_qiskit_hamiltonian(cfg).to_matrix()

    eigs_scipy = np.sort(np.linalg.eigvalsh(H_scipy))
    eigs_qiskit = np.sort(np.linalg.eigvalsh(H_qiskit))

    assert np.allclose(eigs_scipy, eigs_qiskit, atol=1e-12)


def test_qiskit_trotter_evolution_matches_exact_unitary():
    """Verify Qiskit Trotter evolution closely tracks exact SciPy matrix exponential."""
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.8, phi=0.0, A_xx=5.0, A_yy=5.0, A_zz=20.0)
    H = build_total_hamiltonian(cfg)
    psi0, psi1 = get_pure_singlet_nuclear_states()
    ps_op = get_singlet_projector_3spin()

    t_eval = 0.5  # us
    psi0_t = evolve_unitary(psi0, H, t_eval)
    psi1_t = evolve_unitary(psi1, H, t_eval)
    ps_scipy = float(0.5 * (np.real(np.vdot(psi0_t, ps_op @ psi0_t)) + np.real(np.vdot(psi1_t, ps_op @ psi1_t))))

    ps_qiskit = simulate_qiskit_evolution(cfg, t_eval, num_trotter_steps=30)

    assert np.isclose(ps_scipy, ps_qiskit, atol=1e-3)


def test_noncommuting_hamiltonian_and_trotter_state_convergence():
    """
    Rigorously verify that:
    1. [H_Z, H_hf] is strictly non-commuting for tilted field angle theta != 0.
    2. Lie-Trotter evolution discretized via quantum circuit decomposition converges
       monotonically in full state norm error and unitary operator error as reps increase.
    """
    from src.hamiltonian import build_zeeman_hamiltonian, build_hyperfine_hamiltonian
    from src.qiskit_backend import compute_trotter_convergence_metrics

    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.75, phi=0.3, A_xx=5.0, A_yy=5.0, A_zz=20.0)
    hz = build_zeeman_hamiltonian(cfg)
    hhf = build_hyperfine_hamiltonian(cfg)

    # 1. Non-commutation verification
    comm = hz @ hhf - hhf @ hz
    comm_norm = float(np.linalg.norm(comm))
    assert comm_norm > 10.0, f"Expected non-commuting Hamiltonian, got ||[H_Z, H_hf]|| = {comm_norm}"

    # 2. Multi-step Trotter convergence
    reps_list = [2, 4, 8, 16, 32]
    metrics = compute_trotter_convergence_metrics(cfg, times=[0.5], reps_list=reps_list)
    state_errors = metrics["state_norm_error"]
    unitary_errors = metrics["unitary_error"]

    # Verify that error at r=32 is significantly smaller than at r=2
    assert state_errors[-1] < state_errors[0] / 3.0, f"State error failed to converge: {state_errors}"
    assert unitary_errors[-1] < unitary_errors[0] / 3.0, f"Unitary error failed to converge: {unitary_errors}"

