#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP Resources for figrecipe documentation."""

from __future__ import annotations

__all__ = ["register_resources"]

CHEATSHEET = """\
# FigRecipe Cheatsheet - Reproducible Matplotlib Figures
=========================================================

## Quick Start
```python
import figrecipe as fr
import numpy as np

# Create figure with recording enabled
fig, ax = fr.subplots()

# Plot using standard matplotlib API (auto-recorded!)
x = np.linspace(0, 10, 100)
ax.plot(x, np.sin(x), label="sin(x)")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("My Plot")
ax.legend()

# Save -> creates BOTH image AND recipe YAML
fr.save(fig, "my_plot.png")
# Output: my_plot.png + my_plot.yaml + my_plot_data/
```

## Output Files (Auto-Generated)
```
my_plot.png          # The image file
my_plot.yaml         # Recipe for reproduction
my_plot_data/        # Data CSV files for each plot call
  ├── plot_000_x.csv   # X data from first plot call
  └── plot_000_y.csv   # Y data from first plot call
```

## CSV Input Support (for MCP declarative specs)
```yaml
plots:
  - type: scatter
    data_file: experiment.csv  # Path to CSV file
    x: time                    # Column name (not array!)
    y: temperature             # Column name
    color: blue
```

## Reproduce a Figure
```python
# Recreate figure from recipe
fig, ax = fr.reproduce("my_plot.yaml")
fr.save(fig, "reproduced.png")

# Or from the image directly
fig, ax = fr.reproduce("my_plot.png")
```

## Compose Multi-Panel Figures
```python
# Create individual panels first
fig1, ax1 = fr.subplots()
ax1.plot(x, y1)
fr.save(fig1, "panel_a.png")

fig2, ax2 = fr.subplots()
ax2.plot(x, y2)
fr.save(fig2, "panel_b.png")

# Compose into multi-panel figure
fig, axes = fr.compose(
    layout=(1, 2),  # 1 row, 2 columns
    sources={
        (0, 0): "panel_a.yaml",
        (0, 1): "panel_b.yaml",
    }
)
fr.save(fig, "composed.png")
```

## Statistical Annotations
```python
fig, ax = fr.subplots()
ax.bar(["Ctrl", "Exp"], [10, 15], yerr=[1, 1.5])

# Add significance bracket
ax.add_stat_annotation(
    x1=0, x2=1,
    p_value=0.01,      # Auto-converts to **
    style="stars"      # Options: "stars", "p_value", "both"
)
```

## MCP Declarative Spec (for AI agents)
```yaml
figure:
  width_mm: 80
  height_mm: 60
plots:
  - type: line
    x: [1, 2, 3, 4, 5]
    y: [1, 4, 9, 16, 25]
    color: blue
    label: "y = x^2"
xlabel: "X"
ylabel: "Y"
title: "Quadratic Function"
legend: true
```

## Key Patterns
1. **Recording is automatic** - Just use standard matplotlib API
2. **Always creates recipe** - PNG + YAML together
3. **Data is preserved** - CSV files in _data directory
4. **Reproducibility validated** - fr.save() checks MSE on save
"""

