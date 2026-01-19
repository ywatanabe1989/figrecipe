#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Violin plot styler for publication-quality violin plots."""

__all__ = ["ViolinplotStyler", "style_violinplot"]

from typing import Any, List, Optional

from ._base import PlotStyler, get_color_palette, mm_to_pt


class ViolinplotStyler(PlotStyler):
    """Styler for matplotlib violin plot elements.

    Applies consistent line widths, colors, and fill styles to violin plots
    for publication-quality figures.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> fig, ax = fr.subplots()
    >>> vp = ax.violinplot([np.random.randn(100) for _ in range(3)])
    >>> styler = ViolinplotStyler()
    >>> styler.apply(ax)
    """

    style_section = "violinplot"

    def apply(
        self,
        ax: Any,
        linewidth_mm: Optional[float] = None,
        edge_color: str = "black",
        colors: Optional[List[str]] = None,
        alpha: float = 0.7,
    ) -> Any:
        """Apply styling to a violin plot via its axes.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes containing the violin plot.
        linewidth_mm : float, optional
            Line width in mm for edges. Default from style.
        edge_color : str
            Color for violin edges.
        colors : list of str, optional
            Fill colors for violins. If None, uses style palette.
        alpha : float
            Fill transparency. Default: 0.7.

        Returns
        -------
        Axes
            The styled axes.
        """
        # Get parameters with defaults from style
        if linewidth_mm is None:
            linewidth_mm = self.get_param("line_mm", 0.2)

        lw_pt = mm_to_pt(linewidth_mm)

        # Get color palette
        if colors is None:
            colors = get_color_palette(self.style)

        # Style violin bodies (PolyCollections)
        color_idx = 0
        for collection in ax.collections:
            if hasattr(collection, "set_edgecolor"):
                collection.set_edgecolor(edge_color)
            if hasattr(collection, "set_linewidth"):
                collection.set_linewidth(lw_pt)
            if hasattr(collection, "set_facecolor"):
                color = colors[color_idx % len(colors)]
                collection.set_facecolor(color)
                collection.set_alpha(alpha)
                color_idx += 1

        # Style lines (medians, means, extrema)
        for line in ax.lines:
            line.set_linewidth(lw_pt)
            line.set_color(edge_color)

        return ax


# Convenience function
def style_violinplot(
    ax: Any,
    linewidth_mm: Optional[float] = None,
    edge_color: str = "black",
    colors: Optional[List[str]] = None,
    alpha: float = 0.7,
    style: Any = None,
) -> Any:
    """Apply publication-quality styling to a violin plot.

    This is a convenience function that creates a ViolinplotStyler and applies it.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes containing the violin plot.
    linewidth_mm : float, optional
        Line width in mm. Default: from style (0.2).
    edge_color : str
        Edge color. Default: "black".
    colors : list, optional
        Fill colors. Default: style palette.
    alpha : float
        Fill transparency. Default: 0.7.
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    Axes
        The styled axes.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.violinplot(data)
    >>> fr.style_violinplot(ax)
    """
    styler = ViolinplotStyler(style=style)
    return styler.apply(
        ax,
        linewidth_mm=linewidth_mm,
        edge_color=edge_color,
        colors=colors,
        alpha=alpha,
    )


# EOF
