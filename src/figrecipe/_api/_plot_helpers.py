#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper functions for declarative plot creation."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


def apply_plots(
    ax, plots: List[Dict[str, Any]], plot_types: Dict, reserved_keys: set
) -> None:
    """Apply plot elements to an axes."""
    from ..styles import resolve_colors_in_kwargs

    # Additional reserved keys for specific plot types
    boxplot_reserved_keys = {"color", "colors"}

    for plot_spec in plots:
        plot_type = plot_spec.get("type", "line")

        if plot_type not in plot_types:
            raise ValueError(f"Unknown plot type: {plot_type}")

        method_name = plot_types[plot_type]
        method = getattr(ax, method_name)

        # Extract data - support both direct (x, y) and nested (data: {x, y}) formats
        data_spec = plot_spec.get("data", {})
        data_file = plot_spec.get("data_file")

        if isinstance(data_spec, dict):
            x = resolve_data(
                plot_spec.get("x") or data_spec.get("x"),
                data_file=data_file,
            )
            y = resolve_data(
                plot_spec.get("y") or data_spec.get("y"),
                data_file=data_file,
            )
            z = resolve_data(
                plot_spec.get("z") or data_spec.get("z"),
                data_file=data_file,
            )
            data = (
                resolve_data(data_spec.get("dataset"), data_file=data_file)
                if "dataset" in data_spec
                else None
            )
        else:
            x = resolve_data(plot_spec.get("x"), data_file=data_file)
            y = resolve_data(plot_spec.get("y"), data_file=data_file)
            z = resolve_data(plot_spec.get("z"), data_file=data_file)
            data = resolve_data(data_spec, data_file=data_file)

        # Build kwargs (excluding reserved keys)
        excluded_keys = reserved_keys.copy()
        # For boxplot, also exclude color keys (handled separately)
        if plot_type in ("boxplot", "box"):
            excluded_keys = excluded_keys | boxplot_reserved_keys
        kwargs = {k: v for k, v in plot_spec.items() if k not in excluded_keys}

        # Resolve named colors to style colors (e.g., "blue" -> SCITEX blue)
        kwargs = resolve_colors_in_kwargs(kwargs)

        # Call the appropriate method based on plot type
        _call_plot_method(method, plot_type, x, y, z, data, kwargs, plot_spec, ax)


def _call_plot_method(method, plot_type, x, y, z, data, kwargs, plot_spec, ax=None):
    """Call the appropriate plot method based on plot type."""
    if plot_type in ("hist", "pie", "eventplot"):
        # Single data argument
        if x is not None:
            method(x, **kwargs)
        elif data is not None:
            method(data, **kwargs)
    elif plot_type in ("boxplot", "box", "violinplot", "violin"):
        _apply_boxplot(method, plot_type, x, data, kwargs, plot_spec, ax)
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


def _apply_boxplot(method, plot_type, x, data, kwargs, plot_spec, ax=None):
    """Apply boxplot or violinplot with color handling."""
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
                for box in boxes:
                    box.set_facecolor(box_colors)
            elif isinstance(box_colors, (list, tuple)):
                for box, color in zip(boxes, box_colors):
                    box.set_facecolor(color)

        # Apply publication styling from loaded SCITEX style after boxplot creation
        if plot_type in ("boxplot", "box") and ax is not None:
            from ..styles._plot_styles import apply_boxplot_style
            from ..styles._style_loader import get_current_style_dict

            # Get underlying matplotlib axes if wrapped
            mpl_ax = ax._ax if hasattr(ax, "_ax") else ax
            # Use loaded style (e.g., SCITEX) instead of hardcoded values
            style_dict = get_current_style_dict()
            apply_boxplot_style(mpl_ax, style_dict)


def apply_decorations(ax, spec: Dict[str, Any]) -> None:
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

    _apply_tick_customization(ax, spec)

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
        apply_stat_annotations(ax, spec["stat_annotations"])

    # Text annotations
    if "annotations" in spec:
        apply_text_annotations(ax, spec["annotations"])


