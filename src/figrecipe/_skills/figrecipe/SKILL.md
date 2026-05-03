---
name: figrecipe
description: |
  [WHAT] Publication-ready matplotlib figures with mm-precision layouts, YAML recipes, declarative specs, multi-panel composition, whitespace cropping, style presets (SCITEX, MATPLOTLIB), and box-and-arrow diagrams.
  [WHEN] Use when the user asks to "make a figure", "plot this data", "save a figure", "lay out panels at exact mm sizes", "compose panels A/B/C", "crop whitespace", "reproduce a figure", "plot mean ± CI", "confusion matrix", "raster plot", "apply SCITEX style".
  [HOW] `import figrecipe` for the Python API; see leaf skills for entry points.
tags: [figrecipe]
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
* [11_cli-reference](11_cli-reference.md) + [13_cli-extras](13_cli-extras.md) — All CLI commands
* [12_mcp-tools](12_mcp-tools.md) + [14_mcp-tool-catalog](14_mcp-tool-catalog.md) — MCP tool reference

### Standards
* [20_return-fig](20_return-fig.md) — Convention: plotting functions must return fig

## At a glance

- MCP tools — see [12_mcp-tools.md](12_mcp-tools.md)
- CLI commands — see [11_cli-reference.md](11_cli-reference.md)
- Env vars — see [30_env-vars.md](30_env-vars.md)
