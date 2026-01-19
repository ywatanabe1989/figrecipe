#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imshow styler for publication-quality image plots."""

__all__ = ["ImshowStyler", "style_imshow"]

from typing import Any, Optional

from ._base import PlotStyler


class ImshowStyler(PlotStyler):
    """Styler for matplotlib imshow elements.

    Applies consistent interpolation and aspect settings to image plots
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
    >>> im = ax.imshow(np.random.rand(10, 10))
    >>> styler = ImshowStyler()
    >>> styler.apply(im, ax)
    """

    style_section = "imshow"

    def apply(
        self,
        image: Any,
        ax: Optional[Any] = None,
        interpolation: Optional[str] = None,
        aspect: Optional[str] = None,
        cmap: Optional[str] = None,
    ) -> Any:
        """Apply styling to an imshow plot.

        Parameters
        ----------
        image : AxesImage
            Image returned by ax.imshow().
        ax : Axes, optional
            The axes containing the image (for aspect ratio).
        interpolation : str, optional
            Interpolation method. Default from style or "nearest".
        aspect : str, optional
            Aspect ratio. Default: "equal".
        cmap : str, optional
            Colormap to apply.

        Returns
        -------
        AxesImage
            The styled image.
        """
        # Get parameters with defaults from style
        if interpolation is None:
            interpolation = self.get_param("interpolation", "nearest")
        if aspect is None:
            aspect = self.get_param("aspect", "equal")

        # Apply interpolation
        image.set_interpolation(interpolation)

        # Apply colormap if specified
        if cmap is not None:
            image.set_cmap(cmap)

        # Apply aspect to axes if provided
        if ax is not None:
            ax.set_aspect(aspect)

        return image


# Convenience function
def style_imshow(
    image: Any,
    ax: Optional[Any] = None,
    interpolation: Optional[str] = None,
    aspect: Optional[str] = None,
    cmap: Optional[str] = None,
    style: Any = None,
) -> Any:
    """Apply publication-quality styling to an imshow plot.

    This is a convenience function that creates an ImshowStyler and applies it.

    Parameters
    ----------
    image : AxesImage
        Image returned by ax.imshow().
    ax : Axes, optional
        The axes containing the image.
    interpolation : str, optional
        Interpolation method. Default: "nearest".
    aspect : str, optional
        Aspect ratio. Default: "equal".
    cmap : str, optional
        Colormap to apply.
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    AxesImage
        The styled image.

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> fig, ax = fr.subplots()
    >>> im = ax.imshow(np.random.rand(10, 10))
    >>> fr.style_imshow(im, ax)
    """
    styler = ImshowStyler(style=style)
    return styler.apply(
        image,
        ax=ax,
        interpolation=interpolation,
        aspect=aspect,
        cmap=cmap,
    )


# EOF