MODULE_CORE = """\
# FigRecipe Core API
====================

## Creating Figures

### fr.subplots()
```python
# Single axes
fig, ax = fr.subplots()

# Multiple axes
fig, axes = fr.subplots(nrows=2, ncols=2)

# With size specification (mm-based for publications)
fig, ax = fr.subplots(
    axes_width_mm=80,
    axes_height_mm=60,
    margin_left_mm=15
)
```

### Recording Methods
All standard matplotlib methods are auto-recorded when called on RecordingAxes:

**Plotting:**
- ax.plot(), ax.scatter(), ax.bar(), ax.barh()
- ax.hist(), ax.boxplot(), ax.violinplot()
- ax.imshow(), ax.contour(), ax.contourf()
- ax.fill(), ax.fill_between(), ax.fill_betweenx()
- ax.pie(), ax.errorbar(), ax.stem()
- ax.hlines(), ax.vlines(), ax.axhline(), ax.axvline()

**Decorations:**
- ax.set_xlabel(), ax.set_ylabel(), ax.set_title()
- ax.legend(), ax.annotate(), ax.text()
- ax.set_xlim(), ax.set_ylim()

## Saving and Loading

### fr.save()
```python
fr.save(fig, "plot.png")           # PNG + YAML
fr.save(fig, "plot.pdf", dpi=300)  # PDF + YAML
fr.save(fig, "plot.svg")           # SVG + YAML
fr.save(fig, "plot.png", validate=False)  # Skip validation
```

### fr.reproduce()
```python
fig, ax = fr.reproduce("plot.yaml")
fig, ax = fr.reproduce("plot.png")  # Also works
```

## Composition

### fr.compose()
```python
fig, axes = fr.compose(
    layout=(2, 2),  # 2x2 grid
    sources={
        (0, 0): "panel_a.yaml",
        (0, 1): "panel_b.yaml",
        (1, 0): "panel_c.yaml",
        (1, 1): "photo.png",  # Raw images also work
    }
)
```

## Statistical Annotations

### ax.add_stat_annotation()
```python
ax.add_stat_annotation(
    x1=0, x2=1,           # Positions
    p_value=0.001,        # Auto: *** for p<0.001
    y=15,                 # Bracket height (auto if None)
    style="stars"         # "stars", "p_value", "both"
)

# Multiple comparisons
ax.add_stat_annotation(x1=0, x2=1, p_value=0.05)  # *
ax.add_stat_annotation(x1=0, x2=2, p_value=0.01, y=18)  # **
ax.add_stat_annotation(x1=1, x2=2, p_value=0.001, y=20)  # ***
```

## Panel Metadata

### ax.set_caption()
```python
ax.set_caption("(A) Control vs Treatment comparison")
```

### ax.set_stats()
```python
ax.set_stats({
    "n": 50,
    "mean": 12.5,
    "std": 2.3,
    "comparisons": [{"vs": "control", "p_value": 0.002}]
})
```

## Context Manager
```python
# Temporarily disable recording
with ax.no_record():
    ax.plot(x, debug_line)  # Not recorded
```
"""

MCP_SPEC = """\
# FigRecipe MCP Declarative Specification
==========================================

AI agents can create figures using the `plot` MCP tool with a YAML-like spec.

## RECOMMENDED: CSV Column Input
Use CSV files for data - this separates data from visualization and enables
code integration (Python/R writes CSV, MCP visualizes it).

```yaml
figure:
  width_mm: 80
  height_mm: 60

plots:
  - type: scatter
    data_file: results.csv     # Path to CSV file
    x: time_sec                 # Column name (string = column lookup)
    y: amplitude_mv             # Column name
    color: blue
    label: "Measured"

  - type: line
    data_file: results.csv     # Same or different CSV
    x: time_sec
    y: fitted_amplitude        # Different column
    color: red
    linestyle: "--"
    label: "Fitted"

xlabel: "Time (s)"
ylabel: "Amplitude (mV)"
title: "Signal Analysis"
legend: true
```

**Workflow**: Your analysis code writes CSV → MCP plots from CSV columns

## Alternative: Inline Data (for simple cases)
```yaml
plots:
  - type: line
    x: [1, 2, 3, 4]     # Inline array (less flexible)
    y: [1, 4, 9, 16]
    color: blue
```

## Supported Plot Types
- **line**: Line plot (x, y required)
- **scatter**: Scatter plot (x, y required)
- **bar**: Bar chart (x, height required)
- **barh**: Horizontal bar chart (y, width required)
- **hist**: Histogram (data required)
- **boxplot**: Box plot (data required)
- **violinplot**: Violin plot (data required)
- **imshow**: Heatmap (data required, 2D array)
- **errorbar**: Error bars (x, y, yerr required)
- **fill_between**: Filled region (x, y1, y2 required)
- **heatmap**: Annotated heatmap (data required)

## Statistical Annotations
```yaml
stat_annotations:
  - x1: 0
    x2: 1
    p_value: 0.01
    style: stars      # Shows **
  - x1: 0
    x2: 2
    text: "p<0.001"   # Custom text
    y: 15             # Y position
```

## Multi-Axes Layout
```yaml
axes:
  - position: [0, 0]  # Top-left
    plots:
      - type: line
        x: [1, 2, 3]
        y: [1, 4, 9]
    xlabel: "X"
    ylabel: "Y"

  - position: [0, 1]  # Top-right
    plots:
      - type: bar
        x: ["A", "B", "C"]
        height: [10, 20, 15]
```

## Example: Complete Figure Spec
```yaml
figure:
  width_mm: 85          # Nature single column
  height_mm: 70

plots:
  - type: scatter
    x: [1, 2, 3, 4, 5, 6, 7, 8]
    y: [2.1, 4.2, 5.8, 8.1, 9.9, 12.2, 14.0, 16.1]
    color: blue
    alpha: 0.7
    label: "Experimental data"

  - type: line
    x: [1, 8]
    y: [2, 16]
    color: red
    linestyle: "--"
    label: "Linear fit (r=0.99)"

xlabel: "Time (hours)"
ylabel: "Concentration (mM)"
title: "Enzyme Kinetics"
legend:
  loc: "upper left"

stat_annotations:
  - x1: 2
    x2: 6
    p_value: 0.003
    y: 14
    style: stars
```

## Colors
Named colors are resolved to publication-quality palette:
- blue, red, green, orange, purple, navy, pink, brown, gray
- Or use hex: "#1f77b4", RGB: [0.12, 0.47, 0.71]

## Tips for AI Agents
1. Always provide both x and y data for line/scatter plots
2. Use stat_annotations for significance indicators
3. Set appropriate figure size for journal (85mm for single column)
4. Use legend:true or legend:{loc:"best"} for multiple series
5. Call the plot MCP tool with output_path to save
"""

