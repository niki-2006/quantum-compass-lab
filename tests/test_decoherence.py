"""Tests for Lindblad decoherence models, dissipators, and contrast decay."""

import numpy as np
import pytest
from src.spin_model import SpinModelConfig
from src.initial_states import get_initial_density_matrix
from src.decoherence import (
    get_lindblad_dissipators,
    build_liouvillian_decoherence_superoperator,
    compute_decoherence_rhs,
)
from src.experiment_runner import run_angular_sweep


def test_lindblad_dissipator_structure():
    """Verify dissipators are non-empty and correctly populated."""
    cfg_iso = SpinModelConfig(gamma_dephasing=1.5, gamma_relaxation=0.5, dephasing_model="isotropic")
    dissipators_iso = get_lindblad_dissipators(cfg_iso)
    assert len(dissipators_iso) == 8  # 6 isotropic (x,y,z for 2 electrons) + 2 relaxation

    cfg_axial = SpinModelConfig(gamma_dephasing=1.5, gamma_relaxation=0.5, dephasing_model="axial_z")
    dissipators_axial = get_lindblad_dissipators(cfg_axial)
    assert len(dissipators_axial) == 4  # 2 axial (z for 2 electrons) + 2 relaxation

    for L, rate in dissipators_iso:
        assert L.shape == (8, 8)
        assert rate > 0.0


def test_decoherence_superoperator_dimension():
    """Verify L_decoh is 64x64."""
    cfg = SpinModelConfig(gamma_dephasing=2.0)
    L_super = build_liouvillian_decoherence_superoperator(cfg)

    assert L_super.shape == (64, 64)


def test_decoherence_suppresses_contrast():
    """Verify that strong spin dephasing suppresses compass contrast."""
    cfg_ideal = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0, gamma_dephasing=0.0)
    cfg_noisy = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0, gamma_dephasing=15.0)

    res_ideal = run_angular_sweep(cfg_ideal, num_angles=25)
    res_noisy = run_angular_sweep(cfg_noisy, num_angles=25)

    assert res_ideal.metrics.contrast > res_noisy.metrics.contrast
    assert res_noisy.metrics.contrast < 0.02  # contrast washed out by strong dephasing


def test_pure_dephasing_t2_calibration():
    """
    Rigorously verify that pure dephasing (axial_z) produces exact transverse coherence decay:
    rho_01(t) = rho_01(0) * exp(-gamma * t), giving T2 = 1 / gamma,
    while preserving diagonal populations (T1 -> infinity).
    """
    from scipy.linalg import expm
    from src.operators import IDENTITY_2

    # Single-electron |+> = [1, 1]/sqrt(2), combined with |0> on S2 and |0> on nuclear spin
    plus_state = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
    n0 = np.array([1.0, 0.0], dtype=complex)
    psi_init = np.kron(plus_state, np.kron(n0, n0))
    rho_0 = np.outer(psi_init, psi_init.conj())

    gamma = 2.5  # us^-1
    cfg = SpinModelConfig(B_magnitude=0.0, A_xx=0.0, A_yy=0.0, A_zz=0.0,
                          k_S=0.0, k_T=0.0, gamma_dephasing=gamma, dephasing_model="pure_dephasing")
    L_super = build_liouvillian_decoherence_superoperator(cfg)

    t = 0.8  # us
    vec_t = expm(L_super * t) @ rho_0.flatten(order='F')
    rho_t = vec_t.reshape((8, 8), order='F')

    # Partial trace over S2 and nuclear to get reduced rho for S1
    # S1 basis: |0> corresponds to indices 0..3, |1> to 4..7
    rho_s1_01_init = np.sum([rho_0[i, i + 4] for i in range(4)])
    rho_s1_01_t = np.sum([rho_t[i, i + 4] for i in range(4)])
    rho_s1_00_t = np.sum([np.real(rho_t[i, i]) for i in range(4)])
    rho_s1_11_t = np.sum([np.real(rho_t[i + 4, i + 4]) for i in range(4)])

    # Transverse coherence decay: exp(-gamma * t)
    expected_ratio = np.exp(-gamma * t)
    actual_ratio = abs(rho_s1_01_t) / abs(rho_s1_01_init)
    assert np.isclose(actual_ratio, expected_ratio, atol=1e-12), f"T2 decay mismatch: {actual_ratio} vs {expected_ratio}"

    # Populations must be strictly preserved
    assert np.isclose(rho_s1_00_t, 0.5, atol=1e-12)
    assert np.isclose(rho_s1_11_t, 0.5, atol=1e-12)


def test_isotropic_depolarizing_t2_calibration():
    """
    Rigorously verify that isotropic depolarizing noise produces exact transverse coherence decay:
    rho_01(t) = rho_01(0) * exp(-gamma * t), giving T2 = 1 / gamma,
    while relaxing populations toward maximally mixed state (T1 = T2 = 1 / gamma).
    """
    from scipy.linalg import expm

    plus_state = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2.0)
    n0 = np.array([1.0, 0.0], dtype=complex)
    psi_init = np.kron(plus_state, np.kron(n0, n0))
    rho_0 = np.outer(psi_init, psi_init.conj())

    gamma = 2.0  # us^-1
    cfg = SpinModelConfig(B_magnitude=0.0, A_xx=0.0, A_yy=0.0, A_zz=0.0,
                          k_S=0.0, k_T=0.0, gamma_dephasing=gamma, dephasing_model="isotropic_depolarizing")
    L_super = build_liouvillian_decoherence_superoperator(cfg)

    t = 0.5  # us
    vec_t = expm(L_super * t) @ rho_0.flatten(order='F')
    rho_t = vec_t.reshape((8, 8), order='F')

    rho_s1_01_init = np.sum([rho_0[i, i + 4] for i in range(4)])
    rho_s1_01_t = np.sum([rho_t[i, i + 4] for i in range(4)])

    expected_ratio = np.exp(-gamma * t)
    actual_ratio = abs(rho_s1_01_t) / abs(rho_s1_01_init)
    assert np.isclose(actual_ratio, expected_ratio, atol=1e-12), f"Isotropic T2 mismatch: {actual_ratio} vs {expected_ratio}"

