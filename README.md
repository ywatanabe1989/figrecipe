<!-- ---
!-- Timestamp: 2025-12-22 13:51:22
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
[![Tests](https://github.com/ywatanabe1989/figrecipe/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/figrecipe/actions/workflows/test.yml)
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

- ✅ Drop-in replacement for `matplotlib.pyplot` (use `figrecipe.pyplot` to enable recording)
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

## Examples

📓 **[View Demo Notebook on nbviewer](https://nbviewer.org/github/ywatanabe1989/figrecipe/blob/main/examples/figrecipe_demo.ipynb)** (recommended)

The notebook includes side-by-side comparisons of original and reproduced figures.

Source: [examples/figrecipe_demo.ipynb](examples/figrecipe_demo.ipynb)

## Installation

```bash
pip install figrecipe

# Optional extras
pip install figrecipe[seaborn]   # seaborn + pandas support
pip install figrecipe[imaging]   # image cropping (Pillow)
pip install figrecipe[all]       # all extras

# Optional: for PDF export from notebooks (SVG → PDF)
sudo apt install inkscape  # Linux
brew install inkscape      # macOS
```

**Requirements:** Python >= 3.9

## Basic Usage

### Recording & Saving

``` python
import figrecipe as fr
# import figrecipe.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = fr.subplots() # or plt.subplots()
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

See [src/figrecipe/styles/presets/](src/figrecipe/styles/presets/) for full examples.

### Style Format (YAML)

``` yaml
# Timestamp: "2025-12-22 12:40:36 (ywatanabe)"
# File: ./src/figrecipe/styles/presets/SCITEX.yaml
# FIGRECIPE Style Preset
# ======================
# Publication-quality settings for scientific figures.
# Optimized for scientific journals with Arial font.

axes:
  width_mm: 40
  height_mm: 28
  thickness_mm: 0.2

margins:
  left_mm: 1
  right_mm: 1
  bottom_mm: 1
  top_mm: 1

spacing:
  horizontal_mm: 8
  vertical_mm: 10

fonts:
  family: "Arial"
  axis_label_pt: 7
  tick_label_pt: 7
  title_pt: 8
  suptitle_pt: 8
  legend_pt: 6
  annotation_pt: 6

padding:
  label_pt: 2.0
  tick_pt: 2.0
  title_pt: 4.0

lines:
  trace_mm: 0.2
  errorbar_mm: 0.2
  errorbar_cap_mm: 0.8

ticks:
  length_mm: 0.8
  thickness_mm: 0.2
  direction: "out"
  n_ticks: 4

markers:
  size_mm: 0.8
  scatter_mm: 0.8
  edge_width_mm: null  # None = no border (cleaner than 0)

legend:
  frameon: false         # No frame for clean look
  bg: null               # Background (null = use theme.legend_bg)
  edgecolor: null        # Frame edge color
  alpha: 1.0             # Transparency
  loc: "best"

output:
  dpi: 300
  transparent: true
  format: "pdf"

behavior:
  auto_scale_axes: true
  hide_top_spine: true
  hide_right_spine: true
  grid: false

theme:
  mode: "light"
  dark:
    figure_bg: "transparent"
    axes_bg: "transparent"
    legend_bg: "transparent"
    text: "#d4d4d4"
    spine: "#d4d4d4"
    tick: "#d4d4d4"
    grid: "#3a3a3a"
  light:
    figure_bg: "transparent"
    axes_bg: "transparent"
    legend_bg: "transparent"
    text: "black"
    spine: "black"
    tick: "black"
    grid: "#cccccc"

# SciTeX Color Palette (RGB format)
colors:
  palette:
    - [0, 128, 192]      # blue
    - [255, 70, 50]      # red
    - [20, 180, 20]      # green
    - [230, 160, 20]     # yellow
    - [200, 50, 255]     # purple
    - [20, 200, 200]     # lightblue
    - [228, 94, 50]      # orange
    - [255, 150, 200]    # pink

  # Named colors
  white: [255, 255, 255]
  black: [0, 0, 0]
  blue: [0, 128, 192]
  red: [255, 70, 50]
  pink: [255, 150, 200]
  green: [20, 180, 20]
  yellow: [230, 160, 20]
  gray: [128, 128, 128]
  grey: [128, 128, 128]
  purple: [200, 50, 255]
  lightblue: [20, 200, 200]
  brown: [128, 0, 0]
  navy: [0, 0, 100]
  orange: [228, 94, 50]

  # Semantic
  primary: [0, 128, 192]
  secondary: [255, 70, 50]
  accent: [20, 180, 20]

# EOF
```


### API Overview

| Import                           | Description                                       |
|----------------------------------|---------------------------------------------------|
| `import figrecipe.pyplot as plt` | Drop-in replacement of `matplotlib.pyplot as plt` |
| `import figrecipe as fr`         | Import figrecipe package                          |
|----------------------------------|---------------------------------------------------|
| Function                         |                                                   |
|----------------------------------|---------------------------------------------------|
| `fr.subplots()`                  | Create a recording-enabled figure                 |
| `fr.save(fig, 'fig.png')`        | Save image + recipe                               |
| `fr.reproduce('fig.yaml')`       | Reproduce figure from recipe                      |
| `fr.extract_data('fig.yaml')`    | Extract plotted data                              |
| `fr.info('fig.yaml')`            | Inspect recipe metadata                           |
| `fr.load_style()`                | Load style preset (global)                        |
| `fr.list_presets()`              | List available presets                            |
| `fr.crop('fig.png')`             | Crop to content with mm margin                    |

## Positioning

FigRecipe focuses on *how* figures are constructed, not *what* they represent.

FigRecipe is intentionally minimal, focusing on recording, reproduction, and layout fidelity.

Higher-level workflows (figures–tables–statistics bundle, GUI editor, and integration with manuscript Writing) are handled in:

FTS (Figure-Table-Statistics Bundle) in SciTeX Ecosystem:
https://github.com/ywatanabe1989/scitex-code
https://scitex.ai/vis/
https://scitex.ai/writer/


## License

AGPL-3.0 See [LICENSE](LICENSE)
.

<!-- EOF -->