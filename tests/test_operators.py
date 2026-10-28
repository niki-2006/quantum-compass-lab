"""Tests for spin operators, projectors, and algebraic properties."""

import numpy as np
import pytest
from src.operators import (
    S_X, S_Y, S_Z,
    embed_operator_3spin,
    get_spin_operators_3spin,
    get_singlet_state_2spin,
    get_singlet_projector_2spin,
    get_triplet_projector_2spin,
    get_singlet_projector_3spin,
    get_triplet_projector_3spin,
    is_hermitian,
    IDENTITY_2, IDENTITY_4, IDENTITY_8
)


def test_pauli_commutation_relations():
    """Verify [S_x, S_y] = i S_z."""
    comm = S_X @ S_Y - S_Y @ S_X
    expected = 1.0j * S_Z
    assert np.allclose(comm, expected)


def test_embed_operator_dimensions():
    """Verify embedded operators are 8x8."""
    op8 = embed_operator_3spin(S_Z, 0)
    assert op8.shape == (8, 8)
    assert is_hermitian(op8)


def test_spin_operators_dictionary():
    """Verify all 9 spin operators exist and are Hermitian."""
    ops = get_spin_operators_3spin()
    expected_keys = {"S1x", "S1y", "S1z", "S2x", "S2y", "S2z", "Ix", "Iy", "Iz"}
    assert set(ops.keys()) == expected_keys
    for k, v in ops.items():
        assert v.shape == (8, 8)
        assert is_hermitian(v)


def test_singlet_projector_algebra_2spin():
    """Verify P_S properties in 2-electron space."""
    ps = get_singlet_projector_2spin()
    pt = get_triplet_projector_2spin()

    # Dimension and Hermiticity
    assert ps.shape == (4, 4)
    assert is_hermitian(ps)
    assert is_hermitian(pt)

    # Idempotence: P^2 = P
    assert np.allclose(ps @ ps, ps)
    assert np.allclose(pt @ pt, pt)

    # Completeness: P_S + P_T = I_4
    assert np.allclose(ps + pt, IDENTITY_4)

    # Orthogonality: P_S P_T = 0
    assert np.allclose(ps @ pt, np.zeros((4, 4)))

    # Trace: Tr[P_S] = 1, Tr[P_T] = 3
    assert np.isclose(np.trace(ps), 1.0)
    assert np.isclose(np.trace(pt), 3.0)


def test_singlet_projector_algebra_3spin():
    """Verify P_S properties in 3-spin 8D space."""
    ps = get_singlet_projector_3spin()
    pt = get_triplet_projector_3spin()

    assert ps.shape == (8, 8)
    assert pt.shape == (8, 8)
    assert np.allclose(ps @ ps, ps)
    assert np.allclose(pt @ pt, pt)
    assert np.allclose(ps + pt, IDENTITY_8)
    assert np.isclose(np.trace(ps), 2.0)  # 1 * 2 for nuclear degeneracy
    assert np.isclose(np.trace(pt), 6.0)  # 3 * 2 for nuclear degeneracy
