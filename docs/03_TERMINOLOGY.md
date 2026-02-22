<!-- ---
!-- Timestamp: 2026-02-22 20:35:53
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/docs/03_TERMINOLOGY.md
!-- --- -->

# FigRecipe Terminology

Consistent naming across code, docs, and UI.

---

## Core Hierarchy

```
Canvas (editor workspace)
 └─ Figure (matplotlib Figure, mm-sized)
     └─ Axes (single plot panel)
         ├─ Axis (x or y ruler with ticks)
         └─ Plot (visual data: lines, bars, scatter, etc.)
```

## Definitions

### Canvas

The **editor workspace** — an HTML/CSS container with a mm-grid background,
rulers, zoom/pan controls, and snap guides. Not a matplotlib object.
Figures are placed on the canvas at absolute (x, y) pixel positions.

- Dark/light theme affects only canvas appearance, not figure content
- Supports drag-to-move, snapping, and multi-figure composition

### Figure

A **matplotlib `Figure`** — the top-level container for all visual
elements. In FigRecipe, figure dimensions are defined in exact mm via
the style system (margins, axes sizes, spacing).

- Wrapped as `RecordingFigure` to track recipe operations
- `fig._fig` accesses the underlying matplotlib Figure
- `fig.patch` is the background rectangle
- One figure = one `.yaml` recipe = one output image

### Axes

A **single plot panel** (matplotlib `Axes`). One figure can contain a
grid of axes (e.g., 2x3). Each axes has its own coordinate system,
spines, ticks, labels, and title.

- FigRecipe returns axes as a 2D list: `axes[row][col]`
- `ax.ax` accesses the underlying matplotlib Axes (via `RecordingAxes`)
- Plural "axes" refers to multiple panels, not the x/y axis lines

### Axis

A **single x or y ruler line** (matplotlib `XAxis` / `YAxis`).
Part of an axes. Contains:

- Tick marks and tick labels
- Axis label (e.g., "Time (s)")
- Scale (linear, log, etc.)

Not to be confused with "axes" (the panel container).

### Plot

The **visual data representation** drawn within an axes — lines, bars,
scatter points, histograms, contours, images, etc. In matplotlib these
are "artists" (`Line2D`, `PathCollection`, `BarContainer`, etc.).

### Panel

Synonym for **axes** in FigRecipe context. Used in:

- Panel labels: "A", "B", "C" (auto-generated)
- `panel_bboxes`: bounding boxes per axes for snap alignment
- `align_panels()`, `distribute_panels()`

### Style

A **named configuration** (e.g., `SCITEX`) defining mm-based dimensions:
margins, axes sizes, spacing, fonts, line widths, colors. Applied globally
to all figures in a session.

### Recipe

A **YAML file** that fully describes how to reproduce a figure:
plot type, data source, style overrides, panel layout. The single
source of truth for figure reproducibility.

---

## Editor-Specific Terms

| Term | Meaning |
|------|---------|
| **Hitmap** | Color-coded overlay mapping pixel regions to figure elements |
| **Bbox** | Bounding box — `{x, y, width, height}` in image pixels |
| **Placed figure** | A figure positioned on the canvas at `(x, y)` |
| **Snap guide** | Visual alignment line shown during drag |
| **Composition** | Multi-figure arrangement on the canvas |

---

## Common Confusions

| Wrong | Right | Why |
|-------|-------|-----|
| "the axes line" | "the axis" | Axes = panel, axis = ruler line |
| "tight layout" | "mm-based layout" | FigRecipe uses explicit mm positions, not auto-layout |
| "canvas background" | "figure background" | Canvas is the editor; figure is the matplotlib object |
| `bbox_inches="tight"` | (omit) | Breaks mm coordinates — never use in FigRecipe editor |

<!-- EOF -->
