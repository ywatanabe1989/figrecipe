---
description: Publication-ready matplotlib figures with mm-precision layouts, YAML recipes, declarative specs, multi-panel composition, whitespace cropping, style presets (SCITEX, MATPLOTLIB), and box-and-arrow diagrams. Supports 70+ plot types — every matplotlib kind (line/scatter/bar/hist/box/violin/heatmap/imshow/errorbar/contour/quiver/streamplot/hexbin/stackplot/loglog/ecdf/…) plus scitex-specialized ones (`fr_mean_ci`, `fr_mean_std`, `fr_median_iqr`, `fr_shaded_line`, `fr_conf_mat`, `fr_raster`, `fr_violin`, `fr_scatter_hist`, `fr_heatmap` and `stx_*` aliases). Drop-in replacement for raw `matplotlib.pyplot` (`plt.subplots`, `fig.savefig`, `ax.plot/scatter/bar/hist/boxplot/violinplot/heatmap/imshow/errorbar`), `seaborn` (`fr.sns` re-export), manual `subplot2grid` / `GridSpec` layouts, hand-rolled subplot labeling (A, B, C), and `mermaid-cli` / `graphviz` for diagrams. Use whenever the user asks to "make a figure", "plot this data", "save a figure", "create a subplot", "lay out panels at exact mm sizes", "compose panels A/B/C into one figure", "add panel labels", "crop whitespace", "reproduce a figure later", "save a figure recipe", "plot mean ± CI / std / IQR", "confusion matrix plot", "raster plot", "shaded line plot", "apply SCITEX style", or "draw a box-and-arrow diagram / flowchart / Mermaid / Graphviz diagram". Every saved figure ships a YAML recipe so the same plot can be regenerated bit-for-bit months later.
allowed-tools: mcp__scitex__plt_*
primary_interface: python
---

# figrecipe

> **Primary interface: Python API.** Import in scripts/notebooks — CLI & MCP are thin wrappers over the Python functions.

## Installation & import

`pip install figrecipe` installs the standalone:

```python
import figrecipe
```

This package does not ship as a submodule of the `scitex` umbrella.

## Sub-skills

### Core
* [01_quick-start](01_quick-start.md) — Core workflow: subplots, save, reproduce
* [02_plot-types](02_plot-types.md) — All supported plot types with examples
* [03_composition](03_composition.md) — Multi-panel figure composition (grid and mm-based)
* [04_cropping](04_cropping.md) — Figure cropping, whitespace removal
* [05_styles](05_styles.md) — Style presets, SCITEX/MATPLOTLIB, custom styles
* [06_bundle](06_bundle.md) — ZIP bundle format (spec.json + data.csv + exports)
* [07_diagram](07_diagram.md) — Box-and-arrow diagrams, Mermaid, Graphviz

### Workflows
* [10_workflows](10_workflows.md) — Common figure workflows
* [11_cli-reference](11_cli-reference.md) — All CLI commands
* [12_mcp-tools](12_mcp-tools.md) — MCP tool reference for AI agents

### Standards
* [20_return-fig](20_return-fig.md) — Convention: plotting functions must return fig

## MCP Tools

| Tool | Purpose |
|------|---------|
| `plt_plot` | Create figure from declarative spec dict |
| `plt_reproduce` | Reproduce figure from YAML recipe |
| `plt_compose` | Compose multi-panel figure |
| `plt_crop` | Crop whitespace from figure image |
| `plt_validate` | Validate recipe reproducibility |
| `plt_extract_data` | Extract plotted data arrays |
| `plt_info` | Get recipe metadata |
| `plt_get_plot_types` | List all supported plot types |
| `plt_list_styles` | List available style presets |
| `plt_diagram_create` | Create box-and-arrow diagram |
| `plt_diagram_render` | Render diagram to image |
| `plt_diagram_compile_mermaid` | Compile Mermaid diagram |
| `plt_diagram_compile_graphviz` | Compile Graphviz diagram |
| `plt_diagram_list_presets` | List diagram presets |
| `plt_line`, `plt_scatter`, `plt_bar`, ... | Per-type plot tools |

## CLI Summary

```bash
figrecipe plot spec.yaml           # Create from spec
figrecipe reproduce recipe.yaml    # Reproduce figure
figrecipe compose a.yaml b.yaml -o out.png  # Compose panels
figrecipe crop figure.png          # Crop whitespace
figrecipe validate recipe.yaml     # Check reproducibility
figrecipe gui recipe.yaml          # Launch GUI editor
figrecipe style list               # List style presets
figrecipe diagram render flow.mmd  # Render diagram
figrecipe mcp start                # Start MCP server
```
