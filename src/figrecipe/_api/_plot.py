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
from typing import Any, Dict, List, Optional, Union

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
RESERVED_KEYS = {"type", "x", "y", "z", "data", "id"}

# Additional reserved keys for specific plot types
BOXPLOT_RESERVED_KEYS = {"color", "colors"}


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
        # Get underlying matplotlib figure
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

    # Normalize axes to 2D array for consistent indexing
    if nrows == 1 and ncols == 1:
        axes_array = np.array([[axes]])
    elif nrows == 1:
        axes_array = np.array([axes])
    elif ncols == 1:
        axes_array = np.array([[ax] for ax in axes])
    else:
        axes_array = axes

    # Handle plots specification
    if "plots" in spec:
        # Single axes mode - apply to first axes
        ax = axes_array[0, 0]
        _apply_plots(ax, spec["plots"])
        _apply_decorations(ax, spec)

    elif "axes" in spec or "subplots" in spec:
        # Multi-axes mode (support both "axes" and "subplots" keys)
        axes_specs = spec.get("axes") or spec.get("subplots", [])
        for ax_spec in axes_specs:
            # Support both row/col and panel formats
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
            ax = axes_array[row, col]
            if "plots" in ax_spec:
                _apply_plots(ax, ax_spec["plots"])
            _apply_decorations(ax, ax_spec)
    else:
        # No plots specified - just create empty figure
        pass

    # Apply global decorations if not already applied
    if "axes" not in spec:
        # Already applied in single axes mode
        pass

    # Add figure caption if specified
    caption = spec.get("caption")
    if caption:
        underlying_fig = fig._fig if hasattr(fig, "_fig") else fig
        caption_fontsize = spec.get("caption_fontsize", 8)
        underlying_fig.text(
            0.5,
            -0.02,
            caption,
            ha="center",
            va="top",
            fontsize=caption_fontsize,
            wrap=True,
            transform=underlying_fig.transFigure,
        )

    result = {
        "figure": fig,
        "axes": axes,
        "image_path": None,
        "recipe_path": None,
    }

    # Save or show
    if output_path:
        output_path = Path(output_path)
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
                output_path, dpi=dpi, facecolor=facecolor, transparent=transparent
            )
            result["image_path"] = output_path

    if show:
        plt.show()
    elif output_path:
        try:
            plt.close(fig)
        except TypeError:
            # RecordingFigure wrapper - close all instead
            plt.close("all")

    return result


def _apply_plots(ax, plots: List[Dict[str, Any]]) -> None:
    """Apply plot elements to an axes."""
    from ..styles import resolve_colors_in_kwargs

    for plot_spec in plots:
        plot_type = plot_spec.get("type", "line")

        if plot_type not in PLOT_TYPES:
            raise ValueError(f"Unknown plot type: {plot_type}")

        method_name = PLOT_TYPES[plot_type]
        method = getattr(ax, method_name)

        # Extract data - support both direct (x, y) and nested (data: {x, y}) formats
        data_spec = plot_spec.get("data", {})
        if isinstance(data_spec, dict):
            x = _resolve_data(plot_spec.get("x") or data_spec.get("x"))
            y = _resolve_data(plot_spec.get("y") or data_spec.get("y"))
            z = _resolve_data(plot_spec.get("z") or data_spec.get("z"))
            data = (
                _resolve_data(data_spec.get("dataset"))
                if "dataset" in data_spec
                else None
            )
        else:
            x, y, z = (
                _resolve_data(plot_spec.get("x")),
                _resolve_data(plot_spec.get("y")),
                _resolve_data(plot_spec.get("z")),
            )
            data = _resolve_data(data_spec)

        # Build kwargs (excluding reserved keys)
        excluded_keys = RESERVED_KEYS.copy()
        # For boxplot, also exclude color keys (handled separately)
        if plot_type in ("boxplot", "box"):
            excluded_keys = excluded_keys | BOXPLOT_RESERVED_KEYS
        kwargs = {k: v for k, v in plot_spec.items() if k not in excluded_keys}

        # Resolve named colors to style colors (e.g., "blue" -> SCITEX blue)
        kwargs = resolve_colors_in_kwargs(kwargs)

        # Call the appropriate method based on plot type
        if plot_type in ("hist", "pie", "eventplot"):
            # Single data argument
            if x is not None:
                method(x, **kwargs)
            elif data is not None:
                method(data, **kwargs)
        elif plot_type in ("boxplot", "box", "violinplot", "violin"):
            # Extract boxplot-specific color settings (already excluded from kwargs)
            box_colors = plot_spec.get("color") or plot_spec.get("colors")

            # Enable patch_artist for filled boxes (boxplot only)
            if plot_type in ("boxplot", "box"):
                kwargs.setdefault("patch_artist", True)

            # Call boxplot/violinplot
            plot_data = data if data is not None else x
            if plot_data is not None:
                result = method(plot_data, **kwargs)

                # Apply colors to boxplot boxes
                if plot_type in ("boxplot", "box") and box_colors is not None:
                    boxes = result.get("boxes", [])
                    if isinstance(box_colors, str):
                        # Single color for all boxes
                        for box in boxes:
                            box.set_facecolor(box_colors)
                    elif isinstance(box_colors, (list, tuple)):
                        # List of colors, one per box
                        for box, color in zip(boxes, box_colors):
                            box.set_facecolor(color)
        elif plot_type in ("imshow", "matshow", "heatmap"):
            # 2D data
            if data is not None:
                method(data, **kwargs)
            elif z is not None:
                method(z, **kwargs)
        elif plot_type in ("contour", "contourf", "pcolormesh"):
            # X, Y, Z data
            if x is not None and y is not None and z is not None:
                method(x, y, z, **kwargs)
            elif z is not None:
                method(z, **kwargs)
            elif data is not None:
                method(data, **kwargs)
        elif plot_type == "hist2d":
            if x is not None and y is not None:
                method(x, y, **kwargs)
        elif plot_type == "hexbin":
            if x is not None and y is not None:
                method(x, y, **kwargs)
        else:
            # Standard x, y plots
            if x is not None and y is not None:
                method(x, y, **kwargs)
            elif y is not None:
                method(y, **kwargs)
            elif x is not None:
                method(x, **kwargs)


