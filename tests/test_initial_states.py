"""Tests for singlet state preparation and initial density matrix."""

import numpy as np
import pytest
from src.initial_states import get_pure_singlet_nuclear_states, get_initial_density_matrix
from src.operators import get_singlet_projector_3spin, is_hermitian


def test_pure_singlet_nuclear_states_orthonormal():
    """Verify |psi_0> and |psi_1> are normalized and mutually orthogonal."""
    psi0, psi1 = get_pure_singlet_nuclear_states()

    assert psi0.shape == (8,)
    assert psi1.shape == (8,)

    norm0 = np.vdot(psi0, psi0)
    norm1 = np.vdot(psi1, psi1)
    overlap = np.vdot(psi0, psi1)

    assert np.isclose(norm0, 1.0)
    assert np.isclose(norm1, 1.0)
    assert np.isclose(overlap, 0.0)


def test_initial_density_matrix_properties():
    """Verify rho(0) is Hermitian, has unit trace, and positive semi-definite."""
    rho_0 = get_initial_density_matrix(nuclear_polarization=0.0)

    assert rho_0.shape == (8, 8)
    assert is_hermitian(rho_0)
    assert np.isclose(np.trace(rho_0), 1.0)

    # Eigenvalues must be non-negative
    eigs = np.linalg.eigvalsh(rho_0)
    assert all(e >= -1e-14 for e in eigs)

    # Tr[P_S rho(0)] must equal 1.0 (pure singlet initially)
    p_s = get_singlet_projector_3spin()
    p_s_initial = np.real(np.trace(p_s @ rho_0))
    assert np.isclose(p_s_initial, 1.0)


def test_ensemble_equivalence():
    """Verify rho(0) matches 0.5 * (|psi_0><psi_0| + |psi_1><psi_1|)."""
    psi0, psi1 = get_pure_singlet_nuclear_states()
    rho_ensemble = 0.5 * (np.outer(psi0, psi0.conj()) + np.outer(psi1, psi1.conj()))
    rho_matrix = get_initial_density_matrix(nuclear_polarization=0.0)

    assert np.allclose(rho_ensemble, rho_matrix)
