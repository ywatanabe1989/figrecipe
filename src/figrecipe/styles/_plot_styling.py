#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Plot styling utilities - re-exports from plot_stylers module.

This module provides backward compatibility by re-exporting from the
organized plot_stylers/ directory structure.

For new code, prefer importing directly from plot_stylers:
    from figrecipe.styles.plot_stylers import style_boxplot, BoxplotStyler

Functions:
    style_boxplot: Style boxplot elements
    style_violinplot: Style violin plot elements
    style_barplot: Style bar plot elements
    style_scatter: Style scatter plot elements
    style_errorbar: Style error bar elements
"""

# Re-export from new organized module structure
from .plot_stylers import (
    style_barplot,
    style_boxplot,
    style_errorbar,
    style_scatter,
    style_violinplot,
)

__all__ = [
    "style_boxplot",
    "style_violinplot",
    "style_barplot",
    "style_scatter",
    "style_errorbar",
]


# EOF
