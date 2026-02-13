#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KDE-extended violin plot rendering.

Computes KDE manually with extended range so tails converge smoothly
to zero, unlike matplotlib's native violinplot which clips at data
min/max.
"""

from typing import Any, Dict, List, Optional

import numpy as np


def draw_kde_violins(
    ax,
    dataset: List,
    positions: List,
    colors: Optional[List] = None,
    violin_style: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Draw violin bodies using manual KDE with extended tails.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    dataset : list of array-like
        Data arrays for each violin.
    positions : list of float
        X positions for each violin.
    colors : list, optional
        Colors for each violin body.
    violin_style : dict, optional
        Style configuration with keys like ``alpha``, ``kde_half_width``,
        ``line_mm``.

    Returns
    -------
    dict
        Result dict with ``bodies`` key (empty list, since bodies are
        drawn via fill_betweenx rather than matplotlib PolyCollection).
    """
    import matplotlib.pyplot as mpl_plt
    from scipy.stats import gaussian_kde

    from ..styles._style_applier import mm_to_pt

    if violin_style is None:
        violin_style = {}

    alpha = violin_style.get("alpha", 0.4)
    half_width = violin_style.get("kde_half_width", 0.15)
    edge_lw = mm_to_pt(violin_style.get("line_mm", 0.2))

    if colors is None:
        colors = mpl_plt.rcParams["axes.prop_cycle"].by_key()["color"]

    all_y_min, all_y_max = np.inf, -np.inf

    for i, (vals, pos) in enumerate(zip(dataset, positions)):
        vals = np.asarray(vals, dtype=float)
        color = colors[i % len(colors)]

        kde = gaussian_kde(vals)
        data_min, data_max = vals.min(), vals.max()
        data_range = data_max - data_min
        pad = max(data_range * 0.3, kde.factor * np.std(vals) * 3)
        y_eval = np.linspace(data_min - pad, data_max + pad, 500)
        density = kde(y_eval)
        density_scaled = density / density.max() * half_width

        ax.fill_betweenx(
            y_eval,
            pos - density_scaled,
            pos + density_scaled,
            facecolor=color,
            edgecolor="black",
            linewidth=edge_lw,
            alpha=alpha,
            zorder=1,
        )

        all_y_min = min(all_y_min, y_eval[0])
        all_y_max = max(all_y_max, y_eval[-1])

    # Extend y-axis to show full tails
    y_margin = (all_y_max - all_y_min) * 0.05
    ax.set_ylim(all_y_min - y_margin, all_y_max + y_margin)

    # Apply SCITEX tick styling from global ticks config
    import matplotlib.ticker

    from ..styles._internal import get_style

    full_style = get_style()
    ticks_style = full_style.get("ticks", {}) if full_style else {}
    n_ticks = ticks_style.get("n_ticks_max", 4)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(n_ticks))

    return {"bodies": []}


__all__ = ["draw_kde_violins"]

# EOF
