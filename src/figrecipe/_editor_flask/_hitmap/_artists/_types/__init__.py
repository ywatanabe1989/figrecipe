#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot-type-specific hitmap processing modules.

This package organizes hitmap generation by plot type for maintainability.
Each module handles a specific plot type or family of related plot types.

Structure:
- _base.py: Shared utilities (id_to_rgb, normalize_color, etc.)
- _line.py: plot, step, semilogx, semilogy, loglog
- _scatter.py: scatter
- _bar.py: bar, barh, hist
- _fill.py: fill_between, fill_betweenx, stackplot, stairs
- _violin.py: violinplot
- _boxplot.py: boxplot
- _pie.py: pie
- _stem.py: stem
- _quiver.py: quiver, barbs
- _event.py: eventplot
- _heatmap.py: pcolormesh, imshow, hexbin
- _contour.py: contour, contourf
"""

# Base utilities
# Bar-based plots
from ._bar import process_bar_plot, process_histogram
from ._base import (
    apply_hitmap_color,
    get_call_ids,
    has_plot_type,
    id_to_rgb,
    mpl_color_to_hex,
    normalize_color,
    register_element,
)
from ._boxplot import process_boxplot

# Contour plots
from ._contour import process_contour

# Dispatcher
from ._dispatcher import (
    PLOT_TYPE_PROCESSORS,
    PROCESSING_PRIORITY,
    get_processor_for_type,
    list_supported_types,
    process_by_plot_types,
)

# Event plots
from ._event import process_eventplot

# Fill-based plots
from ._fill import (
    process_fill_between,
    process_fill_betweenx,
    process_stackplot,
    process_stairs,
)

# Heatmap/mesh plots
from ._heatmap import process_imshow, process_pcolormesh

# Line-based plots
from ._line import process_line_plot, process_step_plot

# Pie charts
from ._pie import process_pie_chart

# Vector plots
from ._quiver import process_barbs_plot, process_quiver_plot

# Scatter plots
from ._scatter import process_scatter_plot

# Stem plots
from ._stem import process_stem_plot

# Statistical plots
from ._violin import process_violin_plot

__all__ = [
    # Base utilities
    "register_element",
    "apply_hitmap_color",
    "get_call_ids",
    "has_plot_type",
    "id_to_rgb",
    "normalize_color",
    "mpl_color_to_hex",
    # Line-based
    "process_line_plot",
    "process_step_plot",
    # Scatter
    "process_scatter_plot",
    # Bar-based
    "process_bar_plot",
    "process_histogram",
    # Fill-based
    "process_fill_between",
    "process_fill_betweenx",
    "process_stackplot",
    "process_stairs",
    # Statistical
    "process_violin_plot",
    "process_boxplot",
    # Pie
    "process_pie_chart",
    # Stem
    "process_stem_plot",
    # Vector
    "process_quiver_plot",
    "process_barbs_plot",
    # Event
    "process_eventplot",
    # Heatmap
    "process_pcolormesh",
    "process_imshow",
    # Contour
    "process_contour",
    # Dispatcher
    "process_by_plot_types",
    "get_processor_for_type",
    "list_supported_types",
    "PLOT_TYPE_PROCESSORS",
    "PROCESSING_PRIORITY",
]

# EOF
