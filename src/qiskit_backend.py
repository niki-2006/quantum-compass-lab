"""
Qiskit quantum circuit implementation for radical-pair magnetoreception.

Features:
1. 3-qubit mapping:
   Qubit 0: Electron 1 (S1)
   Qubit 1: Electron 2 (S2)
   Qubit 2: Nuclear spin (I)
2. Exact Singlet State Preparation |S> = (|01> - |10>)/sqrt(2).
3. Unpolarized nuclear spin ensemble via complementary state simulations (|0> and |1>).
4. Hamiltonian translation into Qiskit SparsePauliOp.
5. First-order Lie-Trotter synthesis circuit with tunable Trotter steps.
6. Measurement of singlet probability via Bell-basis rotation or SparsePauliOp expectation.
7. Support for Statevector and AerSimulator execution.
"""

from __future__ import annotations
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.synthesis import LieTrotter
from src.spin_model import SpinModelConfig


def create_singlet_prep_circuit(nuclear_state: int = 0) -> QuantumCircuit:
    """
    Construct circuit preparing |S> (x) |nuclear_state>.

    Electron singlet state preparation on qubits 0 and 1:
    |00> -> X(1) -> |01> -> H(0) -> Z(0) -> CX(0, 1) -> (|01> - |10>) / sqrt(2).

    Args:
        nuclear_state: 0 for |0> (up), 1 for |1> (down).
    """
    qc = QuantumCircuit(3, name=f"Prep_Singlet_N{nuclear_state}")

    # Prepare electron singlet on qubits 0, 1
    qc.x(1)
    qc.h(0)
    qc.z(0)
    qc.cx(0, 1)

    # Prepare nuclear spin on qubit 2
    if nuclear_state == 1:
        qc.x(2)

    return qc


def create_bell_measurement_circuit() -> QuantumCircuit:
    """
    Invert singlet preparation on qubits 0 and 1.
    If the two-electron state is |S>, the output on qubits 0 and 1 will be |00>.
    """
    qc = QuantumCircuit(3, name="Bell_Meas_Inverse")
    qc.cx(0, 1)
    qc.z(0)
    qc.h(0)
    qc.x(1)
    return qc


def build_qiskit_hamiltonian(config: SpinModelConfig) -> SparsePauliOp:
    """
    Translate SpinModelConfig Hamiltonian into Qiskit SparsePauliOp.

    Indices:
        Qubit 0: Electron 1
        Qubit 1: Electron 2
        Qubit 2: Nuclear spin
    """
    terms: list[tuple[str, list[int], float]] = []

    # Electron Zeeman: omega_0 * b . (S1 + S2) = (omega_0 / 2) * b . (sigma_1 + sigma_2)
    omega_0 = config.zeeman_omega
    bx, by, bz = config.field_unit_vector

    # Electron 1 Zeeman
    if abs(bx) > 1e-12:
        terms.append(("X", [0], 0.5 * omega_0 * bx))
    if abs(by) > 1e-12:
        terms.append(("Y", [0], 0.5 * omega_0 * by))
    if abs(bz) > 1e-12:
        terms.append(("Z", [0], 0.5 * omega_0 * bz))

    # Electron 2 Zeeman
    if abs(bx) > 1e-12:
        terms.append(("X", [1], 0.5 * omega_0 * bx))
    if abs(by) > 1e-12:
        terms.append(("Y", [1], 0.5 * omega_0 * by))
    if abs(bz) > 1e-12:
        terms.append(("Z", [1], 0.5 * omega_0 * bz))

    # Hyperfine: A_xx * S1x * Ix + A_yy * S1y * Iy + A_zz * S1z * Iz
    # = 0.25 * (A_xx * sigma_1x * sigma_Ix + A_yy * sigma_1y * sigma_Iy + A_zz * sigma_1z * sigma_Iz)
    if abs(config.A_xx) > 1e-12:
        terms.append(("XX", [0, 2], 0.25 * config.A_xx))
    if abs(config.A_yy) > 1e-12:
        terms.append(("YY", [0, 2], 0.25 * config.A_yy))
    if abs(config.A_zz) > 1e-12:
        terms.append(("ZZ", [0, 2], 0.25 * config.A_zz))

    pauli_op = SparsePauliOp.from_sparse_list(terms, num_qubits=3)
    return pauli_op


def create_trotter_evolution_circuit(
    config: SpinModelConfig,
    time: float,
    num_steps: int = 10
) -> QuantumCircuit:
    """
    Construct a Trotterized time-evolution circuit exp(-i * H * time) using Qiskit PauliEvolutionGate.
    """
    h_op = build_qiskit_hamiltonian(config)
    evo_gate = PauliEvolutionGate(h_op, time=time, synthesis=LieTrotter(reps=num_steps))

    qc = QuantumCircuit(3, name=f"Trotter_t{time:.2f}")
    qc.append(evo_gate, [0, 1, 2])
    return qc


