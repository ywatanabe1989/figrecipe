#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ruff: noqa: F401 - Re-exports are intentional
"""Internal re-exports for figrecipe internal use only.

This module provides internal APIs that are used by other figrecipe modules
but should NOT be exposed to end users. Import from here for internal code.

Usage (internal only):
    from ..styles._internal import get_style, resolve_colors_in_kwargs
"""

# Color resolution (internal)
from ._color_resolver import get_color_map as get_color_map
from ._color_resolver import resolve_color as resolve_color
from ._color_resolver import resolve_colors_in_kwargs as resolve_colors_in_kwargs

# DotDict utility (internal)
from ._dotdict import DotDict as DotDict

# Finalization hooks (internal)
from ._finalize import finalize_special_plots as finalize_special_plots
from ._finalize import finalize_ticks as finalize_ticks

# Plot styling functions (internal)
from ._plot_styling import style_barplot as style_barplot
from ._plot_styling import style_boxplot as style_boxplot
from ._plot_styling import style_errorbar as style_errorbar
from ._plot_styling import style_scatter as style_scatter
from ._plot_styling import style_violinplot as style_violinplot

# Style application (internal)
from ._style_applier import apply_style_mm as apply_style_mm
from ._style_loader import STYLE as STYLE

# Style loading internals (internal)
from ._style_loader import get_style as get_style
from ._style_loader import reload_style as reload_style
from ._style_loader import to_subplots_kwargs as to_subplots_kwargs

# Theme colors (internal)
from ._themes import apply_theme_colors as apply_theme_colors

# Plot stylers (internal)
from .plot_stylers import BarplotStyler as BarplotStyler
from .plot_stylers import BoxplotStyler as BoxplotStyler
from .plot_stylers import ErrorbarStyler as ErrorbarStyler
from .plot_stylers import HeatmapStyler as HeatmapStyler
from .plot_stylers import HistogramStyler as HistogramStyler
from .plot_stylers import ImshowStyler as ImshowStyler
from .plot_stylers import LineStyler as LineStyler
from .plot_stylers import PieStyler as PieStyler
from .plot_stylers import PlotStyler as PlotStyler
from .plot_stylers import ScatterStyler as ScatterStyler
from .plot_stylers import ViolinplotStyler as ViolinplotStyler
from .plot_stylers import mm_to_pt as mm_to_pt
from .plot_stylers import style_heatmap as style_heatmap
from .plot_stylers import style_histogram as style_histogram
from .plot_stylers import style_imshow as style_imshow
from .plot_stylers import style_line as style_line
from .plot_stylers import style_pie as style_pie

__all__ = []  # Nothing should be exported from here via import *

# EOF
