#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boxplot styler for publication-quality boxplots."""

__all__ = ["BoxplotStyler", "style_boxplot"]

from typing import Any, List, Optional

from ._base import PlotStyler, get_color_palette, mm_to_pt


class BoxplotStyler(PlotStyler):
    """Styler for matplotlib boxplot elements.

    Applies consistent line widths, colors, and marker styles to boxplots
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
    >>> bp = ax.boxplot([np.random.randn(100) for _ in range(3)], patch_artist=True)
    >>> styler = BoxplotStyler()
    >>> styler.apply(bp)
    """

    style_section = "boxplot"

    def apply(
        self,
        boxplot_dict: dict,
        linewidth_mm: Optional[float] = None,
        flier_size_mm: Optional[float] = None,
        median_color: str = "black",
        edge_color: str = "black",
        colors: Optional[List[str]] = None,
        add_legend: bool = False,
        labels: Optional[List[str]] = None,
    ) -> dict:
        """Apply styling to a boxplot.

        Parameters
        ----------
        boxplot_dict : dict
            Dictionary returned by ax.boxplot().
        linewidth_mm : float, optional
            Line width in mm for all elements. Default from style.
        flier_size_mm : float, optional
            Outlier marker size in mm. Default from style.
        median_color : str
            Color for median line.
        edge_color : str
            Color for box edges, whiskers, and caps.
        colors : list of str, optional
            Fill colors for boxes. If None, uses style palette.
        add_legend : bool
            Whether to add a legend.
        labels : list of str, optional
            Legend labels (required if add_legend=True).

        Returns
        -------
        dict
            The styled boxplot dictionary.
        """
        import matplotlib.patches as mpatches

        # Get parameters with defaults from style
        if linewidth_mm is None:
            linewidth_mm = self.get_param("line_mm", 0.2)
        if flier_size_mm is None:
            flier_size_mm = self.get_param("flier_mm") or self.get_param("size_mm", 0.8)

        lw_pt = mm_to_pt(linewidth_mm)
        flier_size_pt = mm_to_pt(flier_size_mm)

        # Get color palette
        if colors is None:
            colors = get_color_palette(self.style)

        # Style box elements
        for element_name in ["boxes", "whiskers", "caps"]:
            if element_name in boxplot_dict:
                for element in boxplot_dict[element_name]:
                    element.set_linewidth(lw_pt)
                    element.set_color(edge_color)

        # Style medians
        if "medians" in boxplot_dict:
            for median in boxplot_dict["medians"]:
                median.set_linewidth(lw_pt)
                median.set_color(median_color)

        # Style fliers (outliers)
        if "fliers" in boxplot_dict:
            for flier in boxplot_dict["fliers"]:
                flier.set_markersize(flier_size_pt)
                flier.set_markeredgewidth(lw_pt)
                flier.set_markeredgecolor(edge_color)
                flier.set_markerfacecolor("none")

        # Apply fill colors
        for i, box in enumerate(boxplot_dict.get("boxes", [])):
            color = colors[i % len(colors)]
            if hasattr(box, "set_facecolor"):
                box.set_facecolor(color)
            box.set_edgecolor(edge_color)

        # Add legend if requested
        if add_legend and labels is not None:
            legend_elements = [
                mpatches.Patch(
                    facecolor=colors[i % len(colors)],
                    edgecolor=edge_color,
                    linewidth=lw_pt,
                    label=label,
                )
                for i, label in enumerate(labels)
            ]
            if boxplot_dict.get("boxes"):
                ax = boxplot_dict["boxes"][0].axes
                ax.legend(handles=legend_elements)

        return boxplot_dict


# Convenience function
def style_boxplot(
    boxplot_dict: dict,
    linewidth_mm: Optional[float] = None,
    flier_size_mm: Optional[float] = None,
    median_color: str = "black",
    edge_color: str = "black",
    colors: Optional[List[str]] = None,
    add_legend: bool = False,
    labels: Optional[List[str]] = None,
    style: Any = None,
) -> dict:
    """Apply publication-quality styling to a boxplot.

    This is a convenience function that creates a BoxplotStyler and applies it.

    Parameters
    ----------
    boxplot_dict : dict
        Dictionary returned by ax.boxplot().
    linewidth_mm : float, optional
        Line width in mm. Default: from style (0.2).
    flier_size_mm : float, optional
        Outlier marker size in mm. Default: from style (0.8).
    median_color : str
        Median line color. Default: "black".
    edge_color : str
        Edge color for boxes/whiskers/caps. Default: "black".
    colors : list, optional
        Box fill colors. Default: style palette.
    add_legend : bool
        Add legend. Default: False.
    labels : list, optional
        Legend labels.
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    dict
        The styled boxplot dictionary.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> bp = ax.boxplot(data, patch_artist=True)
    >>> fr.style_boxplot(bp)
    """
    styler = BoxplotStyler(style=style)
    return styler.apply(
        boxplot_dict,
        linewidth_mm=linewidth_mm,
        flier_size_mm=flier_size_mm,
        median_color=median_color,
        edge_color=edge_color,
        colors=colors,
        add_legend=add_legend,
        labels=labels,
    )


# EOF
