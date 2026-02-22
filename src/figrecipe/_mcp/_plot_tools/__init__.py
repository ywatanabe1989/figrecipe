#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Explicit per-method MCP plot tools — one tool per matplotlib method.

Registers ~50 typed tools on the MCP server covering all matplotlib Axes
plotting methods:
  plt_line, plt_scatter, plt_errorbar,
  plt_bar, plt_barh,
  plt_boxplot, plt_violinplot,
  plt_pie, plt_hist, plt_fill_between,
  plt_imshow, plt_contourf,
  plt_step, plt_stem, plt_hexbin, plt_eventplot, plt_stackplot,
  plt_specgram, plt_psd,
  plt_fill, plt_fill_betweenx, plt_contour, plt_pcolormesh,
  plt_hist2d, plt_matshow,
  plt_loglog, plt_semilogx, plt_semilogy, plt_quiver,
  plt_acorr, plt_xcorr, plt_spy,
  plt_csd, plt_cohere, plt_angle_spectrum, plt_magnitude_spectrum,
  plt_phase_spectrum,
  plt_streamplot, plt_stairs, plt_ecdf, plt_pcolor

Each tool:
- Accepts typed data params (no spec guessing)
- Accepts figure size, decoration, caption params
- Accepts stat_annotations (manual) OR stats_results (scitex.stats dicts)
- Internally delegates to create_figure_from_spec for recipe/reproduce support
"""


__all__ = ["register_plot_tools"]

from . import (
    _advanced,
    _area2,
    _bar,
    _box,
    _image,
    _line_scatter,
    _log,
    _pie_hist,
    _scitex,
    _special,
    _spectral,
    _spectral2,
    _vector_corr,
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
    _area2.register(mcp)
    _log.register(mcp)
    _vector_corr.register(mcp)
    _spectral2.register(mcp)
    _advanced.register(mcp)
    _scitex.register(mcp)


# EOF
