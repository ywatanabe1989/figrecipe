<!-- ---
!-- Timestamp: 2026-02-07 08:17:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/README.md
!-- --- -->

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<h1 align="center">FigRecipe (<code>scitex-plt</code>)</h1>

<p align="center"><b>Reproducible scientific figures as first-class objects</b></p>

<p align="center">
  <a href="https://badge.fury.io/py/figrecipe"><img src="https://badge.fury.io/py/figrecipe.svg" alt="PyPI version"></a>
  <a href="https://figrecipe.readthedocs.io/"><img src="https://readthedocs.org/projects/figrecipe/badge/?version=latest" alt="Documentation"></a>
  <a href="https://github.com/ywatanabe1989/figrecipe/actions/workflows/test.yml"><img src="https://github.com/ywatanabe1989/figrecipe/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
</p>

FigRecipe is a framework for creating **reproducible, editable, and publication-ready** scientific figures. Part of [**SciTeX**](https://scitex.ai).

> **SciTeX users**: `pip install scitex[plt]` includes FigRecipe. `scitex.plt` delegates to `figrecipe` — they share the same API.

<p align="center">
  <img src="docs/figrecipe_concept.png" alt="FigRecipe: Reproducible Scientific Figures" width="100%"/>
</p>

## Quick Start

```bash
pip install figrecipe
```

## Three APIs

### Python API

```python
import figrecipe as fr
import numpy as np

fig, ax = fr.subplots()
ax.plot(np.sin(np.linspace(0, 10, 100)), id="sine")

fr.save(fig, "figure.png")  # → figure.png + figure.yaml + figure_data/
```

### CLI

```bash
figrecipe reproduce fig.yaml      # Recreate figure from recipe
figrecipe gui figure.png          # Launch visual editor
figrecipe validate fig.yaml       # Verify pixel-identical reproduction
figrecipe extract fig.yaml        # Extract plotted data as CSV
figrecipe compose a.yaml b.yaml   # Compose multi-panel figure
```

### MCP Server (for AI agents)

```bash
figrecipe mcp install             # Add to Claude Code config
```

AI agents can create, compose, and reproduce publication-ready figures autonomously via MCP tools.

## Documentation

- [Full Documentation](https://figrecipe.readthedocs.io/)
- [Plot Gallery](https://figrecipe.readthedocs.io/en/latest/gallery.html) — All 47 plot types
- [CLI Reference](https://figrecipe.readthedocs.io/en/latest/cli_reference.html)
- [MCP Specification](https://figrecipe.readthedocs.io/en/latest/mcp_spec.html)
- [Style Reference](https://figrecipe.readthedocs.io/en/latest/style_reference.html)

<details>
<summary><b>Core Features</b></summary>

- Drop-in replacement for `matplotlib.pyplot`
- Fully reproducible figure recipes (`.yaml`)
- Publication-ready millimeter layout
- Interactive GUI editor
- Dark / light themes
- Works with existing matplotlib code
</details>

<details>
<summary><b>Save / Load Formats</b></summary>

```python
fr.save(fig, "fig.png")     # fig.png + fig.yaml
fr.save(fig, "bundle/")     # directory bundle
fr.save(fig, "fig.zip")     # zip bundle

fr.load("fig.png")
fr.load("bundle/")
fr.load("fig.zip")
```

| Format | Save | Load |
|--------|:----:|:----:|
| PNG / PDF / SVG | ✓ | ✓ |
| YAML | ✓ | ✓ |
| Directory / ZIP | ✓ | ✓ |
</details>

<details>
<summary><b>Style Presets</b></summary>

```python
fr.list_presets()
fr.load_style("SCITEX")
fr.load_style("SCITEX_DARK")
```
</details>

<details>
<summary><b>Millimeter-based Layout</b></summary>

```python
fig, ax = fr.subplots(
    axes_width_mm=60,
    axes_height_mm=40,
    margin_left_mm=15,
)
```
</details>

<details>
<summary><b>Figure Captions</b></summary>

```python
fig.set_caption("Main figure description")
ax.set_caption("Panel A description")
```
</details>

<details>
<summary><b>Figure Composition</b></summary>

Combine multiple figures into publication-ready layouts:

```python
import figrecipe as fr

# Grid-based layout (auto-arranged)
fr.compose(
    sources=["panel_a.png", "panel_b.png", "panel_c.png"],
    output_path="figure.png",
    layout="horizontal",  # or "vertical", "grid"
    gap_mm=5.0,
)

# Free-form mm-based positioning (precise control)
fr.compose(
    canvas_size_mm=(180, 120),
    sources={
        "panel_a.yaml": {"xy_mm": (0, 0), "size_mm": (80, 50)},
        "panel_b.yaml": {"xy_mm": (90, 0), "size_mm": (80, 50)},
        "panel_c.yaml": {"xy_mm": (0, 60), "size_mm": (170, 50)},
    },
    output_path="figure.png",
)
```

**Key features:**
- Auto panel labels (A, B, C...)
- Saves `.compose.yaml` recipe for future re-composition
- Edit positions later with `fr.recompose()`
- All layouts internally use mm-based positioning
</details>

## Who Is This For?

FigRecipe is designed for researchers who:
- already use matplotlib or seaborn
- care about reproducibility and traceability
- want figures that survive revisions and collaboration
- are tired of re-writing plotting code

It is not meant to replace exploratory notebooks or quick plotting — it is meant to **formalize results**.

## Style Granularity

FigRecipe provides **millimeter-precise control** over every visual element with the SCITEX style preset:

<p align="center">
  <img src="docs/style_granularity.jpg" alt="SCITEX Style Anatomy" width="100%"/>
</p>

Includes **statistical annotation brackets** with significance stars (*, **, ***) for publication-ready comparisons.

## Plot Gallery

FigRecipe supports **47 matplotlib plot types** with publication-ready SCITEX styling.

<details>
<summary><b>Supported Plot Types</b></summary>

**Line & Curve**: plot, step, fill, fill_between, fill_betweenx, errorbar, stackplot, stairs

**Scatter & Points**: scatter

**Bar & Categorical**: bar, barh

**Distribution**: hist, hist2d, boxplot, violinplot, ecdf

**2D Image & Matrix**: imshow, matshow, pcolor, pcolormesh, hexbin, spy

**Contour & Surface**: contour, contourf, tricontour, tricontourf, tripcolor, triplot

**Spectral & Signal**: specgram, psd, csd, cohere, angle_spectrum, magnitude_spectrum, phase_spectrum, acorr, xcorr

**Vector & Flow**: quiver, barbs, streamplot

**Special**: pie, stem, eventplot, loglog, semilogx, semilogy, graph

</details>

## Schematic Diagrams

Create publication-quality box-and-arrow schematics with mm-based coordinates:

```python
s = fr.Schematic(title="EEG Analysis Pipeline", width_mm=350, height_mm=100)
s.add_box("raw", "Raw EEG", subtitle="64 ch", emphasis="muted")
s.add_box("filter", "Bandpass Filter", subtitle="0.5-45 Hz", emphasis="primary")
s.add_box("ica", "ICA", subtitle="Artifact removal", emphasis="primary")
s.add_arrow("raw", "filter")
s.add_arrow("filter", "ica")
s.auto_layout(layout="lr", gap_mm=15)

fig, ax = fr.subplots()
ax.schematic(s, id="pipeline")
fr.save(fig, "pipeline.png")
```

<p align="center">
  <img src="examples/09_schematic_out/schematic_lr.png" alt="Left-to-right schematic" width="100%"/>
</p>

<p align="center">
  <img src="examples/09_schematic_out/schematic_tb.png" alt="Top-to-bottom schematic" width="35%"/>
</p>

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
  <br>
  AGPL-3.0 · ywatanabe@scitex.ai
</p>

<!-- EOF -->
