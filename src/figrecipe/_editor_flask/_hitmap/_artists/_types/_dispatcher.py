#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dispatcher for plot-type-based hitmap processing.

This module provides a unified interface for processing hitmap elements
based on detected plot types. It delegates to the appropriate type-specific
processor for each plot type found on an axes.
"""

from typing import Any, Dict, Set

from ._bar import process_bar_plot, process_histogram
from ._boxplot import process_boxplot
from ._contour import process_contour
from ._event import process_eventplot
from ._fill import (
    process_fill_between,
    process_fill_betweenx,
    process_stackplot,
    process_stairs,
)
from ._heatmap import process_imshow, process_pcolormesh
from ._line import process_line_plot, process_step_plot
from ._pie import process_pie_chart
from ._quiver import process_barbs_plot, process_quiver_plot
from ._scatter import process_scatter_plot
from ._stem import process_stem_plot
from ._violin import process_violin_plot

# Mapping from plot type names to their processor functions
PLOT_TYPE_PROCESSORS = {
    # Line-based
    "plot": process_line_plot,
    "step": process_step_plot,
    # Scatter
    "scatter": process_scatter_plot,
    # Bar-based
    "bar": process_bar_plot,
    "barh": process_bar_plot,
    "hist": process_histogram,
    # Fill-based
    "fill_between": process_fill_between,
    "fill_betweenx": process_fill_betweenx,
    "stackplot": process_stackplot,
    "stairs": process_stairs,
    # Statistical
    "violinplot": process_violin_plot,
    "boxplot": process_boxplot,
    # Pie
    "pie": process_pie_chart,
    # Stem
    "stem": process_stem_plot,
    # Vector
    "quiver": process_quiver_plot,
    "barbs": process_barbs_plot,
    # Event
    "eventplot": process_eventplot,
    # Heatmap
    "pcolormesh": process_pcolormesh,
    "imshow": process_imshow,
    # Contour
    "contour": process_contour,
    "contourf": process_contour,
}

# Processing priority - some types should be processed before others
# to avoid conflicts (e.g., boxplot lines before regular lines)
PROCESSING_PRIORITY = [
    # Statistical plots first (they create internal elements)
    "boxplot",
    "violinplot",
    # Stem before regular lines
    "stem",
    # Fill types
    "fill_between",
    "fill_betweenx",
    "stackplot",
    "stairs",
    # Regular plots
    "step",
    "plot",
    "scatter",
    # Bar-based
    "bar",
    "barh",
    "hist",
    # Vector
    "quiver",
    "barbs",
    # Event
    "eventplot",
    # Pie
    "pie",
    # Heatmap/contour
    "pcolormesh",
    "imshow",
    "contour",
    "contourf",
]


def process_by_plot_types(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process hitmap elements using type-based processors.

    This function dispatches to the appropriate processor for each
    detected plot type on the axes.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to process
    ax_idx : int
        Axes index
    element_id : int
        Starting element ID
    original_props : dict
        Dict to store original properties for restoration
    color_map : dict
        Dict to store element color mappings
    ax_info : dict
        Plot type information for this axes

    Returns
    -------
    int
        Updated element ID after processing all types
    """
    detected_types = ax_info.get("types", set())

    # Process types in priority order
    processed_types: Set[str] = set()

    for plot_type in PROCESSING_PRIORITY:
        if plot_type in detected_types and plot_type not in processed_types:
            processor = PLOT_TYPE_PROCESSORS.get(plot_type)
            if processor:
                element_id = processor(
                    ax, ax_idx, element_id, original_props, color_map, ax_info
                )
                processed_types.add(plot_type)

    # Process any remaining types not in priority list
    for plot_type in detected_types:
        if plot_type not in processed_types:
            processor = PLOT_TYPE_PROCESSORS.get(plot_type)
            if processor:
                element_id = processor(
                    ax, ax_idx, element_id, original_props, color_map, ax_info
                )
                processed_types.add(plot_type)

    return element_id


def get_processor_for_type(plot_type: str):
    """Get the processor function for a specific plot type.

    Parameters
    ----------
    plot_type : str
        Plot type name

    Returns
    -------
    callable or None
        Processor function, or None if not found
    """
    return PLOT_TYPE_PROCESSORS.get(plot_type)


def list_supported_types() -> list:
    """List all supported plot types.

    Returns
    -------
    list
        List of supported plot type names
    """
    return list(PLOT_TYPE_PROCESSORS.keys())


__all__ = [
    "process_by_plot_types",
    "get_processor_for_type",
    "list_supported_types",
    "PLOT_TYPE_PROCESSORS",
    "PROCESSING_PRIORITY",
]

# EOF
