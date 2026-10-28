"""
Spin operators, Pauli matrices, tensor products, and projectors for radical-pair modeling.

Hilbert Space Convention:
- Total dimension: 2^3 = 8 for a 3-spin system (Electron 1, Electron 2, Nuclear spin).
- Ordering convention:
    Qubit 0: Electron Spin 1 (S1)
    Qubit 1: Electron Spin 2 (S2)
    Qubit 2: Nuclear Spin (I)
- In Kronecker product notation: |S1, S2, I> = |S1> (x) |S2> (x) |I>
"""

from __future__ import annotations
import numpy as np

# Pauli matrices
SIGMA_X: np.ndarray = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y: np.ndarray = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z: np.ndarray = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
IDENTITY_2: np.ndarray = np.eye(2, dtype=complex)
IDENTITY_4: np.ndarray = np.eye(4, dtype=complex)
IDENTITY_8: np.ndarray = np.eye(8, dtype=complex)

# Spin-1/2 operators (hbar = 1 convention)
S_X: np.ndarray = 0.5 * SIGMA_X
S_Y: np.ndarray = 0.5 * SIGMA_Y
S_Z: np.ndarray = 0.5 * SIGMA_Z


def embed_operator_3spin(op: np.ndarray, target_subsystem: int) -> np.ndarray:
    """
    Embed a 2x2 single-spin operator into the 3-spin (8-dimensional) Hilbert space.

    Args:
        op: 2x2 complex numpy array.
        target_subsystem: 0 for Electron 1 (S1), 1 for Electron 2 (S2), 2 for Nuclear spin (I).

    Returns:
        8x8 complex numpy array.
    """
    if op.shape != (2, 2):
        raise ValueError(f"Expected 2x2 operator, got shape {op.shape}")

    ops = [IDENTITY_2, IDENTITY_2, IDENTITY_2]
    if target_subsystem not in (0, 1, 2):
        raise ValueError(f"Target subsystem must be 0, 1, or 2, got {target_subsystem}")
    ops[target_subsystem] = op

    res = np.kron(ops[0], np.kron(ops[1], ops[2]))
    return res


def get_spin_operators_3spin() -> dict[str, np.ndarray]:
    """
    Return dictionary of all single-spin operators embedded in the 8D Hilbert space.
    Keys:
        'S1x', 'S1y', 'S1z'
        'S2x', 'S2y', 'S2z'
        'Ix',  'Iy',  'Iz'
    """
    return {
        "S1x": embed_operator_3spin(S_X, 0),
        "S1y": embed_operator_3spin(S_Y, 0),
        "S1z": embed_operator_3spin(S_Z, 0),
        "S2x": embed_operator_3spin(S_X, 1),
        "S2y": embed_operator_3spin(S_Y, 1),
        "S2z": embed_operator_3spin(S_Z, 1),
        "Ix": embed_operator_3spin(S_X, 2),
        "Iy": embed_operator_3spin(S_Y, 2),
        "Iz": embed_operator_3spin(S_Z, 2),
    }


def get_singlet_state_2spin() -> np.ndarray:
    """
    Return the two-electron singlet state |S> = (|01> - |10>)/sqrt(2).
    Dimension: 4x1 vector.
    """
    s = np.zeros(4, dtype=complex)
    # Basis: |00>=0, |01>=1, |10>=2, |11>=3
    s[1] = 1.0 / np.sqrt(2.0)
    s[2] = -1.0 / np.sqrt(2.0)
    return s


def get_singlet_projector_2spin() -> np.ndarray:
    """
    Return the 4x4 singlet projector P_S = |S><S| for the two-electron subspace.
    """
    s = get_singlet_state_2spin()
    return np.outer(s, np.conjugate(s))


def get_triplet_projector_2spin() -> np.ndarray:
    """
    Return the 4x4 triplet projector P_T = I_4 - P_S for the two-electron subspace.
    """
    return IDENTITY_4 - get_singlet_projector_2spin()


def get_singlet_projector_3spin() -> np.ndarray:
    """
    Return the 8x8 singlet projector for the 3-spin system:
    P_S^(3) = P_S (x) I_nuclear
    """
    p_s_2 = get_singlet_projector_2spin()
    return np.kron(p_s_2, IDENTITY_2)


def get_triplet_projector_3spin() -> np.ndarray:
    """
    Return the 8x8 triplet projector for the 3-spin system:
    P_T^(3) = P_T (x) I_nuclear = I_8 - P_S^(3)
    """
    return IDENTITY_8 - get_singlet_projector_3spin()


def is_hermitian(matrix: np.ndarray, tol: float = 1e-10) -> bool:
    """Check if matrix is Hermitian within given tolerance."""
    return bool(np.allclose(matrix, matrix.conj().T, atol=tol))
