#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style management for plotspec.

Provides style loading, application, and management for publication-quality figures.

Usage:
    from plotspec.styles import load_style, STYLE

    # Load default style
    style = load_style()

    # Access style parameters
    print(style.axes.width_mm)
    print(style.fonts.axis_label_pt)

    # Use with subplots
    fig, ax = ps.subplots(**style.to_subplots_kwargs())
"""

from ._style_loader import (
    load_style,
    get_style,
    reload_style,
    STYLE,
    to_subplots_kwargs,
)

from ._style_applier import apply_style_mm, apply_theme_colors

__all__ = [
    "load_style",
    "get_style",
    "reload_style",
    "STYLE",
    "to_subplots_kwargs",
    "apply_style_mm",
    "apply_theme_colors",
]