def _apply_tick_customization(ax, spec: Dict[str, Any]) -> None:
    """Apply custom tick positions and labels."""
    underlying_ax = ax._ax if hasattr(ax, "_ax") else ax

    # X-axis tick customization
    if "xticks" in spec:
        xticks_spec = spec["xticks"]
        if isinstance(xticks_spec, dict):
            positions = xticks_spec.get("positions")
            labels = xticks_spec.get("labels")
            if positions is not None:
                underlying_ax.set_xticks(positions)
            if labels is not None:
                underlying_ax.set_xticklabels(labels)
        elif isinstance(xticks_spec, list):
            underlying_ax.set_xticks(xticks_spec)

    # Y-axis tick customization
    if "yticks" in spec:
        yticks_spec = spec["yticks"]
        if isinstance(yticks_spec, dict):
            positions = yticks_spec.get("positions")
            labels = yticks_spec.get("labels")
            if positions is not None:
                underlying_ax.set_yticks(positions)
            if labels is not None:
                underlying_ax.set_yticklabels(labels)
        elif isinstance(yticks_spec, list):
            underlying_ax.set_yticks(yticks_spec)


def apply_stat_annotations(ax, annotations: List[Dict[str, Any]]) -> None:
    """Apply statistical significance annotations."""
    from .._wrappers._stat_annotation import draw_stat_annotation

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


def apply_text_annotations(ax, annotations: List[Dict[str, Any]]) -> None:
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


# Cache for loaded CSV files
_csv_cache: Dict[str, Any] = {}


def resolve_data(
    data: Any,
    data_file: Optional[str] = None,
) -> Any:
    """Resolve data - could be inline list, column name (with data_file), or file path.

    Parameters
    ----------
    data : Any
        Data specification. Can be:
        - List/tuple: converted to numpy array
        - String: if data_file is provided, treated as column name
                  otherwise, treated as file path (.npy, .csv, .npz)
        - Other: returned as-is
    data_file : str, optional
        Path to CSV file. If provided, string `data` is treated as column name.

    Returns
    -------
    Any
        Resolved data (typically numpy array).

    Examples
    --------
    # Direct data
    >>> resolve_data([1, 2, 3])
    array([1, 2, 3])

    # CSV column
    >>> resolve_data("temperature", data_file="experiment.csv")
    array([20.5, 21.0, ...])  # from temperature column
    """
    if data is None:
        return None

    if isinstance(data, (list, tuple)):
        # Handle inhomogeneous arrays (e.g., boxplot data with different group sizes)
        try:
            return np.array(data)
        except ValueError:
            # Fallback for inhomogeneous shapes - return as list for boxplot/violin
            return list(data)

    if isinstance(data, str):
        # If data_file provided, treat string as column name
        if data_file is not None:
            return _load_csv_column(data_file, data)

        # Otherwise, treat as file path
        path = Path(data)
        if path.exists():
            if path.suffix == ".npy":
                return np.load(path)
            elif path.suffix == ".csv":
                return np.loadtxt(path, delimiter=",")
            elif path.suffix == ".npz":
                return np.load(path)

    return data


def _load_csv_column(csv_path: str, column_name: str) -> np.ndarray:
    """Load a specific column from a CSV file.

    Uses pandas if available (handles headers better), falls back to numpy.
    """
    global _csv_cache

    csv_path = str(Path(csv_path).resolve())

    # Check cache
    if csv_path not in _csv_cache:
        try:
            import pandas as pd

            _csv_cache[csv_path] = pd.read_csv(csv_path)
        except ImportError:
            # Fallback to numpy with header detection
            with open(csv_path, "r") as f:
                header = f.readline().strip().split(",")
            data = np.genfromtxt(csv_path, delimiter=",", skip_header=1)
            _csv_cache[csv_path] = {"header": header, "data": data}

    cached = _csv_cache[csv_path]

    # Extract column
    try:
        import pandas as pd

        if isinstance(cached, pd.DataFrame):
            if column_name not in cached.columns:
                raise ValueError(
                    f"Column '{column_name}' not found. Available: {list(cached.columns)}"
                )
            return cached[column_name].values
    except ImportError:
        pass

    # Numpy fallback
    if isinstance(cached, dict):
        header = cached["header"]
        data = cached["data"]
        if column_name not in header:
            raise ValueError(f"Column '{column_name}' not found. Available: {header}")
        col_idx = header.index(column_name)
        return data[:, col_idx] if data.ndim > 1 else np.array([data[col_idx]])

    raise ValueError(f"Cannot extract column from cached data type: {type(cached)}")


def clear_csv_cache() -> None:
    """Clear the CSV file cache."""
    global _csv_cache
    _csv_cache.clear()
