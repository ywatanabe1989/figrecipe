#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Call-specific override application for element properties.

This is the SINGLE SOURCE OF TRUTH for applying element-level changes.
Both initial render and re-render use this same function through apply_overrides().
"""

from typing import Any, Dict

from matplotlib.figure import Figure


def apply_call_overrides(
    fig: Figure, call_overrides: Dict[str, Dict[str, Any]], record: Any
) -> None:
    """Apply call-specific overrides to figure elements.

    Parameters
    ----------
    fig : Figure
        Matplotlib figure.
    call_overrides : dict
        Mapping from call_id to {param: value} overrides.
    record : FigureRecord
        Recording record to find call metadata.
    """
    from matplotlib.patches import Wedge

    axes_list = fig.get_axes()

    # Build mapping from ax_key to axes index
    # ax_keys are in format "ax_{row}_{col}", need to map to actual axes indices
    ax_keys_sorted = sorted(record.axes.keys())
    ax_key_to_index = {key: idx for idx, key in enumerate(ax_keys_sorted)}

    for call_id, params in call_overrides.items():
        # Find the call in record to get function type, ax_index, and call position
        call_function = None
        ax_index = None
        ax_record_found = None
        for ax_key, ax_record in record.axes.items():
            for call in ax_record.calls:
                if call.id == call_id:
                    call_function = call.function
                    ax_record_found = ax_record
                    # Use sorted key order to get correct axes index
                    ax_index = ax_key_to_index.get(ax_key, 0)
                    break
            if call_function:
                break

        if call_function is None or ax_index is None or ax_index >= len(axes_list):
            continue

        ax = axes_list[ax_index]

        # Apply overrides based on plot type
        for param, value in params.items():
            if call_function in ("bar", "barh", "hist"):
                # Bar/hist creates multiple patches per call - apply to ALL
                _apply_bar_override(ax, ax_record_found, call_id, param, value)
            elif call_function == "plot":
                _apply_line_override(ax, ax_record_found, call_id, param, value)
            elif call_function == "scatter":
                _apply_scatter_override(ax, ax_record_found, call_id, param, value)
            elif call_function == "pie":
                # Pie wedges - apply to all wedges for this call
                wedges = [p for p in ax.patches if isinstance(p, Wedge)]
                for wedge in wedges:
                    _apply_patch_param(wedge, param, value)
            elif call_function in ("fill_between", "fill_betweenx"):
                _apply_fill_override(ax, ax_record_found, call_id, param, value)


def _apply_bar_override(ax, ax_record, call_id, param, value):
    """Apply override to bar/hist patches for a specific call."""
    from matplotlib.patches import Rectangle

    rectangles = [p for p in ax.patches if isinstance(p, Rectangle)]
    if not rectangles:
        return

    # Find all bar/hist calls to determine grouping
    bar_calls = [c for c in ax_record.calls if c.function in ("bar", "barh", "hist")]
    if not bar_calls:
        return

    # Find which call index this is
    call_idx = next((i for i, c in enumerate(bar_calls) if c.id == call_id), None)
    if call_idx is None:
        return

    # Distribute patches among calls
    patches_per_call = len(rectangles) // len(bar_calls) if bar_calls else 1
    start_idx = call_idx * patches_per_call
    end_idx = start_idx + patches_per_call

    # Apply to all patches for this call
    for patch in rectangles[start_idx:end_idx]:
        _apply_patch_param(patch, param, value)


def _apply_line_override(ax, ax_record, call_id, param, value):
    """Apply override to line for a specific call."""
    lines = [line for line in ax.get_lines() if not line.get_label().startswith("_")]
    line_calls = [c for c in ax_record.calls if c.function == "plot"]

    call_idx = next((i for i, c in enumerate(line_calls) if c.id == call_id), None)
    if call_idx is not None and call_idx < len(lines):
        _apply_line_param(lines[call_idx], param, value)


def _apply_scatter_override(ax, ax_record, call_id, param, value):
    """Apply override to scatter collection for a specific call."""
    from matplotlib.collections import PathCollection

    collections = [c for c in ax.collections if isinstance(c, PathCollection)]
    scatter_calls = [c for c in ax_record.calls if c.function == "scatter"]

    call_idx = next((i for i, c in enumerate(scatter_calls) if c.id == call_id), None)
    if call_idx is not None and call_idx < len(collections):
        _apply_collection_param(collections[call_idx], param, value)


def _apply_fill_override(ax, ax_record, call_id, param, value):
    """Apply override to fill_between for a specific call."""
    from matplotlib.collections import PolyCollection

    fills = [c for c in ax.collections if isinstance(c, PolyCollection)]
    fill_calls = [
        c for c in ax_record.calls if c.function in ("fill_between", "fill_betweenx")
    ]

    call_idx = next((i for i, c in enumerate(fill_calls) if c.id == call_id), None)
    if call_idx is not None and call_idx < len(fills):
        _apply_collection_param(fills[call_idx], param, value)


def _apply_patch_param(patch: Any, param: str, value: Any) -> None:
    """Apply parameter to a patch (bar, wedge, etc.)."""
    if param == "color":
        patch.set_facecolor(value)
    elif param == "edgecolor":
        patch.set_edgecolor(value)
    elif param == "linewidth":
        patch.set_linewidth(value)
    elif param == "alpha":
        patch.set_alpha(value)


def _apply_line_param(line: Any, param: str, value: Any) -> None:
    """Apply parameter to a line."""
    if param == "color":
        line.set_color(value)
    elif param == "linewidth":
        line.set_linewidth(value)
    elif param == "linestyle":
        line.set_linestyle(value)
    elif param == "alpha":
        line.set_alpha(value)
    elif param == "marker":
        line.set_marker(value)
    elif param == "markersize":
        line.set_markersize(value)


def _apply_collection_param(coll: Any, param: str, value: Any) -> None:
    """Apply parameter to a collection (scatter, fill)."""
    if param in ("color", "c"):
        coll.set_facecolors(value)
    elif param == "edgecolor":
        coll.set_edgecolors(value)
    elif param == "s":
        coll.set_sizes([value] if not hasattr(value, "__len__") else value)
    elif param == "alpha":
        coll.set_alpha(value)


__all__ = ["apply_call_overrides"]

# EOF