INTEGRATION = """\
# FigRecipe Integration with SciTeX
====================================

FigRecipe provides the plotting infrastructure for SciTeX (stx.plt).

## Using via SciTeX
```python
import scitex as stx

@stx.session
def main(plt=stx.INJECTED):
    fig, ax = stx.plt.subplots()
    ax.stx_line(x, y)  # Tracked with auto CSV export
    stx.io.save(fig, "plot.png", symlink_to="./data")
```

## Using FigRecipe Directly
```python
import figrecipe as fr

fig, ax = fr.subplots()
ax.plot(x, y)  # Standard matplotlib API
fr.save(fig, "plot.png")
```

## Key Differences
| Feature | SciTeX (stx.plt) | FigRecipe (fr) |
|---------|------------------|----------------|
| Import | `import scitex as stx` | `import figrecipe as fr` |
| Methods | `ax.stx_line()` | `ax.plot()` |
| Session | `@stx.session` | Not needed |
| Save | `stx.io.save()` | `fr.save()` |
| Symlinks | Built-in | Manual |

## Recipe Format Compatibility
Both produce identical YAML recipes that can be reproduced:
```python
# Reproduce SciTeX figure with figrecipe
fig, ax = fr.reproduce("scitex_plot.yaml")

# Or vice versa (if stx.plt is available)
fig, ax = stx.plt.reproduce("figrecipe_plot.yaml")
```

## When to Use Which
- **SciTeX**: Full experiment workflow (session, logging, symlinks)
- **FigRecipe**: Standalone figure creation and reproduction
"""


def register_resources(mcp) -> None:
    """Register documentation resources for figrecipe MCP server."""

    @mcp.resource("figrecipe://cheatsheet")
    def cheatsheet() -> str:
        """FigRecipe quick reference cheatsheet."""
        return CHEATSHEET

    @mcp.resource("figrecipe://api/core")
    def api_core() -> str:
        """FigRecipe core API documentation."""
        return MODULE_CORE

    @mcp.resource("figrecipe://mcp-spec")
    def mcp_spec() -> str:
        """Declarative specification format for MCP tools."""
        return MCP_SPEC

    @mcp.resource("figrecipe://integration")
    def integration() -> str:
        """FigRecipe integration with SciTeX."""
        return INTEGRATION


# EOF
