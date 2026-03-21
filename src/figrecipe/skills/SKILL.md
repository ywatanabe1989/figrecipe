---
name: figrecipe
description: Publication-ready scientific figures with declarative plot specification, composition, cropping, and diagram generation. Use when creating plots, composing multi-panel figures, or generating diagrams for papers.
allowed-tools: mcp__scitex__plt_*
---

# Publication-Ready Figures with figrecipe

## Quick Start

```python
import figrecipe as fr

# Create a figure
fig, axes = fr.subplots(nrows=1, ncols=2, w_mm=170, h_mm=80)
axes[0].plot(x, y)
fr.save(fig, "figure.png")

# Reproduce from YAML recipe
fig = fr.reproduce("recipe.yaml")

# Compose multi-panel figure
fr.compose(["panel_a.png", "panel_b.png"], ncols=2, output="figure.png")
```

## Common Workflows

### "I need a simple plot"

```python
fig, ax = fr.subplots(w_mm=85, h_mm=60)
ax.plot(x, y, label="data")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
fr.save(fig, "plot.png")
```

### "I need a multi-panel figure"

```python
# From code
fig, axes = fr.subplots(nrows=2, ncols=3, w_mm=170, h_mm=120)
for ax, data in zip(axes.flat, datasets):
    ax.plot(data)
fr.save(fig, "panels.png")

# From existing images
fr.compose(
    ["a.png", "b.png", "c.png", "d.png"],
    ncols=2,
    labels=True,  # Auto a, b, c, d labels
    output="composed.png",
)
```

### "I need a diagram (not a data plot)"

```python
# Mermaid
diagram = fr.Diagram("graph LR; A-->B; B-->C")
diagram.render("flow.png")

# Graphviz
diagram = fr.Diagram("digraph { A -> B -> C }", backend="graphviz")
diagram.render("graph.png")
```

### "I need to crop whitespace"

```python
fr.crop("figure.pdf", output="figure_cropped.pdf", margins_mm=2)
```

### "I need to extract data from a figure"

```python
data = fr.extract_data("plot.png")
# Returns dict of extracted x, y arrays
```

## Style System

```python
# Load journal-specific style
fr.load_style("nature")
fr.load_style("ieee")

# List available styles
fr.list_presets()

# Custom style from YAML
fr.load_style("my_style.yaml")
```

## CLI Commands

```bash
# Create plots
figrecipe plot recipe.yaml -o figure.png
figrecipe plot recipe.yaml --style nature

# Reproduce from recipe
figrecipe reproduce recipe.yaml -o output.png

# Compose multi-panel
figrecipe compose a.png b.png c.png -n 3 -o composed.png

# Crop whitespace
figrecipe crop figure.pdf -o cropped.pdf -m 2

# Image processing
figrecipe convert figure.eps -o figure.png
figrecipe diff old.png new.png -o diff.png

# Diagrams
figrecipe diagram render flow.mmd -o flow.png
figrecipe diagram create --preset flowchart

# Validate recipe
figrecipe validate recipe.yaml

# Style management
figrecipe style list
figrecipe fonts list

# Data extraction
figrecipe extract figure.png -o data.csv

# MCP server
figrecipe mcp run
figrecipe mcp install

# Skills (self-describing)
figrecipe skills list
figrecipe skills get SKILL
figrecipe skills get plot-types
```

## MCP Tools (for AI agents)

| Tool | Purpose |
|------|---------|
| `plt_plot` | Create a plot from data/recipe |
| `plt_reproduce` | Reproduce figure from YAML recipe |
| `plt_compose` | Compose multi-panel figure |
| `plt_crop` | Crop whitespace from figure |
| `plt_validate` | Validate a recipe file |
| `plt_extract_data` | Extract data from figure image |
| `plt_info` | Get figure metadata |
| `plt_get_plot_types` | List available plot types |
| `plt_list_styles` | List available style presets |
| `plt_diagram_create` | Create diagram from spec |
| `plt_diagram_render` | Render diagram to image |
| `plt_diagram_compile_mermaid` | Compile Mermaid diagram |
| `plt_diagram_compile_graphviz` | Compile Graphviz diagram |
| `plt_diagram_list_presets` | List diagram presets |

## Packaging: Bridge Frontend Source

figrecipe provides a workspace bridge via `_django/frontend/src/`. The `[app]` optional extra (`pip install figrecipe[app]`) provides Python deps for platform integration. The frontend TypeScript source stays in the repo (excluded from pip wheel) and is discovered by scitex-cloud via sibling-directory scanning. In CI, clone the repo as a sibling.

## Specific Topics

* **Available plot types** [references/plot-types.md](references/plot-types.md)
