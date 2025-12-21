#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapped Axes that records all plotting calls."""

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

if TYPE_CHECKING:
    from .._recorder import Recorder


class RecordingAxes:
    """Wrapper around matplotlib Axes that records all calls.

    This wrapper intercepts calls to plotting methods and records them
    for later reproduction.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The underlying matplotlib axes.
    recorder : Recorder
        The recorder instance to log calls to.
    position : tuple
        (row, col) position in the figure grid.

    Examples
    --------
    >>> import plotspec as mpr
    >>> fig, ax = mpr.subplots()
    >>> ax.plot([1, 2, 3], [4, 5, 6], color='red', id='my_line')
    >>> # The call is recorded automatically
    """

    def __init__(
        self,
        ax: Axes,
        recorder: "Recorder",
        position: Tuple[int, int] = (0, 0),
    ):
        self._ax = ax
        self._recorder = recorder
        self._position = position
        self._track = True

    @property
    def ax(self) -> Axes:
        """Get the underlying matplotlib axes."""
        return self._ax

    @property
    def position(self) -> Tuple[int, int]:
        """Get axes position in grid."""
        return self._position

    def __getattr__(self, name: str) -> Any:
        """Intercept attribute access to wrap methods.

        This is the core mechanism for recording calls.
        """
        attr = getattr(self._ax, name)

        # If it's a plotting or decoration method, wrap it
        if callable(attr) and name in (
            self._recorder.PLOTTING_METHODS | self._recorder.DECORATION_METHODS
        ):
            return self._create_recording_wrapper(name, attr)

        # For other methods/attributes, return as-is
        return attr

    def _create_recording_wrapper(self, method_name: str, method: callable):
        """Create a wrapper function that records the call.

        Parameters
        ----------
        method_name : str
            Name of the method.
        method : callable
            The original method.

        Returns
        -------
        callable
            Wrapped method that records calls.
        """
        def wrapper(*args, id: Optional[str] = None, track: bool = True, **kwargs):
            # Record the call if tracking is enabled
            if self._track and track:
                self._recorder.record_call(
                    ax_position=self._position,
                    method_name=method_name,
                    args=args,
                    kwargs=kwargs,
                    call_id=id,
                )

            # Call the original method (without our custom kwargs)
            return method(*args, **kwargs)

        return wrapper

    def no_record(self):
        """Context manager to temporarily disable recording.

        Examples
        --------
        >>> with ax.no_record():
        ...     ax.plot([1, 2, 3], [4, 5, 6])  # Not recorded
        """
        return _NoRecordContext(self)

    # Expose common properties directly
    @property
    def figure(self):
        return self._ax.figure

    @property
    def xaxis(self):
        return self._ax.xaxis

    @property
    def yaxis(self):
        return self._ax.yaxis

    # Methods that should not be recorded
    def get_xlim(self):
        return self._ax.get_xlim()

    def get_ylim(self):
        return self._ax.get_ylim()

    def get_xlabel(self):
        return self._ax.get_xlabel()

    def get_ylabel(self):
        return self._ax.get_ylabel()

    def get_title(self):
        return self._ax.get_title()


class _NoRecordContext:
    """Context manager to temporarily disable recording."""

    def __init__(self, axes: RecordingAxes):
        self._axes = axes
        self._original_track = axes._track

    def __enter__(self):
        self._axes._track = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._axes._track = self._original_track
        return False
