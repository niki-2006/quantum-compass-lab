# Theoretical Model: Radical-Pair Magnetoreception

## 1. Biophysical Background
The radical-pair mechanism (RPM), first proposed in spin chemistry and extended to avian magnetoreception by Schulten (1978) and Ritz et al. (2000), posits that migratory birds detect the inclination of Earth's geomagnetic field via spin-correlated radical pairs in ocular cryptochrome photopigments.

In cryptochrome (CRY4):
1. **Light Absorption:** Blue photons ($\lambda \sim 450$ nm) photo-excite the flavin adenine dinucleotide (FAD) cofactor.
2. **Sequential Electron Transfer:** FAD accepts an electron from a conserved triad/tetrad of tryptophan residues (TrpH), forming the radical pair:
   $$\mathrm{FAD} + \mathrm{TrpH} \xrightarrow{h\nu} [\mathrm{FAD}^{\bullet -} \cdots \mathrm{TrpH}^{\bullet +}]$$
3. **Spin Correlation:** Because electron transfer occurs rapidly from a closed-shell singlet ground state, the radical pair is born in an electron-spin **singlet state** ($|S\rangle$).
4. **Coherent Spin Dynamics:** The two unpaired electrons ($S_1$ on $\mathrm{FAD}^{\bullet -}$, $S_2$ on $\mathrm{TrpH}^{\bullet +}$) evolve coherently under:
   - External Zeeman interaction with Earth's field ($\mathbf{B}$).
   - Anisotropic hyperfine couplings ($\mathbf{A}$) with nearby nuclear spins ($I$).
5. **Spin-Selective Recombination:**
   - Singlet recombination regenerates the resting state: $[\mathrm{FAD}^{\bullet -} \cdots \mathrm{TrpH}^{\bullet +}] \xrightarrow{k_S} \mathrm{FAD} + \mathrm{TrpH}$.
   - Triplet recombination proceeds to long-lived signaling conformers: $[\mathrm{FAD}^{\bullet -} \cdots \mathrm{TrpH}^{\bullet +}] \xrightarrow{k_T} \text{Signaling State}$.

Because the chemical yield depends on the fraction of radicals in the singlet state upon recombination, any factor influencing the rate of Singlet $\leftrightarrow$ Triplet interconversion—such as the orientation of $\mathbf{B}$ relative to the protein's hyperfine tensor—modulates the downstream biological signal.

---

## 2. Spin System & Hilbert Space Formulation
To model the core physics with absolute mathematical rigor, we implement an explicit **3-spin system**:
- **Electron 1 ($S_1$):** Spin-1/2 on $\mathrm{FAD}^{\bullet -}$.
- **Electron 2 ($S_2$):** Spin-1/2 on $\mathrm{TrpH}^{\bullet +}$.
- **Nuclear Spin ($I$):** Spin-1/2 coupled to $S_1$ (e.g., $^{14}$N or $^{1}$H).

The Hilbert space dimension is explicitly:
$$\mathcal{H} = \mathcal{H}_{S_1} \otimes \mathcal{H}_{S_2} \otimes \mathcal{H}_{I} \cong \mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \mathbb{C}^2 \quad (\dim = 8)$$

### Basis & State Vector Conventions
Standard computational basis:
$$|s_1, s_2, m_I\rangle, \quad s_1, s_2, m_I \in \{0, 1\}$$
where $|0\rangle = |\uparrow\rangle$ and $|1\rangle = |\downarrow\rangle$.

### Electron Singlet and Triplet States
Two-electron singlet:
$$|S\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$$

Two-electron triplets:
$$|T_+\rangle = |00\rangle, \quad |T_0\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |10\rangle), \quad |T_-\rangle = |11\rangle$$

In the full 8D Hilbert space, the projection operators are:
$$\hat{P}_S = |S\rangle\langle S| \otimes \mathbb{I}_2 = \left( \frac{1}{4}\mathbb{I}_4 - \mathbf{S}_1 \cdot \mathbf{S}_2 \right) \otimes \mathbb{I}_2$$
$$\hat{P}_T = \mathbb{I}_8 - \hat{P}_S$$

---

## 3. Initial Density Matrix
At ambient physiological temperature ($T \approx 310$ K), the thermal energy $k_B T \approx 26$ meV far exceeds nuclear Zeeman and hyperfine splittings ($\hbar \omega \sim 10^{-7}$ eV):
$$\frac{\hbar \omega}{k_B T} \sim 10^{-5} \ll 1$$
Therefore, the physical nuclear initial state is **unpolarized** (maximally mixed):
$$\rho_N(0) = \frac{1}{2}\mathbb{I}_2$$

The complete initial density matrix is:
$$\rho(0) = |S\rangle\langle S| \otimes \frac{1}{2}\mathbb{I}_2 = \frac{1}{2}\left( |S, 0\rangle\langle S, 0| + |S, 1\rangle\langle S, 1| \right)$$

---

## 4. Spin Hamiltonian
The total Hamiltonian consists of Zeeman and Hyperfine terms:
$$H = H_Z + H_{\mathrm{hf}}$$

### Zeeman Interaction ($H_Z$)
Assuming isotropic $g$-factors ($g_1 \approx g_2 \approx g_e \approx 2.0023$):
$$H_Z = \gamma_e \mathbf{B} \cdot (\mathbf{S}_1 + \mathbf{S}_2) = \omega_0 \mathbf{b} \cdot (\mathbf{S}_1 + \mathbf{S}_2)$$
where $\omega_0 = \gamma_e B$, and $\mathbf{b} = (\sin\theta\cos\phi, \sin\theta\sin\phi, \cos\theta)$ is the magnetic field unit vector.

### Hyperfine Interaction ($H_{\mathrm{hf}}$)
In the principal-axis frame of the hyperfine tensor:
$$\mathbf{A} = \begin{pmatrix} A_{xx} & 0 & 0 \\ 0 & A_{yy} & 0 \\ 0 & 0 & A_{zz} \end{pmatrix}$$
$$H_{\mathrm{hf}} = \mathbf{S}_1 \cdot \mathbf{A} \cdot \mathbf{I} = A_{xx} S_{1x} I_x + A_{yy} S_{1y} I_y + A_{zz} S_{1z} I_z$$

---

## 5. Symmetry & Rotational Invariance
- **Isotropic Tensor ($A_{xx} = A_{yy} = A_{zz} = a$):**
  $$H_{\mathrm{hf}} = a \mathbf{S}_1 \cdot \mathbf{I}$$
  Because $\mathbf{S}_1 \cdot \mathbf{I}$ and $\mathbf{b} \cdot (\mathbf{S}_1 + \mathbf{S}_2)$ are both invariant under simultaneous spatial rotations, rotating the field $\mathbf{B}$ merely rotates the eigenspaces without altering any transition frequencies or reaction yields.
  **Fundamental Theorem:** An isotropic radical-pair compass has strictly **zero directional contrast** ($\Delta \Phi_S = 0, C = 0$).
- **Anisotropic / Axial Tensor ($A_{xx} = A_{yy} \neq A_{zz}$):**
  Breaks spherical symmetry, defining a molecular reference axis ($z$). As the field angle $\theta$ relative to $z$ sweeps from $0^\circ$ to $180^\circ$, the effective splitting between magnetic sublevels changes, producing an orientation-dependent chemical yield $\Phi_S(\theta)$.
