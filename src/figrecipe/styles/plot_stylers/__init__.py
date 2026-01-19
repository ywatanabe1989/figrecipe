#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot stylers for publication-quality matplotlib figures.

This module provides dedicated styler classes and convenience functions
for applying consistent styling to various matplotlib plot types.

Usage:
    from figrecipe.styles.plot_stylers import style_boxplot, BoxplotStyler

    # Convenience function
    fr.style_boxplot(bp)

    # Or use the styler class directly
    styler = BoxplotStyler()
    styler.apply(bp)

Stylers follow a consistent pattern:
    - Each plot type has a Styler class inheriting from PlotStyler
    - Each has a convenience function (e.g., style_boxplot)
    - All accept style configuration and override parameters
    - All return the styled object for chaining
"""

# Base class and utilities
# Core stylers (actively used)
from ._barplot import BarplotStyler, style_barplot
from ._base import (
    PlotStyler,
    get_color_palette,
    get_style_value,
    mm_to_pt,
)
from ._boxplot import BoxplotStyler, style_boxplot
from ._errorbar import ErrorbarStyler, style_errorbar

# Placeholder stylers (for future expansion)
from ._heatmap import HeatmapStyler, style_heatmap
from ._histogram import HistogramStyler, style_histogram
from ._imshow import ImshowStyler, style_imshow
from ._line import LineStyler, style_line
from ._pie import PieStyler, style_pie
from ._scatter import ScatterStyler, style_scatter
from ._violinplot import ViolinplotStyler, style_violinplot

__all__ = [
    # Base
    "PlotStyler",
    "mm_to_pt",
    "get_style_value",
    "get_color_palette",
    # Core stylers
    "BoxplotStyler",
    "style_boxplot",
    "ViolinplotStyler",
    "style_violinplot",
    "BarplotStyler",
    "style_barplot",
    "ScatterStyler",
    "style_scatter",
    "ErrorbarStyler",
    "style_errorbar",
    "PieStyler",
    "style_pie",
    "ImshowStyler",
    "style_imshow",
    # Placeholder stylers
    "LineStyler",
    "style_line",
    "HistogramStyler",
    "style_histogram",
    "HeatmapStyler",
    "style_heatmap",
]


# EOF
