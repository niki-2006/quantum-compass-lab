# Scientific Poster Presentation Content
## Qiskit Fall Fest 2026 Poster Layout

---

### 1. Title & Presenter Details
**Title:**
Quantum Compass Lab: Simulating Radical-Pair Magnetoreception Under Decoherence

**Authors & Affiliation:**
Quantum Biology & Quantum Information Research Group
Prepared for Qiskit Fall Fest 2026

**Complete 48x36" Research Poster Artifacts:**
- **Digital / Dark Theme (Vector PDF):** [docs/figures/quantum_compass_poster_dark.pdf](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/quantum_compass_poster_dark.pdf) | [PNG](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/quantum_compass_poster_dark.png) | [SVG](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/quantum_compass_poster_dark.svg)
- **Print / Light Theme (Vector PDF):** [docs/figures/quantum_compass_poster_print.pdf](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/quantum_compass_poster_print.pdf) | [PNG](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/quantum_compass_poster_print.png) | [SVG](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/quantum_compass_poster_print.svg)
- Synchronized in `results/`: [`results/quantum_compass_poster_dark.pdf`](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/quantum_compass_poster_dark.pdf) and [`results/quantum_compass_poster_print.pdf`](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/quantum_compass_poster_print.pdf)

---

### 2. Corrected Research Abstract
"Migratory birds are hypothesized to sense Earth's geomagnetic field (~25–65 µT) through the radical-pair mechanism, a quantum process in retinal cryptochrome proteins. Photo-excitation generates two correlated electron spins initialized in an entangled singlet state whose interconversion with triplet states is steered by geomagnetic and nuclear hyperfine interactions, modulating downstream chemical yields.

In this work, we model the radical pair as an explicit **three-qubit quantum system** in Qiskit and SciPy, comprising two electron spins and one coupled nuclear spin (Hilbert space dimension 8). We investigate directional reaction yields across geomagnetic field orientations, reproducing the angular anisotropy of the biological compass. We systematically evaluate open-system decoherence using Lindblad master equations and Qiskit quantum circuits, quantifying how spin dephasing ($T_2$) suppresses angular contrast. 

Our results verify that: (1) an anisotropic hyperfine tensor is mathematically necessary to break rotational symmetry and produce directional contrast; (2) under Earth's field (50 µT), the model generates ~13.3% angular contrast; and (3) isotropic dephasing with coherence times $T_2 < 0.2\ \mu$s suppresses contrast below operational detection thresholds. Finally, we establish cross-validation between classical Liouvillian solvers and Qiskit Trotter circuits, providing a reproducible quantum simulation framework connecting quantum information science with biological magnetoreception."

---

### 3. Introduction & Motivation
- **Avian Navigation Mystery:** Migratory songbirds navigate continents using an inclination compass sensitive to field direction rather than polarity.
- **Quantum Biology at Physiological Temperatures:** Cryptochrome photochemistry generates spin-correlated radical pairs $[\mathrm{FAD}^{\bullet-} \cdots \mathrm{TrpH}^{\bullet+}]$.
- **The Physics Question:** How can a weak geomagnetic field (~50 µT) alter chemical reaction yields against thermal noise ($k_B T \gg \hbar \gamma B$)? Answer: non-equilibrium coherent spin dynamics.

---

### 4. Research Gap & Challenges
- **Simplistic 2-Qubit Claims:** Prior simulations often omit the nuclear spin or incorrectly claim a 2-qubit system can explicitly model two electrons and a nuclear spin.
- **Unverified Noise Claims:** Decoherence is often assumed to always degrade contrast, ignoring noise symmetry and differential damping.
- **Lack of Open Validation:** Few open-source, verifiable platforms cross-validate quantum circuits against exact open-system master equations.

---

