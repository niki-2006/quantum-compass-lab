# Experimental Protocol & Benchmark Procedures

This document outlines the systematic, reproducible protocol for conducting and reproducing the six primary scientific experiments in the Quantum Compass Lab.

---

## Experiment 1: Field Orientation & Magnitude Sweep

- **Objective:** Evaluate whether the spin Hamiltonian yields direction-dependent singlet yield across the geomagnetic range ($25$ to $65\ \mu\text{T}$).
- **Parameter Grid:**
  - $B \in \{25.0, 50.0, 65.0\}\ \mu\text{T}$.
  - $\theta \in [0, 180^\circ]$ sampled in $2^\circ$ steps (91 angles).
  - Hyperfine tensor: $\mathbf{A} = \text{diag}(5.0, 5.0, 20.0)\ \text{rad}/\mu\text{s}$.
  - Kinetics: $k_S = 1.0\ \mu\text{s}^{-1}$, $k_T = 1.0\ \mu\text{s}^{-1}$.
- **Protocol:**
  1. Initialize state $\rho(0) = |S\rangle\langle S| \otimes \frac{1}{2}\mathbb{I}_2$.
  2. For each angle $\theta$, construct $H(\theta) = H_Z(B, \theta) + H_{\mathrm{hf}}$.
  3. Form Liouvillian generator $\mathcal{M}$ and compute $\Phi_S(\theta)$ via Green's function inversion.
  4. Record $\Phi_{S,\mathrm{min}}$, $\Phi_{S,\mathrm{max}}$, and compute contrast $C$.
- **Outputs:** `results/angular_response.png`, `results/experiment_1_angular_response.csv`.

---

## Experiment 2: Decoherence & Coherence-Time (T2) Sweep

- **Objective:** Quantify how environmental dephasing reduces directional sensitivity and determine the operational detectability threshold.
- **Parameter Grid:**
  - Dephasing rate: $\gamma \in [0.0, 20.0]\ \mu\text{s}^{-1}$ (corresponding to $T_2 = 1/\gamma \in [\infty, 0.05\ \mu\text{s}]$).
  - Noise models: Isotropic dephasing vs Axial $S_z$ dephasing.
  - $B = 50.0\ \mu\text{T}$.
- **Protocol:**
  1. Sweep $\theta$ for fixed $\gamma$ values ($0.0, 0.5, 2.0, 5.0, 15.0\ \mu\text{s}^{-1}$).
  2. Plot family of curves $\Phi_S(\theta; \gamma)$.
  3. Sweep $T_2$ on logarithmic scale and record contrast $C(T_2)$.
- **Outputs:** `results/decoherence_comparison.png`, `results/contrast_sweep.png`.

---

## Experiment 3: Hyperfine Anisotropy Sensitivity

- **Objective:** Determine the impact of tensor anisotropy ratio $A_{zz} / A_{xx}$ on signal shape and magnitude.
- **Parameter Grid:**
  - Anisotropy ratio: $R \in \{1.0, 2.0, 4.0, 8.0\}$ with $A_{xx} = 5.0\ \text{rad}/\mu\text{s}$ and $A_{zz} = 5.0 \times R\ \text{rad}/\mu\text{s}$.
- **Protocol:**
  1. For each ratio $R$, execute angular sweep.
  2. Overlay resulting curves to show symmetry breaking and contrast growth.
- **Outputs:** `results/hyperfine_sensitivity.png`.

---

## Experiment 4: Reaction Kinetics Sensitivity

- **Objective:** Examine the effect of differential recombination rates ($k_S \neq k_T$).
- **Protocol:**
  1. Vary $k_S / k_T$ from $0.2$ to $5.0$.
  2. Verify that total yield $\Phi_S + \Phi_T = 1.0$ is strictly conserved for all rate pairs.

---

## Experiment 5: Numerical Convergence Verification

- **Objective:** Demonstrate that the exact Liouvillian inversion, numerical time integration, and Qiskit Trotter evolution are converged and stable.
- **Protocol:**
  1. Horizon convergence: integrate $\int_0^{t_{\mathrm{max}}} p_S(t) dt$ for $t_{\mathrm{max}} \in [2, 4, 6, 8, 10, 14]\ \mu\text{s}$ and compare with exact $\Phi_S$.
  2. Trotter convergence: simulate unitary evolution at $t=1.0\ \mu\text{s}$ for Trotter steps $r \in [2, 5, 10, 20, 40]$ and compare with matrix exponential.
- **Outputs:** `results/convergence.png`.

---

## Experiment 6: Model Comparison & Rotational Symmetry Invariance

- **Objective:** Prove that an isotropic hyperfine tensor possesses spherical symmetry and yields zero angular contrast.
- **Protocol:**
  1. Set $A_{xx} = A_{yy} = A_{zz} = 10.0\ \text{rad}/\mu\text{s}$.
  2. Sweep $\theta \in [0, 180^\circ]$.
  3. Confirm $\Delta\Phi_S < 10^{-6}$ and $C = 0.00\%$.
