# Quantum Compass Lab 🧭
### Simulating Radical-Pair Magnetoreception Under Decoherence
*A multidisciplinary research project prepared for Qiskit Fall Fest 2026*

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.x-6929C4.svg)](https://qiskit.org/)
[![Qiskit Aer](https://img.shields.io/badge/Qiskit--Aer-0.18.0-3B82F6.svg)](https://github.com/Qiskit/qiskit-aer)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42.0-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-82%20Passing%20(0%20warnings)-success.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🔬 Executive Summary

Migratory songbirds navigate across continents using an inclination compass sensitive to the orientation of Earth's geomagnetic field (~25–65 µT). The leading quantum biological hypothesis—the **radical-pair mechanism (RPM)**—posits that blue-light photoexcitation of cryptochrome photopigments in the retina generates a spin-correlated radical pair ($[\mathrm{FAD}^{\bullet-} \cdots \mathrm{TrpH}^{\bullet+}]$) initialized in an entangled electron singlet state ($|S\rangle$). The interplay between weak geomagnetic Zeeman interactions and internal nuclear hyperfine interactions modulates coherent singlet-triplet oscillations, determining downstream chemical signaling yields.

**Quantum Compass Lab** provides an explicit, mathematically rigorous **3-qubit simulation framework** combining:
1. **Classical Reference Engine:** Exact 64×64 Liouvillian Green's function solver, Haberkorn non-unitary reaction sinks, and Lindblad open-system master equations in SciPy.
2. **Qiskit Quantum Circuit Engine:** Explicit 3-qubit mapping, Bell-state singlet preparation, unpolarized nuclear ensemble averaging, and first-order Lie-Trotter Hamiltonian synthesis with decomposed `PauliEvolutionGate`.
3. **Interactive Research Dashboard:** Laboratory interface built in Streamlit featuring live parameter sweeps, real-time dynamics, decoherence analysis, and export tools.
4. **Automated Verification:** 82 unit, integration, and regression tests confirming yield conservation ($\Phi_S + \Phi_T = 1.0$), density-matrix eigenvalue positivity ($\lambda_{\min} \ge -10^{-10}$), rotational symmetry invariance, and Qiskit-SciPy cross-validation.

---

## 📊 Key Research Findings

1. **Rotational Symmetry & Anisotropy:** An isotropic hyperfine tensor ($A_{xx}=A_{yy}=A_{zz}$) possesses continuous spherical symmetry, producing **strictly zero compass contrast** ($C = 0.00\%$, $\Delta\Phi_S = 5.0 \times 10^{-16}$). An anisotropic tensor ($A_{zz}/A_{xx} = 4$) breaks rotational symmetry, yielding **$13.32\%$ contrast** under Earth's field ($50\ \mu\text{T}$).
2. **Decoherence Sensitivity Threshold:** Isotropic spin dephasing with coherence lifetimes $T_2 < 0.15\ \mu\text{s}$ ($\gamma > 6.67\ \mu\text{s}^{-1}$) suppresses directional contrast below operational thresholds ($\Delta\Phi_S < 0.001$), explaining why long-lived spin coherence is essential in cryptochrome.
3. **Cross-Validation Agreement:** SciPy exact matrix exponentiation and Qiskit Trotter circuit simulation agree to within $3.55 \times 10^{-15}$ in spectrum and exhibit monotone $O(1/r)$ convergence for non-commuting $[H_Z, H_{\mathrm{hf}}] \neq 0$.

---

## 📈 Poster Presentation Figures

| Figure | Description | File Path |
|---|---|---|
| **Figure 1: Angular Sweep** | Singlet yield $\Phi_S(\theta)$ vs polar angle $\theta \in [0^\circ, 180^\circ]$ at $B = 50\ \mu\text{T}$. Labeled max ($0.4872$ at $0^\circ$), min ($0.3726$ at $32^\circ$), and isotropic control flat line ($\Phi_S = 0.4595$). | [`angular_sweep.png`](angular_sweep.png) |
| **Figure 2: Contrast vs Decoherence** | Directional contrast $C = \frac{\Delta\Phi_S}{\Phi_{\max}+\Phi_{\min}}$ vs decoherence rate $\gamma = 1/T_2$ on a log-scale x-axis, highlighting the operational threshold ($C = 1.0\%$) at $\gamma \approx 2.74\ \mu\text{s}^{-1}$ ($T_2 \approx 0.36\ \mu\text{s}$). | [`contrast_vs_decoherence.png`](contrast_vs_decoherence.png) |
| **Full Poster (Dark Theme)** | Complete 48×36 inch conference poster canvas for digital displays. | [`docs/figures/quantum_compass_poster_dark.pdf`](docs/figures/quantum_compass_poster_dark.pdf) |
| **Full Poster (Print Theme)** | Complete 48×36 inch conference poster canvas for physical printing. | [`docs/figures/quantum_compass_poster_print.pdf`](docs/figures/quantum_compass_poster_print.pdf) |

---

## ⚙️ Model Parameters

| Parameter | Symbol | Value (Code) | Physical Equivalent | Physical Description |
|---|---|---|---|---|
| **Geomagnetic Field Magnitude** | $B_0$ | $50.0\ \mu\text{T}$ | $0.050\ \text{mT}$ | Earth ambient field (typical temperate latitude) |
| **Larmor Frequency** | $\omega_0 = \gamma_e B_0$ | $8.7941\ \text{rad}/\mu\text{s}$ | $1.3996\ \text{MHz}$ | Electron Zeeman precession rate ($\gamma_e = 0.176086\ \text{rad}/(\mu\text{s}\cdot\mu\text{T})$) |
| **Field Polar Angle** | $\theta$ | $0^\circ \to 180^\circ$ (91 points) | Steps of $2.0^\circ$ | Geomagnetic inclination angle relative to molecular $\hat{z}$ axis |
| **Field Azimuthal Angle** | $\phi$ | $0.0\ \text{rad}$ | $0^\circ$ | Reference azimuthal orientation |
| **Hyperfine Coupling (Axial)** | $A_{xx}, A_{yy}$ | $5.0\ \text{rad}/\mu\text{s}$ | $0.796\ \text{MHz}$ ($28.4\ \mu\text{T}$) | Perpendicular hyperfine interaction with nucleus $I=1/2$ |
| **Hyperfine Coupling (Symmetry)** | $A_{zz}$ | $20.0\ \text{rad}/\mu\text{s}$ | $3.183\ \text{MHz}$ ($113.6\ \mu\text{T}$) | Parallel hyperfine interaction along symmetry axis $\hat{z}$ |
| **Anisotropy Ratio** | $A_{zz} / A_{xx}$ | $4.0$ | Dimensionless | Ratio breaking spherical rotational symmetry |
| **Isotropic Control Coupling** | $A_{\mathrm{iso}}$ | $10.0\ \text{rad}/\mu\text{s}$ | $1.592\ \text{MHz}$ ($56.8\ \mu\text{T}$) | Spherical control tensor ($A_{xx}=A_{yy}=A_{zz}=10$) |
| **Singlet Reaction Sink Rate** | $k_S$ | $1.0\ \mu\text{s}^{-1}$ | Lifetime $\tau_S = 1.0\ \mu\text{s}$ | Haberkorn decay rate into ground-state signaling product |
| **Triplet Reaction Sink Rate** | $k_T$ | $1.0\ \mu\text{s}^{-1}$ | Lifetime $\tau_T = 1.0\ \mu\text{s}$ | Haberkorn decay rate into non-signaling triplet product |
| **Coherent Limit Dephasing** | $\gamma_{\mathrm{deph}}$ | $0.0\ \mu\text{s}^{-1}$ | $T_2 \to \infty$ | Baseline unperturbed quantum evolution |
| **Decoherence Sweep Range** | $\gamma = 1/T_2$ | $0.05 \to 31.62\ \mu\text{s}^{-1}$ | $T_2 \in [0.03, 20.0]\ \mu\text{s}$ | Range explored in Experiment 2 |
| **Critical Lifetime ($\Delta\Phi_S \ge 0.001$)** | $T_{2,\mathrm{crit}}$ | $0.15\ \mu\text{s}$ | $\gamma \le 6.67\ \mu\text{s}^{-1}$ | Model computational detectability threshold |
| **Critical Lifetime ($C \ge 1.0\%$)** | $T_{2,\mathrm{contrast}}$ | $0.36\ \mu\text{s}$ | $\gamma \le 2.74\ \mu\text{s}^{-1}$ | Minimum coherence lifetime for $\ge 1\%$ relative contrast |
| **Initial State** | $\rho(0)$ | $|S\rangle\langle S| \otimes \frac{I_2}{2}$ | $\dim = 8$ | Entangled singlet electron pair $\otimes$ maximally mixed nuclear ensemble |

---

## 🔬 Qiskit Trotter Validation Results

Trotter synthesis of $e^{-i H t}$ on the 3-qubit register with non-commuting $[H_Z, H_{\mathrm{hf}}] \neq 0$ evaluated against exact matrix exponentiation ($\theta = \pi/4$, $B = 50\ \mu\text{T}$):

### Primary Validation Horizon ($t = 0.5\ \mu\text{s}$):
| Trotter Steps ($r$) | Singlet Expectation Error $|\Delta P_S|$ | Statevector Norm Error $\|\psi_{\mathrm{trot}} - \psi_{\mathrm{ex}}\|_2$ | State Infidelity ($1 - F$) | Unitary Operator Error $\|U_{\mathrm{trot}} - U_{\mathrm{ex}}\|_F$ |
|---|---|---|---|---|
| $r = 1$ | $9.9062 \times 10^{-2}$ | $0.9976$ | $0.7458$ | $3.9906$ |
| $r = 2$ | $2.7522 \times 10^{-1}$ | $0.9140$ | $0.6441$ | $2.5065$ |
| $r = 4$ | $9.2038 \times 10^{-2}$ | $0.3512$ | $0.1166$ | $1.0951$ |
| $r = 8$ | $2.2165 \times 10^{-2}$ | $0.1584$ | $0.0241$ | $0.5247$ |
| $r = 16$ | $5.4748 \times 10^{-3}$ | $0.0765$ | $0.0056$ | $0.2596$ |
| **$r = 25$ (Benchmark)** | **$2.2369 \times 10^{-3}$** | **$0.0485$** | **$0.0023$** | **$0.1658$** |
| $r = 32$ | $1.3644 \times 10^{-3}$ | $0.0378$ | $0.0014$ | $0.1294$ |

*At the test suite benchmark ($r = 25$), SciPy matrix exponentiation yields $P_S = 0.598284$ and the decomposed Qiskit circuit yields $P_S = 0.600057$, demonstrating agreement within $0.22\%$ ($1.77 \times 10^{-3}$).*

---

## 🗂️ Project Structure

```
Mangnetoreception/
├── angular_sweep.png           # User figure: Phi_S vs theta (300 DPI, 6x4 in)
├── contrast_vs_decoherence.png # User figure: Contrast vs decoherence rate (300 DPI, 6x4 in)
├── app.py                      # Interactive Streamlit Laboratory Dashboard
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Build & test configuration
├── README.md                   # Complete documentation & GitHub instructions
├── .gitignore                  # Git exclusion rules
│
├── src/                        # Physics and Simulation Core Engine
│   ├── operators.py            # Spin-1/2 operators, embeddings, P_S & P_T projectors
│   ├── initial_states.py       # Singlet prep, unpolarized nuclear state, density matrices
│   ├── spin_model.py           # SpinModelConfig dataclass
│   ├── hamiltonian.py          # Zeeman, Hyperfine, and Total 8x8 Hamiltonians
│   ├── reaction_kinetics.py    # Haberkorn master equation & Liouville Green's function
│   ├── decoherence.py          # Lindblad dissipators (isotropic and axial T2/T1)
│   ├── evolution.py            # Unitary evolution & time-domain ODE trajectory solvers
│   ├── qiskit_backend.py       # Qiskit 3-qubit circuits, PauliEvolutionGate, Trotterization
│   ├── experiment_runner.py    # Standardized suite for Experiments 1 through 6
│   ├── metrics.py              # Compass contrast C, Delta_Phi_S, and detectability
│   ├── validation.py           # Automated physical and numerical sanity audits
│   └── plotting.py             # Research-theme scientific visualizations
│
├── tests/                      # Automated Pytest Test Suite (82 Tests, 0 Warnings)
│   ├── test_audit_regression.py# Audit regression tests (positivity, singular M, convergence)
│   ├── test_operators.py
│   ├── test_initial_states.py
│   ├── test_hamiltonian.py
│   ├── test_evolution.py
│   ├── test_reaction_kinetics.py
│   ├── test_decoherence.py
│   ├── test_qiskit_consistency.py
│   └── test_validation.py
│
├── results/                    # Saved Publication Figures & Numerical Artifacts
│   ├── angular_sweep.png
│   ├── contrast_vs_decoherence.png
│   ├── quantum_compass_poster_dark.pdf / .png / .svg
│   ├── quantum_compass_poster_print.pdf / .png / .svg
│   ├── experiment_1_angular_response.csv
│   └── experiment_results.json
│
├── docs/                       # Theoretical Documentation & Poster Artifacts
│   ├── figures/                # High-res poster graphics and vector files
│   ├── theoretical_model.md
│   ├── equations_and_units.md
│   ├── assumptions_and_limitations.md
│   ├── experimental_protocol.md
│   ├── poster_content.md
│   └── references.md
│
└── scripts/                    # Figure & Poster Generators
    ├── generate_user_plots.py  # Builds angular_sweep.png & contrast_vs_decoherence.png
    ├── generate_poster_figures.py
    └── build_research_poster.py# Builds 48x36" conference posters
```

---

## 🚀 Step-by-Step GitHub Upload & Poster QR Code Guide

Follow these steps to upload this project to GitHub and generate a QR code for your presentation poster:

### Step 1: Create a New GitHub Repository
1. Log in to [GitHub](https://github.com/).
2. Click the **+** icon in the top-right corner and select **New repository**.
3. Name your repository (e.g., `quantum-compass-lab` or `radical-pair-magnetoreception`).
4. Set visibility to **Public** (required for judges and poster viewers).
5. **Do NOT** initialize with a README, .gitignore, or license (these already exist in your local project).
6. Click **Create repository**.
7. Copy your repository URL (e.g., `https://github.com/<your-username>/quantum-compass-lab.git`).

### Step 2: Initialize Git and Push from Terminal
Open PowerShell or your terminal in this project folder (`Mangnetoreception`) and run:

```bash
# 1. Initialize git repository
git init

# 2. Stage all files (the provided .gitignore safely excludes .venv and cache)
git add .

# 3. Commit the verified research codebase
git commit -m "feat: complete Quantum Compass Lab research project for Qiskit Fall Fest 2026"

# 4. Set main branch
git branch -M main

# 5. Link to your GitHub repository (replace with your actual URL)
git remote add origin https://github.com/<your-username>/quantum-compass-lab.git

# 6. Push to GitHub
git push -u origin main
```

### Step 3: What to Upload (Sanity Checklist)
Your repository should include:
- `src/` (all simulation source code)
- `tests/` (all 82 pytest test files)
- `results/` (data CSVs, JSON results, and generated figures)
- `docs/` (theoretical documentation and poster layouts)
- `scripts/` (reproducible plotting and poster generators)
- `angular_sweep.png` and `contrast_vs_decoherence.png`
- `app.py` (Streamlit dashboard)
- `requirements.txt` and `pyproject.toml`
- `README.md` and `.gitignore`

*Do NOT commit:* `.venv/`, `__pycache__/`, `.pytest_cache/` (handled automatically by `.gitignore`).

### Step 4: Generate a QR Code for Your Poster
Once pushed, generate a high-resolution QR code linking to your repository:
1. Copy your public GitHub repository URL: `https://github.com/<your-username>/quantum-compass-lab`.
2. Generate a QR code using Python directly in your terminal:
   ```bash
   python -c "import urllib.request; url='https://github.com/<your-username>/quantum-compass-lab'; urllib.request.urlretrieve(f'https://api.qrserver.com/v1/create-qr-code/?size=1000x1000&data={url}', 'github_qr_code.png'); print('Saved github_qr_code.png')"
   ```
   *(Or use any free online vector QR code generator such as qr-code-generator.com or qr-monkey.com).*
3. Place `github_qr_code.png` in the bottom-right corner of your poster next to the **References & Open Science** section so poster attendees can scan it to view your live code and Streamlit dashboard!

---

## 🏃 Running the Project Locally

### 1. Run Automated Test Suite
```bash
pytest -v
```
*Expected: 82 passed in ~10 seconds with 0 warnings.*

### 2. Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

### 3. Regenerate Publication Figures
```bash
python scripts/generate_user_plots.py
```

### 4. Regenerate Full 48×36" Research Posters
```bash
python scripts/build_research_poster.py
```

---

## 📜 Citation
If you use this work for Qiskit Fall Fest 2026 or academic research, please cite:
```bibtex
@misc{quantum_compass_lab_2026,
  title={Quantum Compass Lab: Simulating Radical-Pair Magnetoreception Under Decoherence},
  author={Quantum Compass Lab Research Team},
  year={2026},
  publisher={Qiskit Fall Fest 2026}
}
```
