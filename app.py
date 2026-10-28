"""
QUANTUM COMPASS LAB
Simulating Radical-Pair Magnetoreception Under Decoherence
Interactive Research Dashboard for Qiskit Fall Fest 2026
"""

from __future__ import annotations
import io
import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.spin_model import SpinModelConfig, GAMMA_E_RAD_PER_US_PER_UT
from src.initial_states import get_initial_density_matrix, get_pure_singlet_nuclear_states
from src.hamiltonian import (
    build_zeeman_hamiltonian,
    build_hyperfine_hamiltonian,
    build_total_hamiltonian,
)
from src.reaction_kinetics import calculate_yields_exact
from src.evolution import simulate_time_trajectory, integrate_yield_numerically, evolve_unitary
from src.experiment_runner import (
    run_angular_sweep,
    AngularSweepResult,
    run_experiment_1_angular_response,
    run_experiment_2_decoherence,
    run_experiment_3_hyperfine_sensitivity,
    run_experiment_5_convergence,
)
from src.metrics import calculate_compass_metrics, CompassMetrics
from src.plotting import (
    plot_angular_response,
    plot_decoherence_comparison,
    plot_contrast_decay,
    plot_time_dynamics,
    STYLE_CONFIG,
    apply_research_theme
)
from src.qiskit_backend import (
    create_singlet_prep_circuit,
    create_trotter_evolution_circuit,
    build_qiskit_hamiltonian,
    simulate_qiskit_evolution,
    build_singlet_projector_operator,
)
from src.validation import ValidationSuite
from src.exports import (
    export_config_json,
    generate_experiment_report_md,
    get_model_equations_markdown,
)

