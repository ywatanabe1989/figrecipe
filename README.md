<!-- ---
!-- Timestamp: 2026-01-01 01:44:36
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/README.md
!-- --- -->

# FigRecipe — **Reproducible matplotlib figures with mm-precision layouts.**

[![PyPI version](https://badge.fury.io/py/figrecipe.svg)](https://badge.fury.io/py/figrecipe)
[![Tests](https://github.com/ywatanabe1989/figrecipe/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/figrecipe/actions/workflows/test.yml)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

FigRecipe separates **what** is plotted from **how** it is styled, enabling reproducible figures with GUI editing. Part of [**SciTeX™**](https://scitex.ai).

<p align="center">
  <img src="docs/FigRecipe-demo.png" alt="FigRecipe GUI Editor" width="100%"/>
</p>

## Quick Start

```bash
pip install figrecipe
```

```python
import figrecipe as fr
import numpy as np

fig, ax = fr.subplots()
ax.plot(np.sin(np.linspace(0, 10, 100)), id='sine')
fr.save(fig, 'figure.png')  # → figure.png + figure.yaml

fig, ax = fr.load('figure.png')  # Reproduce from recipe
fr.edit(fig)  # Launch GUI editor
```

```bash
# CLI
figrecipe edit figure.png      # Launch GUI editor
figrecipe reproduce fig.yaml   # Reproduce figure
figrecipe extract fig.yaml     # Extract data
figrecipe info fig.yaml        # Show recipe info
```

<details>
<summary><b>Key Features</b></summary>

- ✅ Drop-in replacement for `matplotlib.pyplot`
- ✅ Familiar formats (PNG/SVG/PDF/YAML)
- ✅ Millimeter-based layout (journal-ready)
- ✅ Publication-quality style presets
- ✅ Dark theme support
- ✅ Interactive GUI editor
</details>

<details>
<summary><b>Installation Options</b></summary>

```bash
pip install figrecipe[seaborn]   # seaborn + pandas
pip install figrecipe[desktop]   # native window mode
pip install figrecipe[all]       # all extras

# PDF export from notebooks
sudo apt install inkscape  # Linux
brew install inkscape      # macOS
```
</details>

<details>
<summary><b>Save/Load Formats</b></summary>

```python
fr.save(fig, 'fig.png')       # → fig.png + fig.yaml
fr.save(fig, 'bundle/')       # → directory bundle
fr.save(fig, 'fig.zip')       # → ZIP bundle

fr.load('fig.png')            # finds fig.yaml
fr.load('bundle/')            # finds recipe.yaml
fr.load('fig.zip')            # extracts recipe
```

| Format | Save | Load |
|--------|:----:|:----:|
| `.png`/`.jpg`/`.pdf`/`.svg`/`.tif` | ✓ | ✓ |
| `.yaml`/`.yml` | ✓ | ✓ |
| Directory / `.zip` | ✓ | ✓ |
</details>

<details>
<summary><b>Style Presets</b></summary>

```python
fr.list_presets()           # ['MATPLOTLIB', 'SCITEX']
fr.load_style('SCITEX')     # Publication-quality
fr.load_style('SCITEX_DARK') # Dark theme
```
</details>

<details>
<summary><b>MM-Based Layout</b></summary>

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
<summary><b>API Reference</b></summary>

| Function | Description |
|----------|-------------|
| `fr.subplots()` | Create recording-enabled figure |
| `fr.save(fig, path)` | Save image + recipe |
| `fr.load(path)` | Reproduce from recipe |
| `fr.edit(fig)` | Launch GUI editor |
| `fr.load_style(name)` | Load style preset |
| `fr.extract_data(path)` | Extract plotted data |
| `fr.crop(path)` | Crop to content |
</details>

---

**License:** AGPL-3.0 | **Contact:** ywatanabe@scitex.ai

<p align="center">
  <a href="https://scitex.ai" target="_blank">
    <img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="60"/>
  </a>
</p>

<!-- EOF -->
