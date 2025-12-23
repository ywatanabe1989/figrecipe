<!-- ---
!-- Timestamp: 2025-12-22 13:01:11
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/README.md
!-- --- -->

<p align="center">
  <img src="docs/figrecipe_logo.png" alt="figrecipe logo" width="200"/>
</p>

# FigRecipe

**Reproducible matplotlib figures with mm-precision layouts.**
FigRecipe is a lightweight recording & reproduction layer for matplotlib,
designed for scientific figures that must remain **editable, inspectable,
and reproducible**.

Part of **SciTeX™ – Research OS for reproducible science**
https://scitex.ai

[![PyPI version](https://badge.fury.io/py/figrecipe.svg)](https://badge.fury.io/py/figrecipe)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

## Why FigRecipe?

In scientific workflows, figures are often:
- hard to reproduce once scripts change,
- resized manually in pixels or inches,
- impossible to partially reuse or inspect later.

**FigRecipe solves this by recording plotting calls as a structured “recipe”**,
allowing figures to be:
- faithfully reproduced,
- partially re-rendered,
- inspected for underlying data,
- laid out in **exact millimeters** for publication.

---

## Key Features

- ✅ Drop-in replacement for `matplotlib.pyplot`
- ✅ Automatic recording of plotting calls
- ✅ Reproduce figures from a YAML recipe
- ✅ Extract plotted data programmatically
- ✅ Selective reproduction of specific plots
- ✅ Millimeter-based layout (journal-ready)
- ✅ Publication-quality style presets
- ✅ Dark theme support (data colors preserved)
- ✅ Seamless seaborn integration
- ✅ Crop figures to content with mm margins

---

## Installation

```bash
pip install figrecipe

# Optional: for PDF export from notebooks (SVG → PDF)
sudo apt install inkscape  # Linux
brew install inkscape      # macOS

```

## Basic Usage

### Recording & Saving

``` python
import figrecipe as fr
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = fr.subplots()
ax.plot(x, y, color='red', linewidth=2, id='sine_wave')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')

# Save image + recipe
img_path, yaml_path, result = fr.save(fig, 'figure.png')
# → creates: figure.png + figure.yaml
```

### Reproducing a Figure

``` python
import figrecipe as fr

fig, ax = fr.reproduce('figure.yaml')
```

### Extracting Plotted Data

``` python
import figrecipe as fr

data = fr.extract_data('figure.yaml')
# {'sine_wave': {'x': array([...]), 'y': array([...])}}
```

### Millimeter-Based Layout (Publication-Ready)

``` python
fig, ax = fr.subplots(
    axes_width_mm=60,
    axes_height_mm=40,
    margin_left_mm=15,
    margin_bottom_mm=12,
)
```
This guarantees consistent sizing across editors, exports, and journals.

### Style Presets

``` python
fr.list_presets()
# ['MATPLOTLIB', 'SCITEX']

# Publication-quality preset (applied globally)
fr.load_style('SCITEX')
fig, ax = fr.subplots()

# Dark theme (UI-only, data colors preserved)
fr.load_style('SCITEX_DARK')
# or: fr.load_style('SCITEX', dark=True)

# Custom style
fr.load_style('/path/to/my_style.yaml')
```

See docs/EXAMPLE_RECIPE.yaml for a full style template.

### Recipe Format (YAML)

``` yaml
# Timestamp: "2025-12-22 11:53:14 (ywatanabe)"
# File: ./docs/EXAMPLE_RECIPE.yaml
# MATPLOTLIB Style Preset
# =======================
# Vanilla matplotlib defaults - minimal customization.
# Use this to reset to standard matplotlib behavior.

axes:
  width_mm: null   # Use matplotlib default (auto)
  height_mm: null  # Use matplotlib default (auto)
  thickness_mm: null  # Use matplotlib default

margins:
  left_mm: null
  right_mm: null
  bottom_mm: null
  top_mm: null

spacing:
  horizontal_mm: null
  vertical_mm: null

fonts:
  family: null  # matplotlib default (DejaVu Sans)
  axis_label_pt: null
  tick_label_pt: null
  title_pt: null
  suptitle_pt: null
  legend_pt: null
  annotation_pt: null

padding:
  label_pt: null
  tick_pt: null
  title_pt: null

lines:
  trace_mm: null
  errorbar_mm: null
  errorbar_cap_mm: null

ticks:
  length_mm: null
  thickness_mm: null
  direction: null
  n_ticks: null

markers:
  size_mm: null
  scatter_mm: null
  edge_width_mm: null

legend:
  frameon: null          # matplotlib default (True)
  bg: null               # matplotlib default
  edgecolor: null        # matplotlib default
  alpha: null            # matplotlib default
  loc: null              # matplotlib default

output:
  dpi: 300
  transparent: false
  format: "png"

behavior:
  auto_scale_axes: false
  hide_top_spine: false
  hide_right_spine: false
  grid: false

theme:
  mode: "light"
  dark:
    figure_bg: "#1e1e1e"
    axes_bg: "#1e1e1e"
    legend_bg: "#1e1e1e"
    text: "#d4d4d4"
    spine: "#3c3c3c"
    tick: "#d4d4d4"
    grid: "#3a3a3a"
  light:
    figure_bg: "white"
    axes_bg: "white"
    legend_bg: "white"
    text: "black"
    spine: "black"
    tick: "black"
    grid: "#cccccc"

# Standard matplotlib color cycle (tab10)
colors:
  palette:
    - [31, 119, 180]     # tab:blue
    - [255, 127, 14]     # tab:orange
    - [44, 160, 44]      # tab:green
    - [214, 39, 40]      # tab:red
    - [148, 103, 189]    # tab:purple
    - [140, 86, 75]      # tab:brown
    - [227, 119, 194]    # tab:pink
    - [127, 127, 127]    # tab:gray
    - [188, 189, 34]     # tab:olive
    - [23, 190, 207]     # tab:cyan

# EOF
```

The recipe is human-readable, version-controllable, and inspectable.


### API Overview

| Function                      | Description                       |
| ----------------------------- | --------------------------------- |
| `fr.subplots()`               | Create a recording-enabled figure |
| `fr.save(fig, 'fig.png')`     | Save image + recipe               |
| `fr.reproduce('fig.yaml')`    | Reproduce figure from recipe      |
| `fr.extract_data('fig.yaml')` | Extract plotted data              |
| `fr.info('fig.yaml')`         | Inspect recipe metadata           |
| `fr.load_style()`             | Load style preset (global)        |
| `fr.list_presets()`           | List available presets            |
| `fr.crop('fig.png')`          | Crop to content with mm margin    |


### Examples
- 📓 Interactive demo notebook:
  examples/figrecipe_demo.ipynb

- 🌐 View on nbviewer:
  https://nbviewer.org/github/ywatanabe1989/figrecipe/blob/main/examples/figrecipe_demo.ipynb

The notebook includes side-by-side comparisons of original and reproduced figures.

## Positioning

FigRecipe is intentionally minimal.
It focuses on recording, reproduction, and layout fidelity.

Higher-level workflows (figures, tables, statistics, GUIs) are handled in:

FTS (Figure-Table-Statics Bundle) in SciTeX ecosystem (https://scitex.ai/vis/)


## License

AGPL-3.0 See [LICENSE](LICENSE)
.

<!-- EOF -->
