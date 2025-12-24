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

from ._dotdict import DotDict
from ._finalize import finalize_special_plots, finalize_ticks
from ._fonts import check_font, list_available_fonts
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
]
