#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style management for figrecipe.

Provides style loading, application, and management for publication-quality figures.

Usage:
    from figrecipe.styles import load_style, STYLE

    # Load default style
    style = load_style()

    # Access style parameters
    print(style.axes.width_mm)
    print(style.fonts.axis_label_pt)

    # Use with subplots
    fig, ax = ps.subplots(**style.to_subplots_kwargs())
"""

from ._color_resolver import (
    get_color_map,
    resolve_color,
    resolve_colors_in_kwargs,
)
from ._dotdict import DotDict
from ._finalize import finalize_special_plots, finalize_ticks
from ._fonts import check_font, list_available_fonts
from ._plot_styling import (
    style_barplot,
    style_boxplot,
    style_errorbar,
    style_scatter,
    style_violinplot,
)
from ._style_applier import apply_style_mm
from ._style_loader import (
    STYLE,
    get_style,
    list_presets,
    load_style,
    reload_style,
    to_subplots_kwargs,
    unload_style,
)
from ._themes import apply_theme_colors

# Axis helper utilities
from .axis_helpers import (
    OOMFormatter,
    extend,
    force_aspect,
    hide_spines,
    map_ticks,
    rotate_labels,
    sci_note,
    set_n_ticks,
    set_ticks,
    set_x_ticks,
    set_y_ticks,
    show_all_spines,
    show_classic_spines,
    show_spines,
    toggle_spines,
)

# Also expose styler classes and additional functions
from .plot_stylers import (
    BarplotStyler,
    BoxplotStyler,
    ErrorbarStyler,
    HeatmapStyler,
    HistogramStyler,
    ImshowStyler,
    LineStyler,
    PieStyler,
    PlotStyler,
    ScatterStyler,
    ViolinplotStyler,
    mm_to_pt,
    style_heatmap,
    style_histogram,
    style_imshow,
    style_line,
    style_pie,
)

__all__ = [
    "DotDict",
    "load_style",
    "unload_style",
    "get_style",
    "reload_style",
    "list_presets",
    "STYLE",
    "to_subplots_kwargs",
    "apply_style_mm",
    "apply_theme_colors",
    "check_font",
    "list_available_fonts",
    "finalize_ticks",
    "finalize_special_plots",
    "resolve_color",
    "resolve_colors_in_kwargs",
    "get_color_map",
    # Plot styling utilities (convenience functions)
    "style_boxplot",
    "style_violinplot",
    "style_barplot",
    "style_scatter",
    "style_errorbar",
    "style_pie",
    "style_imshow",
    "style_line",
    "style_histogram",
    "style_heatmap",
    # Styler classes
    "PlotStyler",
    "BoxplotStyler",
    "ViolinplotStyler",
    "BarplotStyler",
    "ScatterStyler",
    "ErrorbarStyler",
    "PieStyler",
    "ImshowStyler",
    "LineStyler",
    "HistogramStyler",
    "HeatmapStyler",
    # Unit conversion
    "mm_to_pt",
    # Axis helper utilities
    "rotate_labels",
    "hide_spines",
    "show_spines",
    "show_all_spines",
    "show_classic_spines",
    "toggle_spines",
    "set_n_ticks",
    "set_ticks",
    "set_x_ticks",
    "set_y_ticks",
    "map_ticks",
    "OOMFormatter",
    "sci_note",
    "force_aspect",
    "extend",
]
