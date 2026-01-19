#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bar plot styler for publication-quality bar plots."""

__all__ = ["BarplotStyler", "style_barplot"]

from typing import Any, List, Optional, Union

from ._base import PlotStyler, mm_to_pt


class BarplotStyler(PlotStyler):
    """Styler for matplotlib bar plot elements.

    Applies consistent edge widths and colors to bar plots
    for publication-quality figures.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> bars = ax.bar([1, 2, 3], [4, 5, 6])
    >>> styler = BarplotStyler()
    >>> styler.apply(bars)
    """

    style_section = "barplot"

    def apply(
        self,
        bars: Any,
        edge_thickness_mm: Optional[float] = None,
        edgecolor: Optional[Union[str, List[str]]] = None,
    ) -> Any:
        """Apply styling to a bar plot.

        Parameters
        ----------
        bars : BarContainer
            Container returned by ax.bar().
        edge_thickness_mm : float, optional
            Edge line width in mm. Default from style.
        edgecolor : str or list of str, optional
            Edge color(s) for bars. If None, uses "black".

        Returns
        -------
        BarContainer
            The styled bar container.
        """
        # Get parameters with defaults from style
        if edge_thickness_mm is None:
            edge_thickness_mm = self.get_param("edge_mm", 0.2)

        lw_pt = mm_to_pt(edge_thickness_mm)

        # Default edge color
        if edgecolor is None:
            edgecolor = "black"

        # Apply styling to each bar
        for i, bar in enumerate(bars):
            bar.set_linewidth(lw_pt)
            if isinstance(edgecolor, list):
                bar.set_edgecolor(edgecolor[i % len(edgecolor)])
            else:
                bar.set_edgecolor(edgecolor)

        return bars


# Convenience function
def style_barplot(
    bars: Any,
    edge_thickness_mm: Optional[float] = None,
    edgecolor: Optional[Union[str, List[str]]] = None,
    style: Any = None,
) -> Any:
    """Apply publication-quality styling to a bar plot.

    This is a convenience function that creates a BarplotStyler and applies it.

    Parameters
    ----------
    bars : BarContainer
        Container returned by ax.bar().
    edge_thickness_mm : float, optional
        Edge line width in mm. Default: from style (0.2).
    edgecolor : str or list, optional
        Edge color(s). Default: "black".
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    BarContainer
        The styled bar container.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> bars = ax.bar([1, 2, 3], [4, 5, 6])
    >>> fr.style_barplot(bars)
    """
    styler = BarplotStyler(style=style)
    return styler.apply(
        bars,
        edge_thickness_mm=edge_thickness_mm,
        edgecolor=edgecolor,
    )


# EOF
