#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Explicit per-method MCP plot tools — one tool per matplotlib method.

Registers 18 typed tools on the MCP server:
  plt_line, plt_scatter, plt_errorbar,
  plt_bar, plt_barh,
  plt_boxplot, plt_violinplot,
  plt_pie, plt_hist, plt_fill_between,
  plt_imshow, plt_contourf,
  plt_step, plt_stem, plt_hexbin, plt_eventplot, plt_stackplot,
  plt_specgram, plt_psd

Each tool:
- Accepts typed data params (no spec guessing)
- Accepts figure size, decoration, caption params
- Accepts stat_annotations (manual) OR stats_results (scitex.stats dicts)
- Internally delegates to create_figure_from_spec for recipe/reproduce support
"""

from __future__ import annotations

__all__ = ["register_plot_tools"]

from . import (
    _bar,
    _box,
    _image,
    _line_scatter,
    _pie_hist,
    _special,
    _spectral,
)


def register_plot_tools(mcp) -> None:  # noqa: ANN001
    """Register all explicit plotter tools on *mcp*."""
    _line_scatter.register(mcp)
    _bar.register(mcp)
    _box.register(mcp)
    _pie_hist.register(mcp)
    _image.register(mcp)
    _special.register(mcp)
    _spectral.register(mcp)


# EOF
