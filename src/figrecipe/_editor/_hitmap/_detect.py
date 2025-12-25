#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot type detection utilities for hitmap generation."""

from typing import Any, Dict


def detect_plot_types(fig, debug: bool = False) -> Dict[int, Dict[str, Any]]:
    """Detect plot types from recorded calls in figure.

    Parameters
    ----------
    fig : Figure
        The figure to analyze.
    debug : bool
        If True, print debug information.

    Returns
    -------
    dict
        Mapping from ax_index (matching fig.get_axes() order) to plot type info.
    """
    # Get figure record if available
    if hasattr(fig, "record"):
        record = fig.record
    elif hasattr(fig, "fig") and hasattr(fig.fig, "_record"):
        record = fig.fig._record
    else:
        if debug:
            print("[detect_plot_types] No record found")
        return {}

    # Get the actual matplotlib figure and its axes
    mpl_fig = fig.fig if hasattr(fig, "fig") else fig
    axes_list = mpl_fig.get_axes()

    result = {}

    # Process each axes in the record
    if hasattr(record, "axes"):
        # Build mapping from ax_key to ax_record's plot info
        ax_key_to_info = {}
        for ax_key, ax_record in record.axes.items():
            info = {"types": set(), "call_ids": {}}

            if hasattr(ax_record, "calls"):
                for call in ax_record.calls:
                    func_name = call.function
                    call_id = call.id

                    info["types"].add(func_name)

                    if func_name not in info["call_ids"]:
                        info["call_ids"][func_name] = []
                    info["call_ids"][func_name].append(call_id)

            ax_key_to_info[ax_key] = info

        # Map ax_keys to current axes positions using position matching
        # This handles the case where panels have been dragged to new positions
        ax_keys_sorted = sorted(record.axes.keys())

        # Debug: Check which ax_keys have position_override
        overrides = {
            k: getattr(record.axes[k], "position_override", None)
            for k in ax_keys_sorted
            if hasattr(record.axes[k], "position_override")
            and record.axes[k].position_override
        }
        if overrides:
            print(f"[detect_plot_types] Position overrides: {overrides}")

        for ax_idx, ax in enumerate(axes_list):
            # Try to find the matching ax_record by comparing positions
            # or fall back to index-based matching
            matched = False
            ax_pos = ax.get_position()

            for ax_key in ax_keys_sorted:
                ax_record = record.axes[ax_key]
                # Check if there's a position_override that matches
                # Must check ALL 4 coordinates to avoid false matches
                if (
                    hasattr(ax_record, "position_override")
                    and ax_record.position_override
                ):
                    rec_pos = ax_record.position_override
                    # Position override is [x0, y0, width, height]
                    if len(rec_pos) >= 4:
                        if (
                            abs(rec_pos[0] - ax_pos.x0) < 0.01
                            and abs(rec_pos[1] - ax_pos.y0) < 0.01
                            and abs(rec_pos[2] - ax_pos.width) < 0.01
                            and abs(rec_pos[3] - ax_pos.height) < 0.01
                        ):
                            print(
                                f"[detect_plot_types] ax_idx={ax_idx} matched {ax_key} "
                                f"via position_override"
                            )
                            result[ax_idx] = ax_key_to_info.get(
                                ax_key, {"types": set(), "call_ids": {}}
                            )
                            matched = True
                            break
                    else:
                        # Fallback for old format with only x0, y0
                        if (
                            abs(rec_pos[0] - ax_pos.x0) < 0.01
                            and abs(rec_pos[1] - ax_pos.y0) < 0.01
                        ):
                            result[ax_idx] = ax_key_to_info.get(
                                ax_key, {"types": set(), "call_ids": {}}
                            )
                            matched = True
                            break

            # Fall back to index-based matching if position match failed
            if not matched and ax_idx < len(ax_keys_sorted):
                ax_key = ax_keys_sorted[ax_idx]
                info = ax_key_to_info.get(ax_key, {"types": set(), "call_ids": {}})
                print(
                    f"[detect_plot_types] ax_idx={ax_idx} fallback to {ax_key}, "
                    f"types={info.get('types', set())}"
                )
                result[ax_idx] = info

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
