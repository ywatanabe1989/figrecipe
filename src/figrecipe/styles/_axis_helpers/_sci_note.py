#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scientific notation utilities for matplotlib axes."""

__all__ = ["OOMFormatter", "sci_note"]

from typing import Any, Optional, Tuple

import matplotlib.ticker
import numpy as np

from ._base import get_axis_from_wrapper, validate_axis


class OOMFormatter(matplotlib.ticker.ScalarFormatter):
    """Custom formatter for scientific notation with fixed order of magnitude.

    A matplotlib formatter that allows you to specify a fixed exponent for
    scientific notation, rather than letting matplotlib choose it automatically.
    Useful when you want consistent notation across multiple plots or specific
    exponent values.

    Parameters
    ----------
    order : int or None, optional
        Fixed order of magnitude (exponent) to use. If None, calculated
        automatically. Default is None.
    fformat : str, optional
        Format string for the mantissa. Default is "%1.1f".
    offset : bool, optional
        Whether to use offset notation. Default is True.
    mathText : bool, optional
        Whether to use mathtext rendering. Default is True.

    Examples
    --------
    >>> # Force all labels to use 10^3 notation
    >>> formatter = OOMFormatter(order=3, fformat="%1.2f")
    >>> ax.xaxis.set_major_formatter(formatter)

    >>> # Use 10^-6 for microvolts
    >>> formatter = OOMFormatter(order=-6, fformat="%1.1f")
    >>> ax.yaxis.set_major_formatter(formatter)
    """

    def __init__(
        self,
        order: Optional[int] = None,
        fformat: str = "%1.1f",
        offset: bool = True,
        mathText: bool = True,
    ):
        self.order = order
        self.fformat = fformat
        matplotlib.ticker.ScalarFormatter.__init__(
            self, useOffset=offset, useMathText=mathText
        )

    def _set_order_of_magnitude(self) -> None:
        if self.order is not None:
            self.orderOfMagnitude = self.order
        else:
            super()._set_order_of_magnitude()

    def _set_format(
        self, vmin: Optional[float] = None, vmax: Optional[float] = None
    ) -> None:
        self.format = self.fformat
        if self._useMathText:
            self.format = r"$\mathdefault{%s}$" % self.format


def sci_note(
    ax: Any,
    fformat: str = "%1.1f",
    x: bool = False,
    y: bool = False,
    scilimits: Tuple[int, int] = (-3, 3),
    order_x: Optional[int] = None,
    order_y: Optional[int] = None,
    pad_x: int = -22,
    pad_y: int = -20,
) -> Any:
    """Apply scientific notation to axis with optional manual order of magnitude.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Axes object to modify.
    fformat : str
        Format string for tick labels. Default: "%1.1f".
    x : bool
        Whether to apply scientific notation to x-axis. Default: False.
    y : bool
        Whether to apply scientific notation to y-axis. Default: False.
    scilimits : tuple of int
        Scientific notation limits (min_exp, max_exp). Default: (-3, 3).
    order_x : int, optional
        Manual order of magnitude for x-axis. If None, calculated automatically.
    order_y : int, optional
        Manual order of magnitude for y-axis. If None, calculated automatically.
    pad_x : int
        Padding for x-axis labels. Default: -22.
    pad_y : int
        Padding for y-axis labels. Default: -20.

    Returns
    -------
    Axes
        The modified Axes object.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1e6, 2e6, 3e6], [1e-3, 2e-3, 3e-3])
    >>> fr.sci_note(ax, x=True, y=True)  # Auto-calculate order
    >>> # Or specify order manually:
    >>> fr.sci_note(ax, x=True, order_x=6, y=True, order_y=-3)
    """
    validate_axis(ax)
    ax = get_axis_from_wrapper(ax)

    if x:
        # Calculate order if not specified
        if order_x is None:
            xlim = ax.get_xlim()
            max_val = np.max(np.abs(xlim))
            if max_val > 0:
                order_x = int(np.floor(np.log10(max_val + 1e-10)))
            else:
                order_x = 0

        ax.xaxis.set_major_formatter(OOMFormatter(order=order_x, fformat=fformat))
        ax.ticklabel_format(axis="x", style="sci", scilimits=scilimits)
        ax.xaxis.labelpad = pad_x

        # Position the offset text
        xlim = ax.get_xlim()
        shift_x = (xlim[0] - xlim[1]) * 0.01
        ax.xaxis.get_offset_text().set_position((shift_x, 0))

    if y:
        # Calculate order if not specified
        if order_y is None:
            ylim = ax.get_ylim()
            max_val = np.max(np.abs(ylim))
            if max_val > 0:
                order_y = int(np.floor(np.log10(max_val + 1e-10)))
            else:
                order_y = 0

        ax.yaxis.set_major_formatter(OOMFormatter(order=order_y, fformat=fformat))
        ax.ticklabel_format(axis="y", style="sci", scilimits=scilimits)
        ax.yaxis.labelpad = pad_y

        # Position the offset text
        ylim = ax.get_ylim()
        shift_y = (ylim[0] - ylim[1]) * 0.01
        ax.yaxis.get_offset_text().set_position((0, shift_y))

    return ax


# EOF
