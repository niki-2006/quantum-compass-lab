# Equations, Constants, and Unit Conventions

## 1. Physical Constants and Unit System

We use the standard angular frequency unit convention ($\hbar = 1$):
- **Time ($t$):** Microseconds ($\mu\text{s}$).
- **Rates and Angular Frequencies ($\omega, k, \gamma$):** $\text{rad}/\mu\text{s}$ or $\mu\text{s}^{-1}$.
- **Frequency ($\nu$):** $\nu = \omega / (2\pi)$ in Megahertz (MHz).
- **Magnetic Field ($B$):** Microtesla ($\mu\text{T}$).

### Physical Values
| Quantity | Symbol | Numerical Value | Physical Unit |
|:---|:---:|:---:|:---|
| Reduced Planck Constant | $\hbar$ | $1.0545718 \times 10^{-34}$ | $\text{J}\cdot\text{s}$ |
| Bohr Magneton | $\mu_B$ | $9.274010 \times 10^{-24}$ | $\text{J}/\text{T}$ |
| Free Electron $g$-factor | $g_e$ | $2.0023193$ | Dimensionless |
| Electron Gyromagnetic Ratio | $\gamma_e = g_e \mu_B / \hbar$ | $1.7608596 \times 10^{11}$ | $\text{rad}/(\text{s}\cdot\text{T})$ |
| Scaled Gyromagnetic Ratio | $\gamma_e$ | $0.17608596$ | $\text{rad}/(\mu\text{s}\cdot\mu\text{T})$ |
| Earth's Magnetic Field | $B$ | $25.0 \text{ to } 65.0$ | $\mu\text{T}$ (geomagnetic range) |
| Standard Earth Field | $B_0$ | $50.0$ | $\mu\text{T}$ ($0.05$ mT) |
| Earth Zeeman Frequency | $\omega_0 = \gamma_e B_0$ | $8.8043$ | $\text{rad}/\mu\text{s}$ ($\nu_0 \approx 1.401$ MHz) |

---

## 2. Complete Equation Suite

### 1. Haberkorn Master Equation
$$\frac{d\rho(t)}{dt} = -i[H, \rho(t)] - \frac{k_S}{2}\{P_S, \rho(t)\} - \frac{k_T}{2}\{P_T, \rho(t)\} + \mathcal{L}_{\mathrm{decoh}}(\rho(t))$$

Where:
- $\{A, B\} = AB + BA$ denotes the anticommutator.
- $P_S$ is the 8D singlet projector.
- $P_T = \mathbb{I}_8 - P_S$ is the 8D triplet projector.

### 2. Lindblad Dissipator
$$\mathcal{L}_{\mathrm{decoh}}(\rho) = \sum_{k} \Gamma_k \left( L_k \rho L_k^\dagger - \frac{1}{2}\{L_k^\dagger L_k, \rho\} \right)$$

- **Isotropic Depolarizing Noise:** $L_{j,\alpha} = \sigma_{j,\alpha}$ for $j \in \{1, 2\}$, $\alpha \in \{x, y, z\}$ with rate $\Gamma_{\mathrm{iso}} = \gamma / 4$, yielding transverse coherence decay $\rho_{01}(t) \propto e^{-\gamma t}$ and $T_1 = T_2 = 1/\gamma$.
- **Pure Phase Damping (Dephasing along z):** $L_{j,z} = \sigma_{j,z}$ with rate $\Gamma_z = \gamma / 2$, yielding transverse coherence decay $\rho_{01}(t) \propto e^{-\gamma t}$, $T_2 = 1/\gamma$, with diagonal populations strictly conserved ($T_1 \to \infty$).

### 3. Integrated Reaction Yields
$$\Phi_S = k_S \int_0^\infty \mathrm{Tr}[P_S \rho(t)] \, dt$$
$$\Phi_T = k_T \int_0^\infty \mathrm{Tr}[P_T \rho(t)] \, dt$$

Exact Liouville-Green's Function representation:
$$\vec{\rho}_{\mathrm{int}} = -\mathcal{M}^{-1} \vec{\rho}(0)$$
$$\Phi_S = k_S \mathrm{Tr}[P_S \rho_{\mathrm{int}}], \quad \Phi_T = k_T \mathrm{Tr}[P_T \rho_{\mathrm{int}}]$$

Exact Truncated Yield on $[0, t_{\mathrm{max}}]$:
$$\Phi_S(t_{\mathrm{max}}) = k_S \mathrm{Tr}\left[ P_S \text{unvec}\left( \mathcal{M}^{-1}(e^{\mathcal{M} t_{\mathrm{max}}} - \mathbb{I}) \vec{\rho}(0) \right) \right]$$

Analytical Tail Integral:
$$\Delta_{\mathrm{tail}}(t_{\mathrm{max}}) = \Phi_S(\infty) - \Phi_S(t_{\mathrm{max}}) = -k_S \mathrm{Tr}\left[ P_S \text{unvec}\left( \mathcal{M}^{-1} e^{\mathcal{M} t_{\mathrm{max}}} \vec{\rho}(0) \right) \right]$$

### 4. Yield Conservation
$$\Phi_S + \Phi_T = 1.0000000000$$

### 5. Compass Contrast Metric
$$C = \frac{\Phi_{S,\mathrm{max}} - \Phi_{S,\mathrm{min}}}{\Phi_{S,\mathrm{max}} + \Phi_{S,\mathrm{min}}}$$

### 6. Absolute Yield Anisotropy
$$\Delta \Phi_S = \Phi_{S,\mathrm{max}} - \Phi_{S,\mathrm{min}}$$

### 7. Model-Dependent Computational Detectability Criteria
- **Absolute Anisotropy Criterion:** $\Delta\Phi_S \ge 0.001$ ($0.1\%$ absolute chemical yield variation across field orientation). Model threshold: $T_2 \ge 0.15\ \mu\text{s}$.
- **Normalized Contrast Criterion:** $C \ge 0.01$ ($1.0\%$ normalized modulation depth). Model threshold: $T_2 \ge 0.36\ \mu\text{s}$.
- *Note:* These are model-dependent engineering and analysis thresholds, not biological detection thresholds.
