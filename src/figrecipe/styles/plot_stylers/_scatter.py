#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scatter plot styler for publication-quality scatter plots."""

__all__ = ["ScatterStyler", "style_scatter"]

from typing import Any, Optional

from ._base import PlotStyler, mm_to_pt


class ScatterStyler(PlotStyler):
    """Styler for matplotlib scatter plot elements.

    Applies consistent marker sizes and edge widths to scatter plots
    for publication-quality figures.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> scatter = ax.scatter([1, 2, 3], [4, 5, 6])
    >>> styler = ScatterStyler()
    >>> styler.apply(scatter)
    """

    style_section = "scatter"

    def apply(
        self,
        scatter: Any,
        size_mm: Optional[float] = None,
        edge_thickness_mm: Optional[float] = None,
        edgecolor: Optional[str] = None,
    ) -> Any:
        """Apply styling to a scatter plot.

        Parameters
        ----------
        scatter : PathCollection
            Collection returned by ax.scatter().
        size_mm : float, optional
            Marker size in mm. Default from style.
        edge_thickness_mm : float, optional
            Edge line width in mm. Default from style.
        edgecolor : str, optional
            Edge color. If None, uses "black".

        Returns
        -------
        PathCollection
            The styled scatter collection.
        """
        # Get parameters with defaults from style
        if size_mm is None:
            size_mm = self.get_param("size_mm", 1.0)
        if edge_thickness_mm is None:
            edge_thickness_mm = self.get_param("edge_mm", 0.2)

        # Convert mm to points
        size_pt = mm_to_pt(size_mm)
        lw_pt = mm_to_pt(edge_thickness_mm)

        # Matplotlib scatter size is in points^2
        scatter.set_sizes([size_pt**2])
        scatter.set_linewidths([lw_pt])

        if edgecolor is not None:
            scatter.set_edgecolors([edgecolor])

        return scatter


# Convenience function
def style_scatter(
    scatter: Any,
    size_mm: Optional[float] = None,
    edge_thickness_mm: Optional[float] = None,
    edgecolor: Optional[str] = None,
    style: Any = None,
) -> Any:
    """Apply publication-quality styling to a scatter plot.

    This is a convenience function that creates a ScatterStyler and applies it.

    Parameters
    ----------
    scatter : PathCollection
        Collection returned by ax.scatter().
    size_mm : float, optional
        Marker size in mm. Default: from style (1.0).
    edge_thickness_mm : float, optional
        Edge line width in mm. Default: from style (0.2).
    edgecolor : str, optional
        Edge color. Default: "black".
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    PathCollection
        The styled scatter collection.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> scatter = ax.scatter([1, 2, 3], [4, 5, 6])
    >>> fr.style_scatter(scatter)
    """
    styler = ScatterStyler(style=style)
    return styler.apply(
        scatter,
        size_mm=size_mm,
        edge_thickness_mm=edge_thickness_mm,
        edgecolor=edgecolor,
    )


# EOF
