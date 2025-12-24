#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot categories for organized display."""

from typing import Dict, List

from ._registry import REGISTRY

# Plot categories for organized display
# Keys match directory names in demo_plotters/
_CATEGORIES_RAW: Dict[str, List[str]] = {
    "line_curve": [
        "plot",
        "step",
        "fill",
        "fill_between",
        "fill_betweenx",
        "errorbar",
        "stackplot",
        "stairs",
    ],
    "scatter_points": ["scatter"],
    "bar_categorical": ["bar", "barh"],
    "distribution": ["hist", "hist2d", "boxplot", "violinplot", "ecdf"],
    "image_matrix": ["imshow", "matshow", "pcolor", "pcolormesh", "hexbin", "spy"],
    "contour_surface": [
        "contour",
        "contourf",
        "tricontour",
        "tricontourf",
        "tripcolor",
        "triplot",
    ],
    "spectral_signal": [
        "specgram",
        "psd",
        "csd",
        "cohere",
        "angle_spectrum",
        "magnitude_spectrum",
        "phase_spectrum",
        "acorr",
        "xcorr",
    ],
    "vector_flow": ["quiver", "barbs", "streamplot"],
    "special": ["pie", "stem", "eventplot", "loglog", "semilogx", "semilogy"],
}

# Display names for categories (for UI/documentation)
CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    "line_curve": "Line & Curve",
    "scatter_points": "Scatter & Points",
    "bar_categorical": "Bar & Categorical",
    "distribution": "Distribution",
    "image_matrix": "2D Image & Matrix",
    "contour_surface": "Contour & Surface",
    "spectral_signal": "Spectral & Signal",
    "vector_flow": "Vector & Flow",
    "special": "Special",
}

# Filter categories to only include available plots
CATEGORIES: Dict[str, List[str]] = {
    cat: [p for p in plots if p in REGISTRY] for cat, plots in _CATEGORIES_RAW.items()
}
CATEGORIES = {cat: plots for cat, plots in CATEGORIES.items() if plots}

# Representative plots (one per category)
REPRESENTATIVES: Dict[str, str] = {
    "line_curve": "plot",
    "scatter_points": "scatter",
    "bar_categorical": "bar",
    "distribution": "hist",
    "image_matrix": "imshow",
    "contour_surface": "contourf",
    "spectral_signal": "specgram",
    "vector_flow": "quiver",
    "special": "pie",
}

# EOF
