# Model Assumptions, Approximations, and Biological Limitations

## 1. Key Assumptions

1. **Spin System Truncation:**
   - Real avian cryptochrome (e.g. European robin *Erithacus rubecula* Cry4) contains the flavin radical ($\mathrm{FAD}^{\bullet-}$) with multiple nitrogen ($^{14}\text{N}$) and proton ($^{1}\text{H}$) nuclear spins, coupled to a tryptophan radical ($\text{TrpH}^{\bullet+}$) which also possesses numerous nuclear spins.
   - Our model truncates this complex spin bath to **one representative nuclear spin-1/2 coupled to electron 1**. This is the minimal model capable of demonstrating the radical-pair compass mechanism with explicit electron-nuclear quantum dynamics.

2. **Nuclear Spin Quantum Number:**
   - We model the nucleus as a spin-1/2 particle ($d=2$) for direct mapping to a single qubit. The most prominent nitrogen nuclei in flavin rings are $^{14}\text{N}$, which are spin-1 ($d=3$). While spin-1 nuclei introduce quadrupolar interactions and 3-level nuclear manifolds, the qualitative mechanism of anisotropic hyperfine-driven singlet-triplet conversion is faithfully preserved in the spin-1/2 model.

3. **Inter-Radical Interactions:**
   - Direct exchange ($J$) and dipolar ($D$) couplings between electron 1 and electron 2 are assumed small compared to hyperfine couplings ($J, D \ll A$) due to the spatial separation ($\sim 1.5 - 2.0$ nm) in cryptochrome. We set $J = 0, D = 0$.

4. **Kinetics:**
   - Recombination is modeled via the phenomenological Haberkorn anticommutator sink. While non-Hermitian and trace-decreasing, it accurately captures the depletion of the surviving radical pair pool into ground state and signaling products.

---

## 2. Scientific Limitations

1. **Not a Proof of Avian Magnetonavigation:**
   - Simulating directional sensitivity in a 3-qubit model demonstrates the physical feasibility of the quantum compass hypothesis, but does not prove that migrating birds navigate solely via this mechanism. Behavioral, electrophysiological, and biochemical investigations remain ongoing in quantum biology.

2. **Decoherence Simplifications:**
   - We model environmental noise as Markovian Lindblad dephasing and relaxation. In biological protein matrices, spin-bath dynamics may exhibit non-Markovian memory effects and structured spectral densities.

3. **Quantum Hardware vs Ideal Simulation:**
   - Qiskit circuits running on NISQ devices suffer from gate infidelity (Trotter gate accumulation) and readout errors. Matrix exponential and statevector simulations provide exact numerical benchmarks for this small 3-qubit Hilbert space.
