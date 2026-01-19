#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heatmap styler for publication-quality heatmaps.

This is a placeholder for future expansion. Heatmaps extend imshow
with additional annotation and colorbar styling.
"""

__all__ = ["HeatmapStyler", "style_heatmap"]

from typing import Any, Optional

from ._base import PlotStyler, mm_to_pt


class HeatmapStyler(PlotStyler):
    """Styler for matplotlib heatmap elements.

    Placeholder for future expansion. Extends ImshowStyler with
    annotation and colorbar styling.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.
    """

    style_section = "heatmap"

    def apply(
        self,
        image: Any,
        ax: Optional[Any] = None,
        cbar: Optional[Any] = None,
        annotation_fontsize_pt: Optional[float] = None,
        cbar_width_mm: Optional[float] = None,
        interpolation: str = "nearest",
        aspect: str = "equal",
    ) -> Any:
        """Apply styling to a heatmap.

        Parameters
        ----------
        image : AxesImage
            Image returned by ax.imshow().
        ax : Axes, optional
            The axes containing the heatmap.
        cbar : Colorbar, optional
            Colorbar to style.
        annotation_fontsize_pt : float, optional
            Font size for cell annotations in points.
        cbar_width_mm : float, optional
            Colorbar width in mm.
        interpolation : str
            Interpolation method. Default: "nearest".
        aspect : str
            Aspect ratio. Default: "equal".

        Returns
        -------
        AxesImage
            The styled image.
        """
        # Apply base imshow styling
        image.set_interpolation(interpolation)

        if ax is not None:
            ax.set_aspect(aspect)

            # Style existing annotations
            if annotation_fontsize_pt is None:
                annotation_fontsize_pt = self.get_param("annotation_pt", 6)

            for text in ax.texts:
                text.set_fontsize(annotation_fontsize_pt)

        # Style colorbar if provided
        if cbar is not None:
            if cbar_width_mm is None:
                cbar_width_mm = self.get_param("cbar_width_mm", 3.0)

            # Style colorbar outline
            outline_mm = self.get_param("outline_mm", 0.2)
            outline_pt = mm_to_pt(outline_mm)
            cbar.outline.set_linewidth(outline_pt)

        return image


# Convenience function
def style_heatmap(
    image: Any,
    ax: Optional[Any] = None,
    cbar: Optional[Any] = None,
    annotation_fontsize_pt: Optional[float] = None,
    cbar_width_mm: Optional[float] = None,
    interpolation: str = "nearest",
    aspect: str = "equal",
    style: Any = None,
) -> Any:
    """Apply publication-quality styling to a heatmap.

    Parameters
    ----------
    image : AxesImage
        Image returned by ax.imshow().
    ax : Axes, optional
        The axes containing the heatmap.
    cbar : Colorbar, optional
        Colorbar to style.
    annotation_fontsize_pt : float, optional
        Font size for annotations.
    cbar_width_mm : float, optional
        Colorbar width in mm.
    interpolation : str
        Interpolation method. Default: "nearest".
    aspect : str
        Aspect ratio. Default: "equal".
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    AxesImage
        The styled image.
    """
    styler = HeatmapStyler(style=style)
    return styler.apply(
        image,
        ax=ax,
        cbar=cbar,
        annotation_fontsize_pt=annotation_fontsize_pt,
        cbar_width_mm=cbar_width_mm,
        interpolation=interpolation,
        aspect=aspect,
    )


# EOF