# ---------------------------------------------------------
# Page Configuration & High-End Laboratory Theme Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Quantum Compass Lab",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Dark Navy & Obsidian Research Palette */
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    /* Headers & Accent Colors */
    h1, h2, h3, h4 {
        color: #F8FAFC;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Research Card Containers */
    .lab-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.25);
    }
    
    .badge-cyan {
        display: inline-block;
        background-color: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 8px;
    }
    
    .badge-violet {
        display: inline-block;
        background-color: rgba(167, 139, 250, 0.15);
        color: #A78BFA;
        border: 1px solid rgba(167, 139, 250, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Primary Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
        color: white;
        border: 1px solid #38BDF8;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369A1 0%, #075985 100%);
        border-color: #7DD3FC;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar Navigation & Parameter Defaults
# ---------------------------------------------------------
st.sidebar.markdown("""
<div style="padding: 10px 0 20px 0;">
    <span class="badge-cyan">Qiskit Fall Fest 2026</span>
    <span class="badge-violet">Quantum Biology</span>
    <h2 style="margin-top: 10px; font-size: 1.4rem; color: #F8FAFC;">QUANTUM COMPASS LAB</h2>
    <p style="font-size: 0.8rem; color: #94A3B8;">Radical-Pair Magnetoreception Simulator</p>
</div>
""", unsafe_allow_html=True)

nav_page = st.sidebar.radio(
    "Navigation",
    [
        "1. Research Overview",
        "2. Spin Model Architecture",
        "3. Live Angular Experiment",
        "4. Decoherence Lab",
        "5. Quantum Circuit (Qiskit)",
        "6. Validation & Test Suite",
        "7. Export & Reproducibility",
    ],
    index=2  # Default to Live Angular Experiment
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Global Parameters")
global_b = st.sidebar.slider("Earth Field Magnitude B (uT)", min_value=10.0, max_value=100.0, value=50.0, step=1.0)
global_dephasing = st.sidebar.slider("Decoherence Rate gamma (us^-1)", min_value=0.0, max_value=20.0, value=0.0, step=0.1)
global_deph_model = st.sidebar.selectbox(
    "Decoherence Model",
    ["isotropic_depolarizing", "pure_dephasing"],
    format_func=lambda m: "Isotropic Depolarizing (T1=T2)" if "iso" in m else "Pure Dephasing (T1=inf, T2=1/gamma)"
)

if global_dephasing > 1e-6:
    st.sidebar.caption(f"Transverse Coherence Time T2: **{1.0 / global_dephasing:.2f} us**")
else:
    st.sidebar.caption("Transverse Coherence Time T2: **Infinite (Coherent Limit)**")


# =========================================================
# PAGE 1: RESEARCH OVERVIEW
# =========================================================
if nav_page == "1. Research Overview":
    st.title("🧭 Quantum Compass Lab: Research Overview")
    st.markdown("#### Simulating Radical-Pair Magnetoreception Under Decoherence")

    st.markdown("""
    <div class="lab-card">
        <h3 style="color: #38BDF8;">Central Research Question</h3>
        <p style="font-size: 1.05rem; line-height: 1.6; color: #E2E8F0;">
            How do geomagnetic field orientation, anisotropic hyperfine interactions, reaction kinetics, and environmental decoherence 
            affect the directional sensitivity and reaction yields of a simplified avian radical-pair compass?
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="lab-card">
            <h4 style="color: #A78BFA;">The Radical-Pair Mechanism in Cryptochrome</h4>
            <ol style="color: #CBD5E1; line-height: 1.7;">
                <li><strong>Photo-excitation:</strong> Blue light absorbs into flavin adenine dinucleotide (FAD) within cryptochrome in the avian retina.</li>
                <li><strong>Electron Transfer:</strong> An electron cascades along a chain of tryptophan residues (TrpH), generating a spin-correlated radical pair:
                    <code>[FAD•- ... TrpH•+]</code>.</li>
                <li><strong>Entangled Initial State:</strong> Born from a closed-shell precursor, the radical pair starts in a spin-singlet state (|S⟩).</li>
                <li><strong>Magnetic Interconversion:</strong> Weak Earth's magnetic fields (~25–65 µT) compete with nuclear hyperfine couplings to steer coherent Singlet ⇄ Triplet oscillations.</li>
                <li><strong>Spin-Selective Recombination:</strong> Singlet states recombine to ground state; triplet states form signaling products detected by retinal ganglion cells.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="lab-card">
            <h4 style="color: #38BDF8;">Spin System Representation & Qubit Encoding</h4>
            <ul style="color: #CBD5E1; line-height: 1.7;">
                <li><strong>Qubit 0:</strong> Electron spin $S_1$ (on FAD$^{\bullet-}$), spin-1/2 ($d=2$).</li>
                <li><strong>Qubit 1:</strong> Electron spin $S_2$ (on TrpH$^{\bullet+}$), spin-1/2 ($d=2$).</li>
                <li><strong>Qubit 2:</strong> Nuclear spin $I$ (coupled to $S_1$, e.g., $^{14}$N or $^{1}$H), spin-1/2 ($d=2$).</li>
                <li><strong>Hilbert Space Dimension:</strong> Explicitly $2^3 = 8$ dimensions.</li>
                <li><strong>Nuclear Initialization:</strong> Under physiological temperature ($T \approx 310$ K), the nuclear ensemble is unpolarized, described by the maximally mixed state $\rho_N = \mathbb{I}/2$.</li>
                <li><strong>Direct Ensemble Simulation:</strong> Implemented via complementary basis preparations $|S\rangle \otimes |0\rangle$ and $|S\rangle \otimes |1\rangle$.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="lab-card">
        <h4 style="color: #F8FAFC;">Scientific Scope & Methodological Honesty</h4>
        <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.6;">
            <strong>Important Scientific Clarification:</strong> This project models a simplified, 3-spin mathematical representation of the radical-pair mechanism.
            We explicitly acknowledge that actual cryptochromes contain dozens of nuclear spins, complex protein conformational motions, and complex cellular environments.
            We do not claim that our 3-qubit simulation proves how migratory birds navigate, but rather rigorously demonstrate and validate the underlying quantum mechanics,
            rotational symmetry breaking, and decoherence vulnerability in a fully verifiable, reproducible simulation suite.
        </p>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# PAGE 2: SPIN MODEL ARCHITECTURE
# =========================================================
elif nav_page == "2. Spin Model Architecture":
    st.title("⚛️ Spin Model Architecture & Hamiltonian")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Interactive Model Configuration")
        b_mag = st.number_input("Field Magnitude B (uT)", value=float(global_b), step=5.0)
        th_val = st.slider("Field Polar Angle theta (rad)", 0.0, float(np.pi), 0.785, step=0.05)
        phi_val = st.slider("Field Azimuthal Angle phi (rad)", 0.0, float(2*np.pi), 0.0, step=0.05)

        st.markdown("#### Hyperfine Coupling Tensor A (rad/us)")
        c_a1, c_a2, c_a3 = st.columns(3)
        with c_a1:
            a_xx = st.number_input("A_xx", value=5.0, step=1.0)
        with c_a2:
            a_yy = st.number_input("A_yy", value=5.0, step=1.0)
        with c_a3:
            a_zz = st.number_input("A_zz", value=20.0, step=1.0)

        st.markdown("#### Reaction Rates (1/us)")
        c_k1, c_k2 = st.columns(2)
        with c_k1:
            k_s = st.number_input("k_S (Singlet Sink)", value=1.0, step=0.2)
        with c_k2:
            k_t = st.number_input("k_T (Triplet Sink)", value=1.0, step=0.2)

        cfg_user = SpinModelConfig(
            B_magnitude=b_mag,
            theta=th_val,
            phi=phi_val,
            A_xx=a_xx,
            A_yy=a_yy,
            A_zz=a_zz,
            k_S=k_s,
            k_T=k_t,
            gamma_dephasing=global_dephasing,
            dephasing_model=global_deph_model
        )

    with col2:
        st.markdown("### Hamiltonian Matrix & Parameters")
        H_total = build_total_hamiltonian(cfg_user)
        H_zeeman = build_zeeman_hamiltonian(cfg_user)
        H_hf = build_hyperfine_hamiltonian(cfg_user)

        st.markdown(f"""
        - **Electron Zeeman Frequency $\\omega_0$:** `{cfg_user.zeeman_omega:.4f}` rad/$\\mu$s ($`{cfg_user.zeeman_omega / (2*np.pi):.4f}` MHz)
        - **Field Unit Vector $\\mathbf{{b}}$:** `[{cfg_user.field_unit_vector[0]:.3f}, {cfg_user.field_unit_vector[1]:.3f}, {cfg_user.field_unit_vector[2]:.3f}]`
        - **Tensor Symmetry:** `{'Isotropic (Spherical)' if cfg_user.is_isotropic_hyperfine else 'Anisotropic (Axial)'}`
        - **Hilbert Space Dimension:** `8 x 8` complex Hermitian matrix
        """)

        st.markdown("#### Total Hamiltonian Eigenvalues (rad/us)")
        eigs = np.sort(np.linalg.eigvalsh(H_total))
        df_eigs = pd.DataFrame({"Level": [f"E_{i}" for i in range(8)], "Energy (rad/us)": eigs})
        st.dataframe(df_eigs.T, use_container_width=True)

        st.markdown(get_model_equations_markdown())


# =========================================================
# PAGE 3: LIVE ANGULAR EXPERIMENT
# =========================================================
elif nav_page == "3. Live Angular Experiment":
    st.title("🧭 Live Angular Experiment: Compass Response")
    st.markdown("Execute real-time field orientation sweeps and compute exact directional reaction yields.")

    col_ctrl, col_display = st.columns([1, 2])

    with col_ctrl:
        st.markdown("### Sweep Parameters")
        b_exp = st.slider("Field Magnitude B (uT)", 20.0, 70.0, float(global_b), step=5.0)
        n_angles = st.slider("Angular Resolution (Points)", 19, 91, 45, step=4)
        
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            a_perp = st.number_input("A_xx = A_yy (rad/us)", value=5.0, step=1.0)
        with c_a2:
            a_par = st.number_input("A_zz (rad/us)", value=20.0, step=2.0)

        deph_exp = st.slider("Decoherence gamma (us^-1)", 0.0, 15.0, float(global_dephasing), step=0.5)

        run_sweep_btn = st.button("🚀 Run Angular Sweep", use_container_width=True)
        single_sim_btn = st.button("⏱️ Run Time Trajectory", use_container_width=True)

    with col_display:
        cfg_exp = SpinModelConfig(
            B_magnitude=b_exp,
            A_xx=a_perp,
            A_yy=a_perp,
            A_zz=a_par,
            k_S=1.0,
            k_T=1.0,
            gamma_dephasing=deph_exp,
            dephasing_model=global_deph_model
        )

        with st.spinner("Computing radical-pair spin dynamics..."):
            res = run_angular_sweep(cfg_exp, num_angles=n_angles)

        m = res.metrics
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1:
            st.metric("Contrast C", f"{m.contrast * 100:.2f}%")
        with c_m2:
            st.metric("Yield Span ΔΦ_S", f"{m.absolute_anisotropy:.4f}")
        with c_m3:
            st.metric("Min Yield (θ)", f"{m.phi_s_min:.4f} ({m.theta_min_deg:.0f}°)")
        with c_m4:
            st.metric("Max Yield (θ)", f"{m.phi_s_max:.4f} ({m.theta_max_deg:.0f}°)")

        # Render Figure
        fig_ang = plot_angular_response(
            np.array(res.thetas_deg),
            np.array(res.singlet_yields),
            res.metrics,
            title=f"Radical-Pair Singlet Yield vs Field Polar Angle (B = {b_exp:.0f} uT)",
            field_label=f"B = {b_exp:.0f} uT, gamma = {deph_exp:.1f} us^-1"
        )
        st.pyplot(fig_ang)
        plt.close(fig_ang)

        if single_sim_btn:
            st.markdown("### Time-Domain Radical Pair Dynamics")
            times, p_s, surviving = simulate_time_trajectory(
                get_initial_density_matrix(),
                cfg_exp,
                t_span=(0.0, 5.0),
                num_points=300
            )
            fig_time = plot_time_dynamics(times, p_s, surviving)
            st.pyplot(fig_time)
            plt.close(fig_time)


# =========================================================
# PAGE 4: DECOHERENCE LAB
# =========================================================
elif nav_page == "4. Decoherence Lab":
    st.title("🔬 Decoherence Lab: Spin Coherence & Contrast")
    st.markdown("Analyze how spin relaxation ($T_1$) and dephasing ($T_2$) affect compass directional sensitivity.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Progressive Decoherence Comparison")
        decoh_levels = [0.0, 0.5, 2.0, 5.0, 15.0]
        labels = ["Ideal (T2 = inf)", "T2 = 2.0 us", "T2 = 0.5 us", "T2 = 0.2 us", "T2 = 0.07 us"]
        yields_dict = {}

        thetas_deg = None
        for g, lbl in zip(decoh_levels, labels):
            cfg = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0, gamma_dephasing=g, dephasing_model=global_deph_model)
            res = run_angular_sweep(cfg, num_angles=37)
            thetas_deg = np.array(res.thetas_deg)
            yields_dict[lbl] = np.array(res.singlet_yields)

        fig_decoh = plot_decoherence_comparison(
            thetas_deg,
            yields_dict,
            title=f"Angular Response Under {global_deph_model.capitalize()} Decoherence"
        )
        st.pyplot(fig_decoh)
        plt.close(fig_decoh)

    with col2:
        st.markdown("### Compass Contrast vs. Coherence Time T2")
        t2_vals = np.logspace(-1.0, 1.2, 20)
        contrasts = []
        for t2 in t2_vals:
            g = 1.0 / t2
            cfg = SpinModelConfig(B_magnitude=50.0, A_xx=5.0, A_yy=5.0, A_zz=20.0, gamma_dephasing=g, dephasing_model=global_deph_model)
            res = run_angular_sweep(cfg, num_angles=25)
            contrasts.append(res.metrics.contrast)

        fig_t2 = plot_contrast_decay(t2_vals, np.array(contrasts))
        st.pyplot(fig_t2)
        plt.close(fig_t2)

    st.markdown("""
    <div class="lab-card">
        <h4 style="color: #38BDF8;">Calibrated Noise Models & Computational Detectability</h4>
        <ul style="color: #CBD5E1; line-height: 1.6;">
            <li><strong>Isotropic Depolarizing Noise (T1 = T2 = 1/gamma):</strong> 
                Models isotropic 3D magnetic fluctuations ($\sigma_x, \sigma_y, \sigma_z$ channels). Transverse coherence decays strictly as $\exp(-\gamma t)$. 
                As $T_2$ drops below ~1 µs, singlet-triplet quantum interference is suppressed, causing directional contrast to decay monotonically to 0.00%.</li>
            <li><strong>Pure Phase Damping (T1 -> inf, T2 = 1/gamma):</strong> 
                Models longitudinal dephasing along the molecular z-axis ($\sigma_z$ channel), strictly preserving populations. Because noise commutes with $S_z$, 
                moderate axial noise differentially damps transverse oscillations, altering the angular profile before eventual suppression at very high rates.</li>
            <li><strong>Model-Dependent Computational Thresholds:</strong>
                <ul>
                    <li>Absolute Yield Anisotropy threshold ($\Delta\Phi_S \ge 0.001 = 0.1\%$): <strong>$T_2 \ge 0.15\ \mu$s</strong>.</li>
                    <li>Normalized Compass Contrast threshold ($C \ge 0.01 = 1.0\%$): <strong>$T_2 \ge 0.36\ \mu$s</strong>.</li>
                </ul>
            </li>
            <li><strong>Important Scientific Disclaimer:</strong> These are <em>model-dependent engineering and analysis thresholds</em> within our simplified 3-qubit model, 
                <strong>not</strong> a claimed discovery of the physiological threshold in real living birds.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# PAGE 5: QUANTUM CIRCUIT (QISKIT)
# =========================================================
elif nav_page == "5. Quantum Circuit (Qiskit)":
    st.title("⚡ Qiskit Quantum Circuit Architecture")
    st.markdown("Direct 3-qubit mapping, Lie-Trotter Hamiltonian synthesis, and Statevector simulation.")

    cfg_circ = SpinModelConfig(B_magnitude=global_b, theta=0.8, phi=0.0, A_xx=5.0, A_yy=5.0, A_zz=20.0)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Qiskit Subsystem Mapping")
        st.markdown("""
        | Qubit Index | Subsystem | Physical Role | Initialization |
        |:---:|:---:|:---:|:---:|
        | **q0** | Electron 1 ($S_1$) | FAD$^{\bullet-}$ radical | Entangled Singlet $\|S\\rangle$ |
        | **q1** | Electron 2 ($S_2$) | TrpH$^{\bullet+}$ radical | Entangled Singlet $\|S\\rangle$ |
        | **q2** | Nuclear Spin ($I$) | Nitrogen/Proton | Unpolarized Ensemble ($\\|0\\rangle, \\|1\\rangle$) |
        """)

        st.markdown("#### Singlet State Preparation Circuit")
        st.code("""# Qiskit Bell Singlet Preparation: |S> = (|01> - |10>)/sqrt(2)
qc.x(1)
qc.h(0)
qc.z(0)
qc.cx(0, 1)""", language="python")

        qc_prep = create_singlet_prep_circuit(nuclear_state=0)
        fig_prep, ax_prep = plt.subplots(figsize=(6, 2.5), dpi=150)
        apply_research_theme(fig_prep, ax_prep)
        ax_prep.axis('off')
        ax_prep.text(0.1, 0.5, qc_prep.draw(output='text'), family='monospace', fontsize=10, color="#38BDF8")
        st.pyplot(fig_prep)
        plt.close(fig_prep)

    with col2:
        st.markdown("### Hamiltonian Trotter Decomposition")
        n_steps = st.slider("Lie-Trotter Repetitions", min_value=1, max_value=25, value=5)
        t_circ = st.slider("Evolution Time t (us)", min_value=0.1, max_value=3.0, value=0.5, step=0.1)

        qc_trotter = create_trotter_evolution_circuit(cfg_circ, time=t_circ, num_steps=n_steps)
        decomposed = qc_trotter.decompose()

        st.metric("Decomposed Gate Depth", decomposed.depth())
        st.metric("Total 2-Qubit CX/RZZ Gates", decomposed.count_ops().get("cx", 0) + decomposed.count_ops().get("rzz", 0))

        st.markdown("#### Hardware Execution & Transpilation Realities")
        st.markdown("""
        - **NISQ Limitations:** On physical superconducting hardware (e.g. IBM Quantum Eagle/Heron), each Trotter step introduces CNOT error rates (~0.5–1%).
        - **Depth Scaling:** Simulating evolution over long biological lifetimes ($t \\sim 1\\ \\mu$s) requires multiple Trotter steps, accumulating two-qubit gate errors that wash out the signal.
        - **Status:** Our software is hardware-ready for transpilation to IBM backends (`ibm_sherbrooke`, `ibm_brisbane`) when authorized.
        """)


# =========================================================
# PAGE 6: VALIDATION & TEST SUITE
# =========================================================
elif nav_page == "6. Validation & Test Suite":
    st.title("✅ Scientific Validation & Automated Audit")
    st.markdown("Automated verification of physical principles, mathematical consistency, and Qiskit numerical agreement.")

    if st.button("🔄 Re-Run Full Validation Suite"):
        st.session_state.val_suite = ValidationSuite().run_all()

    if "val_suite" not in st.session_state:
        st.session_state.val_suite = ValidationSuite().run_all()

    results = st.session_state.val_suite
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Validation Pass Rate", f"{(passed_count / total_count) * 100:.1f}%")
    with col2:
        st.metric("Tests Passed", f"{passed_count} / {total_count}")
    with col3:
        st.metric("Status", "ALL SYSTEMS VERIFIED" if passed_count == total_count else "ATTENTION REQUIRED")

    val_data = []
    for r in results:
        val_data.append({
            "Test Name": r.name,
            "Status": "PASS ✅" if r.passed else "FAIL ❌",
            "Description": r.description,
            "Numerical Discrepancy": f"{r.numerical_metric:.2e}",
            "Tolerance": f"{r.tolerance:.2e}",
            "Details": r.details,
        })
    df_val = pd.DataFrame(val_data)
    st.dataframe(df_val, use_container_width=True)


# =========================================================
# PAGE 7: EXPORT & REPRODUCIBILITY
# =========================================================
elif nav_page == "7. Export & Reproducibility":
    st.title("📦 Export & Reproducibility Suite")
    st.markdown("Export simulation data, JSON configuration files, and complete experiment reports.")

    cfg_export = SpinModelConfig(
        B_magnitude=global_b,
        A_xx=5.0,
        A_yy=5.0,
        A_zz=20.0,
        gamma_dephasing=global_dephasing,
        dephasing_model=global_deph_model
    )
    res_export = run_angular_sweep(cfg_export, num_angles=73)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Export Data Tables")
        df_csv = res_export.to_dataframe()
        csv_buffer = df_csv.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Angular Sweep CSV",
            data=csv_buffer,
            file_name="quantum_compass_angular_sweep.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("### Export Experiment Configuration")
        cfg_dict = {
            "B_magnitude_uT": cfg_export.B_magnitude,
            "A_xx": cfg_export.A_xx,
            "A_yy": cfg_export.A_yy,
            "A_zz": cfg_export.A_zz,
            "gamma_dephasing": cfg_export.gamma_dephasing,
            "dephasing_model": cfg_export.dephasing_model,
            "coherence_time_T2_us": cfg_export.coherence_time_T2,
        }
        json_buffer = json.dumps(cfg_dict, indent=2).encode('utf-8')
        st.download_button(
            label="📥 Download JSON Configuration",
            data=json_buffer,
            file_name="experiment_config.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        st.markdown("### Export Full Markdown Report")
        report_md = generate_experiment_report_md(res_export)
        st.download_button(
            label="📥 Download Experiment Report (Markdown)",
            data=report_md.encode('utf-8'),
            file_name="quantum_compass_experiment_report.md",
            mime="text/markdown",
            use_container_width=True
        )

        st.markdown("### Report Preview")
        st.text_area("Preview", report_md, height=220)
