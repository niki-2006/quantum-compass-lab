"""
Initial state preparation for radical-pair magnetoreception.

Physical Context:
- Radical pair formation: Photo-excitation of cryptochrome creates an entangled
  electron-spin singlet state |S> = (|01> - |10>) / sqrt(2) on [FAD*-, TrpH*+].
- Nuclear spin state: Under physiological ambient conditions (T ~ 310 K),
  the thermal energy k_B*T (~26 meV) vastly exceeds the nuclear Zeeman/hyperfine
  energy (< 10^-7 eV). Hence, the nuclear spin ensemble is physically unpolarized
  and described by the maximally mixed state rho_N = I / 2.
- Total density matrix:
  rho(0) = |S><S| (x) (I_2 / 2) = 1/2 [ |S,0><S,0| + |S,1><S,1| ]
"""

from __future__ import annotations
import numpy as np
from src.operators import get_singlet_state_2spin, get_singlet_projector_2spin, IDENTITY_2


def get_pure_singlet_nuclear_states() -> tuple[np.ndarray, np.ndarray]:
    """
    Return the two orthogonal 8D basis states representing an electron singlet
    with the nuclear spin in |0> (|up>) and |1> (|down>) respectively:
        |psi_0> = |S> (x) |0> = 1/sqrt(2) (|010> - |100>)
        |psi_1> = |S> (x) |1> = 1/sqrt(2) (|011> - |101>)

    These form the ensemble decomposition of the unpolarized initial density matrix:
        rho(0) = 0.5 * (|psi_0><psi_0| + |psi_1><psi_1|)

    Returns:
        tuple of two 8-element complex state vectors.
    """
    s_electron = get_singlet_state_2spin()  # shape (4,)

    # Nuclear |0> = [1, 0]^T
    n0 = np.array([1.0, 0.0], dtype=complex)
    psi_0 = np.kron(s_electron, n0)

    # Nuclear |1> = [0, 1]^T
    n1 = np.array([0.0, 1.0], dtype=complex)
    psi_1 = np.kron(s_electron, n1)

    return psi_0, psi_1


def get_initial_density_matrix(nuclear_polarization: float = 0.0) -> np.ndarray:
    """
    Construct the initial 8x8 density matrix rho(0) for the 3-spin system.

    Args:
        nuclear_polarization: Polarization degree p in [-1.0, 1.0].
            p = 0.0: unpolarized (maximally mixed) rho_N = I/2 (default physical case).
            p = 1.0: pure nuclear |0> (|up>).
            p = -1.0: pure nuclear |1> (|down>).
            In general: rho_N = ((1+p)/2)|0><0| + ((1-p)/2)|1><1|.

    Returns:
        8x8 complex Hermitian density matrix.
    """
    if not -1.0 <= nuclear_polarization <= 1.0:
        raise ValueError("nuclear_polarization must be between -1.0 and 1.0")

    rho_electrons = get_singlet_projector_2spin()  # 4x4
    p = nuclear_polarization
    rho_nuclear = np.array([
        [(1.0 + p) / 2.0, 0.0],
        [0.0, (1.0 - p) / 2.0]
    ], dtype=complex)

    rho_total = np.kron(rho_electrons, rho_nuclear)
    return rho_total