def build_singlet_projector_operator() -> SparsePauliOp:
    """
    P_S = 1/4 (I - X0 X1 - Y0 Y1 - Z0 Z1) (x) I_2
    """
    terms = [
        ("I", [0], 0.25),
        ("XX", [0, 1], -0.25),
        ("YY", [0, 1], -0.25),
        ("ZZ", [0, 1], -0.25),
    ]
    return SparsePauliOp.from_sparse_list(terms, num_qubits=3)


def simulate_qiskit_evolution(
    config: SpinModelConfig,
    time: float,
    num_trotter_steps: int = 10
) -> float:
    """
    Simulate radical pair singlet probability at time t using Qiskit Statevector
    averaged over the unpolarized nuclear ensemble (|0> and |1>).

    Returns:
        p_S(t): instantaneous singlet probability.
    """
    p_s_op = build_singlet_projector_operator()
    probs: list[float] = []

    for nuclear_spin in (0, 1):
        qc = QuantumCircuit(3)
        prep = create_singlet_prep_circuit(nuclear_state=nuclear_spin)
        qc.compose(prep, inplace=True)

        if time > 1e-9:
            evo = create_trotter_evolution_circuit(config, time, num_steps=num_trotter_steps)
            # Decomposing the PauliEvolutionGate synthesizes the actual Lie-Trotter product formula
            # into discrete elementary rotational gates (RZ, RX, RZZ), rather than evaluating an exact unitary.
            qc.compose(evo.decompose(), inplace=True)

        # Evaluate statevector
        sv = Statevector.from_instruction(qc)
        exp_val = float(np.real(sv.expectation_value(p_s_op)))
        probs.append(exp_val)

    return float(np.mean(probs))


def compute_trotter_convergence_metrics(
    config: SpinModelConfig,
    times: list[float] = [0.2, 0.5, 1.0],
    reps_list: list[int] = [1, 2, 4, 8, 16, 32]
) -> dict[str, list]:
    """
    Compute rigorous Lie-Trotter convergence metrics comparing decomposed circuit evolution
    against the exact matrix exponential across multiple times and repetition steps.

    Measures:
    1. Full State Norm Error: || |psi_Trotter> - |psi_exact> ||_2
    2. State Infidelity: 1 - |<psi_exact | psi_Trotter>|^2
    3. Singlet Expectation Error: |<P_S>_Trotter - <P_S>_exact|
    4. Unitary Operator Frobenius Error: || U_Trotter - U_exact ||_F
    """
    from scipy.linalg import expm
    from qiskit.quantum_info import Operator
    from src.hamiltonian import build_total_hamiltonian

    H_qiskit = build_qiskit_hamiltonian(config).to_matrix()
    p_s_op = build_singlet_projector_operator()

    records = {
        "time_us": [],
        "reps": [],
        "state_norm_error": [],
        "infidelity": [],
        "observable_error": [],
        "unitary_error": [],
    }

    # Reference state: electron singlet with nuclear spin |0>
    psi0_data = Statevector.from_instruction(create_singlet_prep_circuit(0)).data

    for t in times:
        U_exact_qiskit = expm(-1.0j * H_qiskit * t)
        psi_exact_data = U_exact_qiskit @ psi0_data
        ps_exact = float(np.real(np.vdot(psi_exact_data, p_s_op.to_matrix() @ psi_exact_data)))

        for r in reps_list:
            qc = QuantumCircuit(3)
            qc.compose(create_singlet_prep_circuit(0), inplace=True)
            evo = create_trotter_evolution_circuit(config, time=t, num_steps=r)
            qc_decomposed = evo.decompose()
            qc.compose(qc_decomposed, inplace=True)

            # Simulated Trotter state
            sv_trotter = Statevector.from_instruction(qc).data
            state_err = float(np.linalg.norm(sv_trotter - psi_exact_data))
            fidelity = float(abs(np.vdot(psi_exact_data, sv_trotter))**2)
            infidelity = float(max(0.0, 1.0 - fidelity))

            # Observable error
            ps_trotter = float(np.real(np.vdot(sv_trotter, p_s_op.to_matrix() @ sv_trotter)))
            obs_err = abs(ps_trotter - ps_exact)

            # Unitary error
            U_trotter = Operator(qc_decomposed).data
            # In Qiskit, qubit ordering is reversed compared to standard tensor product
            # Compare Operator with Qiskit's exact matrix
            U_exact_qiskit = expm(-1.0j * build_qiskit_hamiltonian(config).to_matrix() * t)
            u_err = float(np.linalg.norm(U_trotter - U_exact_qiskit, ord='fro'))

            records["time_us"].append(t)
            records["reps"].append(r)
            records["state_norm_error"].append(state_err)
            records["infidelity"].append(infidelity)
            records["observable_error"].append(obs_err)
            records["unitary_error"].append(u_err)

    return records