def _apply_decorations(ax, spec: Dict[str, Any]) -> None:
    """Apply axes decorations (labels, title, legend, etc.)."""
    if "xlabel" in spec:
        ax.set_xlabel(spec["xlabel"])
    if "ylabel" in spec:
        ax.set_ylabel(spec["ylabel"])
    if "title" in spec:
        ax.set_title(spec["title"])
    if "xlim" in spec:
        ax.set_xlim(spec["xlim"])
    if "ylim" in spec:
        ax.set_ylim(spec["ylim"])

    # X-axis tick customization
    if "xticks" in spec:
        xticks_spec = spec["xticks"]
        underlying_ax = ax._ax if hasattr(ax, "_ax") else ax
        if isinstance(xticks_spec, dict):
            positions = xticks_spec.get("positions")
            labels = xticks_spec.get("labels")
            if positions is not None:
                underlying_ax.set_xticks(positions)
            if labels is not None:
                underlying_ax.set_xticklabels(labels)
        elif isinstance(xticks_spec, list):
            # Simple list of tick positions
            underlying_ax = ax._ax if hasattr(ax, "_ax") else ax
            underlying_ax.set_xticks(xticks_spec)

    # Y-axis tick customization
    if "yticks" in spec:
        yticks_spec = spec["yticks"]
        underlying_ax = ax._ax if hasattr(ax, "_ax") else ax
        if isinstance(yticks_spec, dict):
            positions = yticks_spec.get("positions")
            labels = yticks_spec.get("labels")
            if positions is not None:
                underlying_ax.set_yticks(positions)
            if labels is not None:
                underlying_ax.set_yticklabels(labels)
        elif isinstance(yticks_spec, list):
            underlying_ax.set_yticks(yticks_spec)

    if spec.get("legend"):
        ax.legend()
    if spec.get("grid"):
        ax.grid(True)
    if "aspect" in spec:
        ax.set_aspect(spec["aspect"])
    if "xscale" in spec:
        ax.set_xscale(spec["xscale"])
    if "yscale" in spec:
        ax.set_yscale(spec["yscale"])

    # Statistical annotations (significance brackets)
    if "stat_annotations" in spec:
        _apply_stat_annotations(ax, spec["stat_annotations"])

    # Text annotations
    if "annotations" in spec:
        _apply_text_annotations(ax, spec["annotations"])


def _apply_stat_annotations(ax, annotations: List[Dict[str, Any]]) -> None:
    """Apply statistical significance annotations."""
    from .._wrappers._stat_annotation import draw_stat_annotation

    # Get underlying matplotlib axes
    underlying_ax = ax._ax if hasattr(ax, "_ax") else ax

    for ann in annotations:
        x1 = ann.get("x1", 0)
        x2 = ann.get("x2", 1)
        y = ann.get("y")
        text = ann.get("text")
        p_value = ann.get("p_value")
        style = ann.get("style", "stars")

        draw_stat_annotation(
            underlying_ax,
            x1=x1,
            x2=x2,
            y=y,
            text=text,
            p_value=p_value,
            style=style,
        )


def _apply_text_annotations(ax, annotations: List[Dict[str, Any]]) -> None:
    """Apply text annotations to axes."""
    underlying_ax = ax._ax if hasattr(ax, "_ax") else ax

    for ann in annotations:
        text = ann.get("text", "")
        xy = ann.get("xy", (0.5, 0.5))
        fontsize = ann.get("fontsize", 8)
        ha = ann.get("ha", "center")
        va = ann.get("va", "center")
        color = ann.get("color", "black")
        fontweight = ann.get("fontweight", "normal")

        underlying_ax.text(
            xy[0],
            xy[1],
            text,
            fontsize=fontsize,
            ha=ha,
            va=va,
            color=color,
            fontweight=fontweight,
        )


def _resolve_data(data: Any) -> Any:
    """Resolve data - could be inline list, numpy array, or file reference."""
    if data is None:
        return None

    if isinstance(data, (list, tuple)):
        return np.array(data)

    if isinstance(data, str):
        # Could be a file path
        path = Path(data)
        if path.exists():
            if path.suffix == ".npy":
                return np.load(path)
            elif path.suffix == ".csv":
                return np.loadtxt(path, delimiter=",")
            elif path.suffix == ".npz":
                return np.load(path)

    return data
