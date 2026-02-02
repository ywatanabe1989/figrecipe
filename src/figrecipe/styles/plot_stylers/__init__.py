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
# Core stylers
from ._barplot import BarplotStyler, style_barplot
from ._base import PlotStyler, mm_to_pt
from ._boxplot import BoxplotStyler, style_boxplot
from ._errorbar import ErrorbarStyler, style_errorbar
from ._heatmap import HeatmapStyler, style_heatmap
from ._histogram import HistogramStyler, style_histogram
from ._imshow import ImshowStyler, style_imshow
from ._line import LineStyler, style_line
from ._pie import PieStyler, style_pie
from ._scatter import ScatterStyler, style_scatter
from ._violinplot import ViolinplotStyler, style_violinplot

# Note: This module is primarily for internal use.
# User-facing styling is handled automatically by figrecipe.
# Direct access to stylers is rarely needed by end users.
__all__ = [
    # Base class
    "PlotStyler",
    "mm_to_pt",
    # Styler classes
    "BarplotStyler",
    "BoxplotStyler",
    "ErrorbarStyler",
    "HeatmapStyler",
    "HistogramStyler",
    "ImshowStyler",
    "LineStyler",
    "PieStyler",
    "ScatterStyler",
    "ViolinplotStyler",
    # Styling functions
    "style_barplot",
    "style_boxplot",
    "style_errorbar",
    "style_heatmap",
    "style_histogram",
    "style_imshow",
    "style_line",
    "style_pie",
    "style_scatter",
    "style_violinplot",
]


# EOF
