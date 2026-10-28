"""Tests for Hamiltonian construction, Zeeman, and Hyperfine interactions."""

import numpy as np
import pytest
from src.spin_model import SpinModelConfig
from src.hamiltonian import (
    build_zeeman_hamiltonian,
    build_hyperfine_hamiltonian,
    build_total_hamiltonian,
)
from src.operators import is_hermitian


def test_hamiltonian_dimensions_and_hermiticity():
    """Verify H_Z, H_hf, and H_total are 8x8 Hermitian matrices."""
    cfg = SpinModelConfig(B_magnitude=50.0, theta=0.6, phi=0.3, A_xx=5.0, A_yy=5.0, A_zz=20.0)

    hz = build_zeeman_hamiltonian(cfg)
    hhf = build_hyperfine_hamiltonian(cfg)
    htot = build_total_hamiltonian(cfg)

    assert hz.shape == (8, 8)
    assert hhf.shape == (8, 8)
    assert htot.shape == (8, 8)

    assert is_hermitian(hz)
    assert is_hermitian(hhf)
    assert is_hermitian(htot)


def test_zeeman_field_proportionality():
    """Verify doubling B doubles H_Z."""
    cfg1 = SpinModelConfig(B_magnitude=25.0, theta=0.5, phi=0.5)
    cfg2 = SpinModelConfig(B_magnitude=50.0, theta=0.5, phi=0.5)

    hz1 = build_zeeman_hamiltonian(cfg1)
    hz2 = build_zeeman_hamiltonian(cfg2)

    assert np.allclose(2.0 * hz1, hz2)


def test_hyperfine_independent_of_field_angle():
    """Verify H_hf depends only on tensor A, not on field orientation theta/phi."""
    cfg1 = SpinModelConfig(B_magnitude=50.0, theta=0.0, phi=0.0, A_xx=4.0, A_yy=4.0, A_zz=16.0)
    cfg2 = SpinModelConfig(B_magnitude=50.0, theta=1.5, phi=2.0, A_xx=4.0, A_yy=4.0, A_zz=16.0)

    hhf1 = build_hyperfine_hamiltonian(cfg1)
    hhf2 = build_hyperfine_hamiltonian(cfg2)

    assert np.allclose(hhf1, hhf2)
