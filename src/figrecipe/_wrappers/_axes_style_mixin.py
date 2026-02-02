#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Axis style helper methods mixin for RecordingAxes.

These methods provide convenient styling operations callable directly
on axes objects (e.g., ax.hide_spines()).
"""

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class AxesStyleMixin:
    """Mixin providing axis styling helper methods.

    Usage:
        >>> ax.hide_spines()  # Instead of fr.styles.hide_spines(ax)
        >>> ax.set_xyt('X', 'Y', 'Title')
    """

    _ax: "Axes"

    def hide_spines(self, spines: Optional[List[str]] = None):
        """Hide specified spines (default: top and right).

        Parameters
        ----------
        spines : list, optional
            Spines to hide. Default: ['top', 'right']

        Examples
        --------
        >>> ax.hide_spines()  # Hide top and right
        >>> ax.hide_spines(['top', 'right', 'bottom'])
        """
        from ..styles._axis_helpers import hide_spines

        return hide_spines(self._ax, spines)

    def show_spines(self, spines: Optional[List[str]] = None):
        """Show specified spines.

        Parameters
        ----------
        spines : list, optional
            Spines to show. Default: all

        Examples
        --------
        >>> ax.show_spines(['left', 'bottom'])
        """
        from ..styles._axis_helpers import show_spines

        return show_spines(self._ax, spines)

    def toggle_spines(self, spines: Optional[List[str]] = None):
        """Toggle spine visibility.

        Parameters
        ----------
        spines : list, optional
            Spines to toggle

        Examples
        --------
        >>> ax.toggle_spines(['top'])
        """
        from ..styles._axis_helpers import toggle_spines

        return toggle_spines(self._ax, spines)

    def rotate_labels(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        x_ha: Optional[str] = None,
        y_ha: Optional[str] = None,
        auto_adjust: bool = True,
    ):
        """Rotate tick labels.

        Parameters
        ----------
        x : float, optional
            Rotation angle for x-axis labels in degrees
        y : float, optional
            Rotation angle for y-axis labels in degrees
        x_ha : str, optional
            Horizontal alignment for x-axis
        y_ha : str, optional
            Horizontal alignment for y-axis
        auto_adjust : bool
            Auto-adjust alignment based on angle

        Examples
        --------
        >>> ax.rotate_labels(x=45)
        >>> ax.rotate_labels(x=45, y=30)
        """
        from ..styles._axis_helpers import rotate_labels

        return rotate_labels(
            self._ax, x=x, y=y, x_ha=x_ha, y_ha=y_ha, auto_adjust=auto_adjust
        )

    def set_xyt(
        self,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        **kwargs,
    ):
        """Set xlabel, ylabel, and title in one call.

        Parameters
        ----------
        xlabel : str, optional
        ylabel : str, optional
        title : str, optional
        **kwargs : dict
            Passed to set_xlabel, set_ylabel, set_title

        Examples
        --------
        >>> ax.set_xyt('Time (s)', 'Amplitude', 'Signal')
        """
        # Use self.method() to go through recording wrapper, not self._ax.method()
        if xlabel is not None:
            self.set_xlabel(xlabel, **kwargs)
        if ylabel is not None:
            self.set_ylabel(ylabel, **kwargs)
        if title is not None:
            self.set_title(title, **kwargs)
        return self

    def set_n_ticks(self, n_x: Optional[int] = None, n_y: Optional[int] = None):
        """Set number of ticks on axes.

        Parameters
        ----------
        n_x : int, optional
            Number of x-axis ticks
        n_y : int, optional
            Number of y-axis ticks

        Examples
        --------
        >>> ax.set_n_ticks(5, 5)
        """
        from ..styles._axis_helpers import set_n_ticks

        return set_n_ticks(self._ax, n_x, n_y)

    def sci_note(self, axis: str = "both", scilimits: Optional[tuple] = None):
        """Use scientific notation for tick labels.

        Parameters
        ----------
        axis : str
            'x', 'y', or 'both'
        scilimits : tuple, optional
            Range outside which to use sci notation

        Examples
        --------
        >>> ax.sci_note('y')
        """
        from ..styles._axis_helpers import sci_note

        return sci_note(self._ax, axis, scilimits)

    def force_aspect(self, ratio: float = 1.0):
        """Force aspect ratio.

        Parameters
        ----------
        ratio : float
            Aspect ratio (height/width)

        Examples
        --------
        >>> ax.force_aspect(1.0)  # Square
        """
        from ..styles._axis_helpers import force_aspect

        return force_aspect(self._ax, ratio)

    def extend(self, direction: str = "both", factor: float = 0.05):
        """Extend axis limits by a factor.

        Parameters
        ----------
        direction : str
            'x', 'y', or 'both'
        factor : float
            Extension factor (default 5%)

        Examples
        --------
        >>> ax.extend('y', 0.1)  # Extend y by 10%
        """
        from ..styles._axis_helpers import extend

        return extend(self._ax, direction, factor)

    def map_ticks(
        self,
        axis: str = "x",
        mapping: Optional[dict] = None,
        labels: Optional[list] = None,
    ):
        """Map tick values to custom labels.

        Parameters
        ----------
        axis : str
            'x' or 'y'
        mapping : dict, optional
            {value: label} mapping
        labels : list, optional
            Labels for current tick positions

        Examples
        --------
        >>> ax.map_ticks('x', {0: 'A', 1: 'B', 2: 'C'})
        """
        from ..styles._axis_helpers import map_ticks

        return map_ticks(self._ax, axis, mapping, labels)


__all__ = ["AxesStyleMixin"]

# EOF
