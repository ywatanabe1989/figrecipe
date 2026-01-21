#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Declarative figure creation from spec dictionaries.

Spec Format
-----------
figure:
  width_mm: 80           # Figure width in mm
  height_mm: 60          # Figure height in mm
  nrows: 1               # Number of subplot rows
  ncols: 1               # Number of subplot columns
  style: SCITEX          # Style preset: SCITEX or MATPLOTLIB
  facecolor: white       # Background color (default: transparent)

plots:                   # List of plot elements (for single axes)
  - type: line           # Plot type: line, scatter, bar, hist, box, etc.
    x: [1, 2, 3]         # X data (list or reference to external file)
    y: [1, 4, 9]         # Y data
    color: blue          # Any matplotlib kwargs
    label: "my line"
    yerr: [0.1, 0.2, 0.1]  # Error bars (optional)
    capsize: 3           # Error bar cap size (optional)

  # CSV column support - use column names from data_file
  - type: scatter
    data_file: experiment.csv  # Path to CSV file
    x: time                    # Column name (string = column lookup)
    y: temperature             # Column name
    color: red

axes:                    # For multi-axes figures
  - row: 0
    col: 0
    plots: [...]
    xlabel: "X"
    ylabel: "Y"

stat_annotations:        # Statistical significance brackets
  - x1: 0                # Left group x position
    x2: 1                # Right group x position
    y: 5.5               # Bracket y position
    text: "***"          # Explicit text: "***", "**", "*", "n.s."
  - x1: 0
    x2: 2
    y: 6.5
    p_value: 0.02        # Auto-convert to stars (alternative to text)
    style: stars         # "stars", "p_value", "both", "bracket_only"

# Axes decorations (apply to single axes or all axes)
xlabel: "X axis"
ylabel: "Y axis"
title: "My Title"
legend: true
xlim: [0, 10]
ylim: [0, 100]

xticks:                  # Custom x-axis ticks
  positions: [0, 1, 2]   # Tick positions
  labels: ["A", "B", "C"]  # Tick labels (categorical)

yticks:                  # Custom y-axis ticks (same format)
  positions: [0, 5, 10]
  labels: ["Low", "Med", "High"]
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np

# Supported plot types and their matplotlib method names
PLOT_TYPES = {
    # Line/curve
    "line": "plot",
    "plot": "plot",
    "step": "step",
    "fill": "fill",
    "fill_between": "fill_between",
    "fill_betweenx": "fill_betweenx",
    "errorbar": "errorbar",
    # Scatter/points
    "scatter": "scatter",
    # Bar/categorical
    "bar": "bar",
    "barh": "barh",
    # Distribution
    "hist": "hist",
    "hist2d": "hist2d",
    "boxplot": "boxplot",
    "box": "boxplot",
    "violinplot": "violinplot",
    "violin": "violinplot",
    # Image/matrix
    "imshow": "imshow",
    "matshow": "matshow",
    "pcolormesh": "pcolormesh",
    "contour": "contour",
    "contourf": "contourf",
    # Special
    "pie": "pie",
    "stem": "stem",
    "eventplot": "eventplot",
    "hexbin": "hexbin",
    # Spectral
    "specgram": "specgram",
    "psd": "psd",
    # Heatmap (convenience alias)
    "heatmap": "imshow",
}

# Keys that are not matplotlib kwargs
RESERVED_KEYS = {"type", "x", "y", "z", "data", "id", "data_file", "style"}


