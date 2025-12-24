#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot type detection utilities for hitmap generation."""

from typing import Any, Dict


def detect_plot_types(fig) -> Dict[int, Dict[str, Any]]:
    """Detect plot types from recorded calls in figure.

    Parameters
    ----------
    fig : Figure
        The figure to analyze.

    Returns
    -------
    dict
        Mapping from ax_index to plot type info.
    """
    # Get figure record if available
    if hasattr(fig, "record"):
        record = fig.record
    elif hasattr(fig, "fig") and hasattr(fig.fig, "_record"):
        record = fig.fig._record
    else:
        return {}

    result = {}

    # Process each axes in the record
    if hasattr(record, "axes"):
        # First pass: collect all ax_keys to determine grid dimensions
        ax_keys = list(record.axes.keys())
        max_row, max_col = 0, 0
        for ax_key in ax_keys:
            try:
                parts = ax_key.split("_")
                row, col = int(parts[1]), int(parts[2])
                max_row = max(max_row, row)
                max_col = max(max_col, col)
            except (ValueError, IndexError):
                pass
        ncols = max_col + 1

        for ax_key, ax_record in record.axes.items():
            # Extract ax_index from key (e.g., "ax_0_0" -> 0, "ax_2_2" -> 8 for 3x3)
            try:
                parts = ax_key.split("_")
                row, col = int(parts[1]), int(parts[2])
                ax_idx = row * ncols + col
            except (ValueError, IndexError):
                ax_idx = 0

            if ax_idx not in result:
                result[ax_idx] = {"types": set(), "call_ids": {}}

            # Collect all call types and their IDs
            if hasattr(ax_record, "calls"):
                for call in ax_record.calls:
                    func_name = call.function
                    call_id = call.id

                    result[ax_idx]["types"].add(func_name)

                    if func_name not in result[ax_idx]["call_ids"]:
                        result[ax_idx]["call_ids"][func_name] = []
                    result[ax_idx]["call_ids"][func_name].append(call_id)

    return result


def is_boxplot_element(line, ax) -> bool:
    """Check if a line element belongs to a boxplot.

    Parameters
    ----------
    line : Line2D
        The line to check.
    ax : Axes
        The axes containing the line.

    Returns
    -------
    bool
        True if line is a boxplot element.
    """
    label = line.get_label() or ""

    # Boxplot whisker/median lines have specific patterns
    if label.startswith("_line"):
        return True

    # Check if line is horizontal (median) or vertical (whisker)
    xdata = line.get_xdata()
    ydata = line.get_ydata()

    if len(xdata) == 2 and len(ydata) == 2:
        # Horizontal or vertical line segments
        is_horizontal = ydata[0] == ydata[1]
        is_vertical = xdata[0] == xdata[1]
        if is_horizontal or is_vertical:
            return True

    return False


def is_violin_element(coll, ax) -> bool:
    """Check if a collection element belongs to a violin plot.

    Parameters
    ----------
    coll : Collection
        The collection to check.
    ax : Axes
        The axes containing the collection.

    Returns
    -------
    bool
        True if collection is a violin element.
    """
    from matplotlib.collections import PolyCollection

    if isinstance(coll, PolyCollection):
        # Violin bodies are PolyCollections
        return True
    return False


__all__ = [
    "detect_plot_types",
    "is_boxplot_element",
    "is_violin_element",
]

# EOF
