#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP fr_* tools: figrecipe-branded scientific plot methods.

Delegates to three sub-modules:
  _scitex_shaded  — fr_line, fr_shaded_line, fr_mean_std, fr_mean_ci, fr_median_iqr
  _scitex_stats   — fr_conf_mat, fr_ecdf, fr_raster, fr_scatter_hist
  _scitex_vis     — fr_heatmap, fr_fillv, fr_rectangle, fr_image, fr_violin
"""


from . import _scitex_shaded, _scitex_stats, _scitex_vis


def register(mcp) -> None:  # noqa: ANN001
    """Register all fr_* scientific plot tools on *mcp*."""
    _scitex_shaded.register(mcp)
    _scitex_stats.register(mcp)
    _scitex_vis.register(mcp)


# EOF
