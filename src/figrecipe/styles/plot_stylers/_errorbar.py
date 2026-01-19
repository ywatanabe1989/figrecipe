#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Errorbar plot styler for publication-quality error bar plots."""

__all__ = ["ErrorbarStyler", "style_errorbar"]

from typing import Any, Optional

from ._base import PlotStyler, mm_to_pt


class ErrorbarStyler(PlotStyler):
    """Styler for matplotlib errorbar plot elements.

    Applies consistent line widths and cap sizes to error bar plots
    for publication-quality figures.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> eb = ax.errorbar([1, 2, 3], [4, 5, 6], yerr=[0.5, 0.5, 0.5])
    >>> styler = ErrorbarStyler()
    >>> styler.apply(eb)
    """

    style_section = "errorbar"

    def apply(
        self,
        errorbar_container: Any,
        thickness_mm: Optional[float] = None,
        cap_width_mm: Optional[float] = None,
        color: Optional[str] = None,
    ) -> Any:
        """Apply styling to an errorbar plot.

        Parameters
        ----------
        errorbar_container : ErrorbarContainer
            Container returned by ax.errorbar().
        thickness_mm : float, optional
            Line thickness in mm. Default from style.
        cap_width_mm : float, optional
            Cap width in mm. Default from style.
        color : str, optional
            Color for all errorbar elements.

        Returns
        -------
        ErrorbarContainer
            The styled errorbar container.
        """
        # Get parameters with defaults from style
        if thickness_mm is None:
            thickness_mm = self.get_param("line_mm", 0.2)
        if cap_width_mm is None:
            cap_width_mm = self.get_param("cap_mm", 1.0)

        lw_pt = mm_to_pt(thickness_mm)
        cap_pt = mm_to_pt(cap_width_mm)

        # ErrorbarContainer structure: (data_line, caplines, barlinecols)
        data_line = errorbar_container[0]
        caplines = errorbar_container[1] if len(errorbar_container) > 1 else []
        barlinecols = errorbar_container[2] if len(errorbar_container) > 2 else []

        # Style data line
        if data_line is not None:
            data_line.set_linewidth(lw_pt)
            if color is not None:
                data_line.set_color(color)

        # Style cap lines
        if caplines is not None:
            for cap in caplines:
                if cap is not None:
                    cap.set_linewidth(lw_pt)
                    cap.set_markersize(cap_pt)
                    if color is not None:
                        cap.set_color(color)

        # Style bar line collections
        if barlinecols is not None:
            for collection in barlinecols:
                if collection is not None:
                    collection.set_linewidth(lw_pt)
                    if color is not None:
                        collection.set_color(color)

        return errorbar_container


# Convenience function
def style_errorbar(
    errorbar_container: Any,
    thickness_mm: Optional[float] = None,
    cap_width_mm: Optional[float] = None,
    color: Optional[str] = None,
    style: Any = None,
) -> Any:
    """Apply publication-quality styling to an errorbar plot.

    This is a convenience function that creates an ErrorbarStyler and applies it.

    Parameters
    ----------
    errorbar_container : ErrorbarContainer
        Container returned by ax.errorbar().
    thickness_mm : float, optional
        Line thickness in mm. Default: from style (0.2).
    cap_width_mm : float, optional
        Cap width in mm. Default: from style (1.0).
    color : str, optional
        Color for all elements.
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    ErrorbarContainer
        The styled errorbar container.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> eb = ax.errorbar([1, 2, 3], [4, 5, 6], yerr=[0.5, 0.5, 0.5])
    >>> fr.style_errorbar(eb)
    """
    styler = ErrorbarStyler(style=style)
    return styler.apply(
        errorbar_container,
        thickness_mm=thickness_mm,
        cap_width_mm=cap_width_mm,
        color=color,
    )


# EOF
