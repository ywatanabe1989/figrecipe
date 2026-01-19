#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Histogram styler for publication-quality histograms.

This is a placeholder for future expansion. Histograms share styling
with bar plots and are handled by finalize_special_plots.
"""

__all__ = ["HistogramStyler", "style_histogram"]

from typing import Any, List, Optional, Union

from ._base import PlotStyler, get_color_palette, mm_to_pt


class HistogramStyler(PlotStyler):
    """Styler for matplotlib histogram elements.

    Placeholder for future expansion. Histograms share styling
    characteristics with bar plots.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.
    """

    style_section = "histogram"

    def apply(
        self,
        patches: Union[Any, List[Any]],
        edge_thickness_mm: Optional[float] = None,
        edge_color: str = "black",
        colors: Optional[List[str]] = None,
        alpha: float = 0.7,
    ) -> Union[Any, List[Any]]:
        """Apply styling to a histogram.

        Parameters
        ----------
        patches : list of Patch or BarContainer
            Patches from ax.hist().
        edge_thickness_mm : float, optional
            Edge line width in mm. Default from style.
        edge_color : str
            Edge color. Default: "black".
        colors : list of str, optional
            Fill colors. If None, uses style palette.
        alpha : float
            Fill transparency. Default: 0.7.

        Returns
        -------
        list or BarContainer
            The styled patches.
        """
        # Get parameters with defaults from style
        if edge_thickness_mm is None:
            edge_thickness_mm = self.get_param("edge_mm", 0.2)

        lw_pt = mm_to_pt(edge_thickness_mm)

        # Get color palette
        if colors is None:
            colors = get_color_palette(self.style)

        # Handle both single histogram and multiple
        patch_list = patches if isinstance(patches, (list, tuple)) else [patches]

        for i, patch_group in enumerate(patch_list):
            color = colors[i % len(colors)]
            # Handle BarContainer or list of patches
            if hasattr(patch_group, "__iter__"):
                for patch in patch_group:
                    patch.set_linewidth(lw_pt)
                    patch.set_edgecolor(edge_color)
                    patch.set_facecolor(color)
                    patch.set_alpha(alpha)
            else:
                patch_group.set_linewidth(lw_pt)
                patch_group.set_edgecolor(edge_color)
                patch_group.set_facecolor(color)
                patch_group.set_alpha(alpha)

        return patches


# Convenience function
def style_histogram(
    patches: Union[Any, List[Any]],
    edge_thickness_mm: Optional[float] = None,
    edge_color: str = "black",
    colors: Optional[List[str]] = None,
    alpha: float = 0.7,
    style: Any = None,
) -> Union[Any, List[Any]]:
    """Apply publication-quality styling to a histogram.

    Parameters
    ----------
    patches : list of Patch or BarContainer
        Patches from ax.hist().
    edge_thickness_mm : float, optional
        Edge line width in mm. Default: from style.
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
    list or BarContainer
        The styled patches.
    """
    styler = HistogramStyler(style=style)
    return styler.apply(
        patches,
        edge_thickness_mm=edge_thickness_mm,
        edge_color=edge_color,
        colors=colors,
        alpha=alpha,
    )


# EOF
