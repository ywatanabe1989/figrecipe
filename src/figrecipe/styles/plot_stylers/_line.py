#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Line plot styler for publication-quality line plots.

This is a placeholder for future expansion. Line plots are typically
styled automatically via figrecipe's recording wrappers.
"""

__all__ = ["LineStyler", "style_line"]

from typing import Any, Optional

from ._base import PlotStyler, mm_to_pt


class LineStyler(PlotStyler):
    """Styler for matplotlib line plot elements.

    Placeholder for future expansion. Line plots are typically styled
    automatically via figrecipe's recording wrappers.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.
    """

    style_section = "lines"

    def apply(
        self,
        line: Any,
        linewidth_mm: Optional[float] = None,
        color: Optional[str] = None,
        linestyle: Optional[str] = None,
    ) -> Any:
        """Apply styling to a line plot.

        Parameters
        ----------
        line : Line2D
            Line object from ax.plot().
        linewidth_mm : float, optional
            Line width in mm. Default from style.
        color : str, optional
            Line color.
        linestyle : str, optional
            Line style (e.g., '-', '--', ':', '-.').

        Returns
        -------
        Line2D
            The styled line.
        """
        # Get parameters with defaults from style
        if linewidth_mm is None:
            linewidth_mm = self.get_param("trace_mm", 0.2)

        lw_pt = mm_to_pt(linewidth_mm)
        line.set_linewidth(lw_pt)

        if color is not None:
            line.set_color(color)
        if linestyle is not None:
            line.set_linestyle(linestyle)

        return line


# Convenience function
def style_line(
    line: Any,
    linewidth_mm: Optional[float] = None,
    color: Optional[str] = None,
    linestyle: Optional[str] = None,
    style: Any = None,
) -> Any:
    """Apply publication-quality styling to a line plot.

    Parameters
    ----------
    line : Line2D
        Line object from ax.plot().
    linewidth_mm : float, optional
        Line width in mm. Default: from style.
    color : str, optional
        Line color.
    linestyle : str, optional
        Line style.
    style : DotDict, optional
        Style configuration.

    Returns
    -------
    Line2D
        The styled line.
    """
    styler = LineStyler(style=style)
    return styler.apply(
        line,
        linewidth_mm=linewidth_mm,
        color=color,
        linestyle=linestyle,
    )


# EOF