### 5. Methodology & System Architecture
```
+-----------------------------------------------------------------------------------+
|                            QUANTUM COMPASS LAB WORKFLOW                           |
+-----------------------------------------------------------------------------------+
|  [1] Biophysical Radical Pair                                                     |
|      FAD*- (S1) + TrpH*+ (S2) + 14N/1H Nucleus (I)                                |
|                              |                                                    |
|  [2] Explicit 3-Spin Hilbert Space (dim = 8)                                      |
|      Initial State: rho(0) = |S><S| (x) (I_2 / 2) [Unpolarized Nuclear Ensemble]  |
|                              |                                                    |
|  [3] Total Spin Hamiltonian                                                       |
|      H = omega_0 * b . (S1 + S2) + S1 . A . I                                     |
|                              |                                                    |
|           +------------------+-------------------+                                |
|           |                                      |                                |
|  [4A] Classical Reference               [4B] Qiskit Circuit Engine                |
|       - Liouvillian Green's Function         - 3-Qubit Circuit Mapping            |
|       - Haberkorn Reaction Sinks             - Lie-Trotter PauliEvolutionGate     |
|       - Lindblad Decoherence                 - Statevector / Aer Simulation       |
|           |                                      |                                |
|           +------------------+-------------------+                                |
|                              |                                                    |
|  [5] Cross-Validation: ||H_Qiskit - H_SciPy|| < 1e-12, Trotter Error < 1e-4        |
|                              |                                                    |
|  [6] Scientific Findings: Angular Contrast, Coherence Limits, Symmetry Proof      |
+-----------------------------------------------------------------------------------+
```

---

### 6. Theoretical Model & Key Equations
- **Hamiltonian:** $H = \omega_0 \mathbf{b} \cdot (\mathbf{S}_1 + \mathbf{S}_2) + \mathbf{S}_1 \cdot \mathbf{A} \cdot \mathbf{I}$
- **Haberkorn Master Equation:** $\frac{d\rho}{dt} = -i[H, \rho] - \frac{k_S}{2}\{P_S, \rho\} - \frac{k_T}{2}\{P_T, \rho\} + \mathcal{L}_{\mathrm{decoh}}(\rho)$
- **Singlet Reaction Yield:** $\Phi_S = k_S \int_0^\infty \mathrm{Tr}[P_S \rho(t)] dt = -k_S \mathrm{Tr}[P_S \mathcal{M}^{-1} \rho(0)]$
- **Yield Conservation:** $\Phi_S + \Phi_T = 1.000000$ (verified numerically).
- **Compass Contrast:** $C = \frac{\Phi_{S,\mathrm{max}} - \Phi_{S,\mathrm{min}}}{\Phi_{S,\mathrm{max}} + \Phi_{S,\mathrm{min}}}$

---

### 7. Experimental Results

#### Figure 1: Directional Compass Response
- **Parameters:** $B = 50\ \mu\text{T}$, $\mathbf{A} = \text{diag}(5, 5, 20)\ \text{rad}/\mu\text{s}$, $k_S = k_T = 1.0\ \mu\text{s}^{-1}$.
- **Result:** Singlet yield varies smoothly from $\Phi_{S,\mathrm{min}} = 0.3726$ (at $\theta = 32^\circ$) to $\Phi_{S,\mathrm{max}} = 0.4872$ (at $\theta = 0^\circ$).
- **Contrast:** $C = 13.32\%$, $\Delta\Phi_S = 0.1146$.
- *Saved Files:* `results/angular_response.png`, `docs/figures/poster_figure_angular_sweep.{png,svg,pdf}`, `results/poster_figure_angular_sweep.{png,svg,pdf}`

