# Scientific Poster Presentation: Angular Response Figure

## Radical-Pair Singlet Reaction Yield vs Geomagnetic Field Orientation

This document provides the high-resolution, publication-ready poster figures for the directional compass response experiment ($B_0 = 50\ \mu\mathrm{T}$, $\mathbf{A} = \mathrm{diag}(5, 5, 20)\ \mathrm{rad}/\mu\mathrm{s}$, $k_S = k_T = 1.0\ \mu\mathrm{s}^{-1}$).

All plots are generated directly from the simulation data in [results/experiment_1_angular_response.csv](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/experiment_1_angular_response.csv).

---

### Poster-Ready Dark Theme (Digital Poster & Presentation)

![Figure 1: Singlet reaction yield Phi_S vs field polar angle theta at B = 50 uT, showing 13.32% contrast](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/poster_figure_angular_sweep.png)

### Vector and High-Resolution Artifact Files

| Format | Resolution / Type | Path (Docs) | Path (Results) |
|---|---|---|---|
| **PNG (Dark)** | 300 DPI Raster | [docs/figures/poster_figure_angular_sweep.png](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/poster_figure_angular_sweep.png) | [results/poster_figure_angular_sweep.png](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/poster_figure_angular_sweep.png) |
| **SVG (Dark)** | Scalable Vector | [docs/figures/poster_figure_angular_sweep.svg](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/poster_figure_angular_sweep.svg) | [results/poster_figure_angular_sweep.svg](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/poster_figure_angular_sweep.svg) |
| **PDF (Dark)** | Print Vector | [docs/figures/poster_figure_angular_sweep.pdf](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/poster_figure_angular_sweep.pdf) | [results/poster_figure_angular_sweep.pdf](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/poster_figure_angular_sweep.pdf) |
| **PNG (Print/White)** | 300 DPI Raster | [docs/figures/poster_figure_angular_sweep_print.png](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/poster_figure_angular_sweep_print.png) | [results/poster_figure_angular_sweep_print.png](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/poster_figure_angular_sweep_print.png) |
| **SVG (Print/White)** | Scalable Vector | [docs/figures/poster_figure_angular_sweep_print.svg](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/poster_figure_angular_sweep_print.svg) | [results/poster_figure_angular_sweep_print.svg](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/poster_figure_angular_sweep_print.svg) |
| **PDF (Print/White)** | Print Vector | [docs/figures/poster_figure_angular_sweep_print.pdf](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/docs/figures/poster_figure_angular_sweep_print.pdf) | [results/poster_figure_angular_sweep_print.pdf](file:///c:/Users/Nikitha/OneDrive/Desktop/Mangnetoreception/results/poster_figure_angular_sweep_print.pdf) |

---

### Exact Numerical Values & Scientific Interpretation

The curve reflects the non-equilibrium spin dynamics governed by the Haberkorn master equation:

$$\frac{d\rho}{dt} = -i[H(\theta), \rho] - \frac{k_S}{2}\{P_S, \rho\} - \frac{k_T}{2}\{P_T, \rho\}$$

- **Maximum Yield $\Phi_{S,\mathrm{max}}$:** $0.487214$ at $\theta = 0.0^\circ$ (field parallel to the hyperfine symmetry axis $\hat{z}$).
- **Minimum Yield $\Phi_{S,\mathrm{min}}$:** $0.372643$ at $\theta = 32.0^\circ$.
- **Absolute Anisotropy $\Delta\Phi_S$:** $\Phi_{S,\mathrm{max}} - \Phi_{S,\mathrm{min}} = 0.114571$.
- **Relative Directional Contrast $C$:** $\frac{\Phi_{S,\mathrm{max}} - \Phi_{S,\mathrm{min}}}{\Phi_{S,\mathrm{max}} + \Phi_{S,\mathrm{min}}} = 13.3244\%$.
- **Yield Conservation:** $\Phi_S(\theta) + \Phi_T(\theta) = 1.0000000000$ across all 91 sampled angles in $[0^\circ, 180^\circ]$.
- **Physical Significance:** Breaking spherical symmetry through the anisotropic hyperfine coupling tensor ($A_{zz} / A_{xx} = 4$) enables the geomagnetic field ($50\ \mu\mathrm{T}$) to selectively mix singlet and triplet manifolds, altering macroscopic chemical yields by $13.32\%$.
