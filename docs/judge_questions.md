# Anticipated Judge Questions & Technically Accurate Answers
## Qiskit Fall Fest 2026 Presentation Preparation

---

### Question 1: "Your project abstract mentions two electron spins and one nuclear spin, but why did you use 3 qubits instead of 2?"
**Answer:**
> "In quantum mechanics, a spin-1/2 particle occupies a 2-dimensional Hilbert space. An explicit representation of two correlated electron spins ($S_1, S_2$) and one coupled nuclear spin ($I$) requires a tensor-product Hilbert space $\mathcal{H} = \mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \mathbb{C}^2$, which has dimension $2^3 = 8$. Mapping this directly onto a digital quantum circuit requires exactly 3 qubits (one per spin-1/2 particle). 
> While some pedagogical literature collapses the nuclear degree of freedom into an effective local magnetic field on one electron to yield a 2-qubit model, that effective approximation destroys the dynamic electron-nuclear entanglement and quantum state transfer that drive Singlet-Triplet interconversion. Therefore, we explicitly implemented the full 3-qubit physical model."

---

### Question 2: "Why does an isotropic hyperfine interaction yield zero angular contrast?"
**Answer:**
> "Under an isotropic hyperfine tensor, $\mathbf{A} = a\mathbb{I}$, the hyperfine Hamiltonian reduces to $H_{\mathrm{hf}} = a \mathbf{S}_1 \cdot \mathbf{I}$, which is a scalar product of two vector spin operators. This scalar product is spherically symmetric (invariant under simultaneous $SO(3)$ rotations of the spin coordinate frames). Similarly, the Zeeman interaction $\omega_0 \mathbf{b} \cdot (\mathbf{S}_1 + \mathbf{S}_2)$ depends only on the orientation of $\mathbf{b}$. 
> In the absence of an anisotropic tensor to break spatial symmetry, changing the direction of $\mathbf{b}$ simply corresponds to a global coordinate rotation that leaves the eigenvalues and transition transition matrix elements unchanged. Consequently, the time-integrated reaction yield $\Phi_S$ is completely independent of $\theta$ ($\Delta\Phi_S = 0, C = 0$). An anisotropic tensor ($A_{xx} = A_{yy} \neq A_{zz}$) is mathematically indispensable to define a molecular reference frame and generate compass sensitivity."

---

### Question 3: "Migratory birds navigate at body temperature (~40°C / 313 K). How can nuclear spins remain coherent, and how did you model the nuclear initial state?"
**Answer:**
> "At $310$ K, thermal energy $k_B T \approx 26$ meV is nearly five orders of magnitude larger than the nuclear Zeeman or hyperfine splitting ($\sim 10^{-7}$ eV). Therefore, nuclear polarization is virtually zero ($\sim 10^{-5}$ Boltzmann factor). We represent the nucleus as an **unpolarized, maximally mixed state** $\rho_N(0) = \frac{1}{2}\mathbb{I}_2$.
> To simulate this mixed state on quantum circuits without ancilla overhead, we use an **ensemble simulation strategy**: we execute complementary circuits initialized in $|S\rangle \otimes |0\rangle$ and $|S\rangle \otimes |1\rangle$, and average their expectation values with equal $50\%$ weight. This reproduces the unpolarized initial density matrix $\rho(0) = |S\rangle\langle S| \otimes \frac{1}{2}\mathbb{I}_2$ with complete statistical fidelity."

---

### Question 4: "Recombination in radical pairs is dissipative and trace-decreasing. How do you simulate that on unitary quantum circuits?"
**Answer:**
> "We implement two complementary simulation paths:
> 1. In our **classical reference physics engine**, we solve the open-system Haberkorn master equation directly using both Liouvillian Green's function inversion ($\vec{\rho}_{\mathrm{int}} = -\mathcal{M}^{-1}\vec{\rho}(0)$) and time-domain ODE integration.
> 2. In our **Qiskit circuit engine**, we simulate the coherent unitary spin dynamics $U(t) = \exp(-iHt)$ using Lie-Trotter synthesized circuits (`PauliEvolutionGate`), extract the instantaneous singlet probability $p_S(t) = \langle \psi(t) | P_S | \psi(t) \rangle$, and compute the reaction yield via weighted time-quadrature $\Phi_S = k_S \int_0^\infty p_S(t) e^{-kt} dt$. 
> We proved that for equal recombination rates $k_S = k_T = k$, the Haberkorn evolution is strictly equivalent to unitary evolution exponentially modulated by survival probability."

---

### Question 5: "How does decoherence affect the compass? Does noise always reduce directional sensitivity?"
**Answer:**
> "Our investigation reveals a nuanced physical dependency on the symmetry of the noise channel:
> - **Isotropic Dephasing:** When environmental fluctuations act symmetrically on $S_x, S_y, S_z$, spin coherence decays monotonically. For coherence times $T_2 < 1\ \mu\text{s}$, contrast drops rapidly, reaching $< 0.1\%$ by $T_2 = 0.07\ \mu\text{s}$.
> - **Axial $S_z$ Dephasing:** When noise acts purely along the $z$-axis, it commutes with $S_z$ and selectively damps transverse coherence. Because the magnetic field tilts relative to $z$, moderate axial noise can actually enhance the relative contrast between $\theta=0^\circ$ and $\theta=90^\circ$ before eventual suppression at very high rates.
> This demonstrates why specifying the physical symmetry of the decoherence model is essential."

---

### Question 6: "Can your circuits run on physical IBM Quantum backends? What are the limitations?"
**Answer:**
> "Yes, our circuit is transpilation-ready for IBM Quantum backends. However, simulating continuous Hamiltonian evolution over biological radical lifetimes ($t \sim 1\ \mu\text{s}$) requires at least 10–20 Lie-Trotter steps. With each Trotter repetition requiring two-qubit $R_{ZZ}$ or CNOT operations between electron and nuclear qubits, the total two-qubit gate depth reaches 40–80 CNOTs. 
> On current NISQ hardware (with two-qubit gate error rates around $0.5 - 1\%$), cumulative gate infidelity and decoherence wash out the delicate few-percent angular contrast signal. Therefore, we present quantum hardware execution as a transpiled readiness benchmark and clearly distinguish it from our exact statevector and classical reference results."
