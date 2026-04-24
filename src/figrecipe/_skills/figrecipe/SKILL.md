---
description: Publication-ready matplotlib figures with mm-precision layouts, YAML recipes, declarative specs, multi-panel composition, whitespace cropping, style presets (SCITEX, MATPLOTLIB), and box-and-arrow diagrams. Supports 70+ plot types — every matplotlib kind plus scitex-specialized ones (`fr_mean_ci`, `fr_mean_std`, `fr_median_iqr`, `fr_shaded_line`, `fr_conf_mat`, `fr_raster`, `fr_violin`, `fr_scatter_hist`, `fr_heatmap` and `stx_*` aliases). Drop-in replacement for raw `matplotlib.pyplot`, `seaborn` (`fr.sns` re-export), manual `GridSpec` layouts, hand-rolled subplot labeling, and `mermaid-cli`/`graphviz`. Use when the user asks to "make a figure", "plot this data", "save a figure", "lay out panels at exact mm sizes", "compose panels A/B/C", "crop whitespace", "reproduce a figure", "plot mean ± CI", "confusion matrix", "raster plot", "apply SCITEX style", or "draw a Mermaid / Graphviz diagram". Every saved figure ships a YAML recipe so it can be regenerated bit-for-bit later.
allowed-tools: mcp__scitex__plt_*
primary_interface: mixed
interfaces:
  python: 3
  cli: 1
  mcp: 3
  skills: 2
  hook: 0
  http: 0
---

# figrecipe

> **Interfaces:** Python ⭐⭐⭐ · CLI ⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP —

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
* [21_scientific-figure-patterns](21_scientific-figure-patterns.md) — Comparison plots (shared color scale + single colorbar), shared time axes (heatmap + averaged profile), per-subject grids, PDF report assembly with bookmarks/size budget. Implements universal rules from `general/30_scientific-figures.md`.

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


## Environment

- [30_env-vars.md](30_env-vars.md) — SCITEX_* env vars read by figrecipe at runtime
