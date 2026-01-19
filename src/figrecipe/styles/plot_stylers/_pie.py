#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pie chart styler for publication-quality pie charts."""

__all__ = ["PieStyler", "style_pie"]

from typing import Any, List, Optional

from ._base import PlotStyler, get_color_palette, mm_to_pt


class PieStyler(PlotStyler):
    """Styler for matplotlib pie chart elements.

    Applies consistent edge widths, colors, and text styles to pie charts
    for publication-quality figures.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> patches, texts = ax.pie([1, 2, 3])[:2]
    >>> styler = PieStyler()
    >>> styler.apply(patches, texts)
    """

    style_section = "pie"

    def apply(
        self,
        patches: List[Any],
        texts: Optional[List[Any]] = None,
        autotexts: Optional[List[Any]] = None,
        edge_thickness_mm: Optional[float] = None,
        edge_color: str = "white",
        colors: Optional[List[str]] = None,
    ) -> List[Any]:
        """Apply styling to a pie chart.

        Parameters
        ----------
        patches : list of Wedge
            Wedge patches from ax.pie().
        texts : list of Text, optional
            Label texts from ax.pie().
        autotexts : list of Text, optional
            Autopct texts from ax.pie().
        edge_thickness_mm : float, optional
            Edge line width in mm. Default from style.
        edge_color : str
            Edge color for wedges. Default: "white".
        colors : list of str, optional
            Fill colors for wedges. If None, uses style palette.

        Returns
        -------
        list
            The styled wedge patches.
        """
        # Get parameters with defaults from style
        if edge_thickness_mm is None:
            edge_thickness_mm = self.get_param("edge_mm", 0.3)

        lw_pt = mm_to_pt(edge_thickness_mm)

        # Get color palette
        if colors is None:
            colors = get_color_palette(self.style)

        # Style wedge patches
        for i, patch in enumerate(patches):
            patch.set_linewidth(lw_pt)
            patch.set_edgecolor(edge_color)
            if colors:
                patch.set_facecolor(colors[i % len(colors)])

        # Style label texts if provided
        if texts is not None:
            for text in texts:
                if text is not None:
                    # Use style font size if available
                    font_size = self.get_param("label_pt", 8)
                    text.set_fontsize(font_size)

        # Style autopct texts if provided
        if autotexts is not None:
            for text in autotexts:
                if text is not None:
                    font_size = self.get_param("autopct_pt", 7)
                    text.set_fontsize(font_size)

        return patches


# Convenience function
def style_pie(
    patches: List[Any],
    texts: Optional[List[Any]] = None,
    autotexts: Optional[List[Any]] = None,
    edge_thickness_mm: Optional[float] = None,
    edge_color: str = "white",
    colors: Optional[List[str]] = None,
    style: Any = None,
) -> List[Any]:
    """Apply publication-quality styling to a pie chart.

    This is a convenience function that creates a PieStyler and applies it.

    Parameters
    ----------
    patches : list of Wedge
        Wedge patches from ax.pie().
    texts : list of Text, optional
        Label texts from ax.pie().
    autotexts : list of Text, optional
        Autopct texts from ax.pie().
    edge_thickness_mm : float, optional
        Edge line width in mm. Default: from style (0.3).
    edge_color : str
        Edge color. Default: "white".
    colors : list, optional
        Fill colors. Default: style palette.
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    list
        The styled wedge patches.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> patches, texts = ax.pie([1, 2, 3])[:2]
    >>> fr.style_pie(patches, texts)
    """
    styler = PieStyler(style=style)
    return styler.apply(
        patches,
        texts=texts,
        autotexts=autotexts,
        edge_thickness_mm=edge_thickness_mm,
        edge_color=edge_color,
        colors=colors,
    )


# EOF