#### Figure 2: Impact of Decoherence ($T_2$ Lifetime)
- **Result:** Isotropic depolarizing noise monotonically suppresses directional sensitivity ($T_1 = T_2 = 1/\gamma$).
  - $T_2 = \infty$ (Coherent Limit): $C = 13.32\%$, $\Delta\Phi_S = 0.1145$
  - $T_2 = 2.0\ \mu\text{s}$: $C = 7.10\%$, $\Delta\Phi_S = 0.0571$
  - $T_2 = 0.5\ \mu\text{s}$: $C = 2.34\%$, $\Delta\Phi_S = 0.0151$
  - $T_2 = 0.15\ \mu\text{s}$: $C = 0.25\%$, $\Delta\Phi_S = 0.0014$ (Threshold boundary: $\Delta\Phi_S \ge 0.001$)
  - $T_2 = 0.03\ \mu\text{s}$: $C = 0.0006\%$, $\Delta\Phi_S = 3.0 \times 10^{-6}$
- **Computational Detectability Threshold:** Coherence must persist for $T_2 \ge 0.15\ \mu\text{s}$ for $\Delta\Phi_S \ge 0.001$, and $T_2 \ge 0.36\ \mu\text{s}$ for $C \ge 0.01$ (model-dependent computational threshold).
- *Saved File:* `results/decoherence_comparison.png` & `results/contrast_sweep.png`

#### Figure 3: Symmetry Invariance Proof
- **Isotropic ($A_{xx}=A_{yy}=A_{zz}$):** $\Delta\Phi_S = 5.0 \times 10^{-16}$, $C = 5.4 \times 10^{-16}$ (strictly zero within machine precision).
- **Anisotropic ($A_{zz}/A_{xx} = 4$):** $\Delta\Phi_S = 0.1145$, $C = 13.32\%$.
- *Saved File:* `results/hyperfine_sensitivity.png`

#### Figure 4: Numerical Convergence & Qiskit Cross-Validation
- **Panel 1 (Truncation Tail):** Analytical tail integral drops exponentially below $10^{-5}$ by $t_{\mathrm{max}} = 8\ \mu\text{s}$.
- **Panel 2 (Quadrature Error):** Numerical quadrature error converges quadratically as $O(\Delta t^2)$, reaching $< 2 \times 10^{-6}$ at $\Delta t = 0.005\ \mu\text{s}$.
- **Panel 3 (Trotter Discretization):** Lie-Trotter decomposed circuit evolution on non-commuting spin Hamiltonian ($[H_Z, H_{\mathrm{hf}}] \neq 0$) converges monotonically in full-state norm error and unitary operator error as $O(1/r)$, resolving previous undecomposed operator evaluation.
- *Saved File:* `results/convergence.png`

---

### 8. Applications & Use Cases
1. **Bio-Inspired Quantum Sensing:** Design principles for room-temperature quantum magnetometers mimicking cryptochrome.
2. **Quantum Information Education:** Clean pedagogical platform for teaching open quantum systems, Trotterization, and tensor products in Qiskit.
3. **Evaluating Environmental RF Noise:** Testing the vulnerability of quantum biological systems to anthropogenic electromagnetic noise (e.g. broadband RF disruption of avian migration).

---

### 9. Conclusions & Key Contributions
- Implemented and validated an explicit 3-qubit radical-pair compass model.
- Proved rotational symmetry breaking as the indispensable physical foundation for directional magnetoreception.
- Quantified coherence-time thresholds ($T_2 \gtrsim 0.2\ \mu\text{s}$) necessary to maintain a detectable compass signal.
- Delivered an open, interactive Streamlit laboratory dashboard with 100% automated test verification.

---

### 10. Future Work & Hardware Readiness
- Extension to multiple nuclear spins via tensor network simulators (matrix product states).
- Hardware execution on IBM Quantum Heron processors utilizing error mitigation (zero-noise extrapolation).
- Incorporation of non-Markovian environmental baths.

---

### 11. References
- Schulten et al., *Z. Phys. Chem.* 111, 1 (1978).
- Ritz et al., *Biophys. J.* 78, 707 (2000).
- Hore & Mouritsen, *Annu. Rev. Biophys.* 45, 299 (2016).
- Haberkorn, *Mol. Phys.* 32, 1491 (1976).