def create_figure_from_spec(
    spec: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None,
    dpi: int = 300,
    save_recipe: bool = False,
    show: bool = False,
) -> Dict[str, Any]:
    """Create a matplotlib figure from a declarative spec.

    Parameters
    ----------
    spec : dict
        Declarative specification for the figure.
    output_path : str or Path, optional
        Path to save the figure.
    dpi : int
        DPI for raster output.
    save_recipe : bool
        If True, also save as figrecipe recipe.
    show : bool
        If True, display the figure.

    Returns
    -------
    dict
        Result containing 'figure', 'axes', 'image_path', 'recipe_path'.
    """
    import matplotlib.pyplot as plt

    import figrecipe as fr

    from ._plot_helpers import apply_decorations, apply_plots

    # Extract figure config
    fig_config = spec.get("figure", {})
    style = fig_config.get("style")

    # Apply style if specified
    if style:
        fr.load_style(style)

    # Create figure
    nrows = fig_config.get("nrows", 1)
    ncols = fig_config.get("ncols", 1)

    fig_kwargs = {}
    if "width_mm" in fig_config:
        fig_kwargs["axes_width_mm"] = fig_config["width_mm"] / ncols
    if "height_mm" in fig_config:
        fig_kwargs["axes_height_mm"] = fig_config["height_mm"] / nrows

    fig, axes = fr.subplots(nrows=nrows, ncols=ncols, **fig_kwargs)

    # Apply facecolor if specified (for non-transparent backgrounds)
    facecolor = fig_config.get("facecolor")
    if facecolor:
        _apply_facecolor(fig, axes, facecolor)

    # Normalize axes to 2D array for consistent indexing
    axes_array = _normalize_axes_array(axes, nrows, ncols)

    # Handle plots specification
    if "plots" in spec:
        # Single axes mode - apply to first axes
        ax = axes_array[0, 0]
        apply_plots(ax, spec["plots"], PLOT_TYPES, RESERVED_KEYS)
        apply_decorations(ax, spec)

    elif "axes" in spec or "subplots" in spec:
        # Multi-axes mode (support both "axes" and "subplots" keys)
        axes_specs = spec.get("axes") or spec.get("subplots", [])
        for ax_spec in axes_specs:
            row, col = _parse_axes_position(ax_spec)
            ax = axes_array[row, col]
            if "plots" in ax_spec:
                apply_plots(ax, ax_spec["plots"], PLOT_TYPES, RESERVED_KEYS)
            apply_decorations(ax, ax_spec)

    # Add figure caption if specified
    caption = spec.get("caption")
    if caption:
        _add_caption(fig, caption, spec.get("caption_fontsize", 8))

    result = {
        "figure": fig,
        "axes": axes,
        "image_path": None,
        "recipe_path": None,
    }

    # Save or show
    if output_path:
        output_path = Path(output_path)
        result = _save_figure(fig, output_path, dpi, save_recipe, facecolor, result)

    if show:
        plt.show()
    elif output_path:
        _close_figure(fig)

    return result


def _apply_facecolor(fig, axes, facecolor: str) -> None:
    """Apply facecolor to figure and axes backgrounds."""
    underlying_fig = fig._fig if hasattr(fig, "_fig") else fig
    underlying_fig.patch.set_facecolor(facecolor)
    # Also set axes facecolor for consistent background
    if hasattr(axes, "__iter__"):
        for ax in np.array(axes).flat:
            underlying_ax = ax._ax if hasattr(ax, "_ax") else ax
            underlying_ax.set_facecolor(facecolor)
    else:
        underlying_ax = axes._ax if hasattr(axes, "_ax") else axes
        underlying_ax.set_facecolor(facecolor)


def _normalize_axes_array(axes, nrows: int, ncols: int) -> np.ndarray:
    """Normalize axes to 2D array for consistent indexing."""
    if nrows == 1 and ncols == 1:
        return np.array([[axes]])
    elif nrows == 1:
        return np.array([axes])
    elif ncols == 1:
        return np.array([[ax] for ax in axes])
    else:
        return axes


def _parse_axes_position(ax_spec: Dict) -> tuple:
    """Parse axes position from spec (supports row/col or panel formats)."""
    if "panel" in ax_spec:
        # Parse panel like "0,0" or "0,1"
        panel = ax_spec["panel"]
        if isinstance(panel, str):
            parts = panel.split(",")
            row = int(parts[0].strip())
            col = int(parts[1].strip()) if len(parts) > 1 else 0
        else:
            row, col = 0, 0
    else:
        row = ax_spec.get("row", 0)
        col = ax_spec.get("col", 0)
    return row, col


def _add_caption(fig, caption: str, fontsize: int) -> None:
    """Add caption text below figure."""
    underlying_fig = fig._fig if hasattr(fig, "_fig") else fig
    underlying_fig.text(
        0.5,
        -0.02,
        caption,
        ha="center",
        va="top",
        fontsize=fontsize,
        wrap=True,
        transform=underlying_fig.transFigure,
    )


def _save_figure(
    fig, output_path: Path, dpi: int, save_recipe: bool, facecolor, result: dict
) -> dict:
    """Save figure to file."""
    import figrecipe as fr

    # Determine transparency based on facecolor
    transparent = facecolor is None or (
        isinstance(facecolor, str) and facecolor.lower() in ("none", "transparent")
    )

    if save_recipe:
        img_path, recipe_path, _ = fr.save(
            fig,
            output_path,
            dpi=dpi,
            validate=False,
            verbose=False,
            facecolor=facecolor,
        )
        result["image_path"] = img_path
        result["recipe_path"] = recipe_path
    else:
        fig.savefig(
            output_path,
            dpi=dpi,
            facecolor=facecolor,
            transparent=transparent,
            save_recipe=False,
            validate=False,
        )
        result["image_path"] = output_path

    return result


def _close_figure(fig) -> None:
    """Close figure, handling RecordingFigure wrapper."""
    import matplotlib.pyplot as plt

    try:
        plt.close(fig)
    except TypeError:
        # RecordingFigure wrapper - close all instead
        plt.close("all")
