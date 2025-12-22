#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapped Axes that records all plotting calls."""

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np
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
    >>> import figrecipe as ps
    >>> fig, ax = ps.subplots()
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
            # Call the original method first (without our custom kwargs)
            result = method(*args, **kwargs)

            # Record the call if tracking is enabled
            if self._track and track:
                # Capture actual colors from result for plotting methods
                # that use matplotlib's color cycle
                recorded_kwargs = kwargs.copy()
                if method_name in ('plot', 'scatter', 'bar', 'barh', 'step', 'fill_between'):
                    if 'color' not in recorded_kwargs and 'c' not in recorded_kwargs:
                        actual_color = self._extract_color_from_result(method_name, result)
                        if actual_color is not None:
                            recorded_kwargs['color'] = actual_color

                self._recorder.record_call(
                    ax_position=self._position,
                    method_name=method_name,
                    args=args,
                    kwargs=recorded_kwargs,
                    call_id=id,
                )

            return result

        return wrapper

    def _extract_color_from_result(self, method_name: str, result) -> Optional[str]:
        """Extract actual color used from plot result.

        Parameters
        ----------
        method_name : str
            Name of the plotting method.
        result : Any
            Return value from the plotting method.

        Returns
        -------
        str or None
            The color used, or None if not extractable.
        """
        try:
            if method_name == 'plot':
                # plot() returns list of Line2D
                if result and hasattr(result[0], 'get_color'):
                    return result[0].get_color()
            elif method_name == 'scatter':
                # scatter() returns PathCollection
                if hasattr(result, 'get_facecolor'):
                    fc = result.get_facecolor()
                    if len(fc) > 0:
                        # Convert RGBA to hex
                        import matplotlib.colors as mcolors
                        return mcolors.to_hex(fc[0])
            elif method_name in ('bar', 'barh'):
                # bar() returns BarContainer
                if hasattr(result, 'patches') and result.patches:
                    fc = result.patches[0].get_facecolor()
                    import matplotlib.colors as mcolors
                    return mcolors.to_hex(fc)
            elif method_name == 'step':
                # step() returns list of Line2D
                if result and hasattr(result[0], 'get_color'):
                    return result[0].get_color()
            elif method_name == 'fill_between':
                # fill_between() returns PolyCollection
                if hasattr(result, 'get_facecolor'):
                    fc = result.get_facecolor()
                    if len(fc) > 0:
                        import matplotlib.colors as mcolors
                        return mcolors.to_hex(fc[0])
        except Exception:
            pass
        return None

    def no_record(self):
        """Context manager to temporarily disable recording.

        Examples
        --------
        >>> with ax.no_record():
        ...     ax.plot([1, 2, 3], [4, 5, 6])  # Not recorded
        """
        return _NoRecordContext(self)

    def record_seaborn_call(
        self,
        func_name: str,
        args: tuple,
        kwargs: Dict[str, Any],
        data_arrays: Dict[str, np.ndarray],
        call_id: Optional[str] = None,
    ) -> None:
        """Record a seaborn plotting call.

        Parameters
        ----------
        func_name : str
            Name of the seaborn function (e.g., 'scatterplot').
        args : tuple
            Processed positional arguments.
        kwargs : dict
            Processed keyword arguments.
        data_arrays : dict
            Dictionary of array data extracted from DataFrame/arrays.
        call_id : str, optional
            Custom ID for this call.
        """
        if not self._track:
            return

        from .._utils._numpy_io import should_store_inline, to_serializable

        # Generate call ID if not provided
        if call_id is None:
            call_id = self._recorder._generate_call_id(f"sns_{func_name}")

        # Process data arrays into args format
        processed_args = []
        for i, arg in enumerate(args):
            if arg == "__ARRAY__":
                key = f"_arg_{i}"
                if key in data_arrays:
                    arr = data_arrays[key]
                    if should_store_inline(arr):
                        processed_args.append({
                            "name": f"arg{i}",
                            "data": to_serializable(arr),
                            "dtype": str(arr.dtype),
                        })
                    else:
                        processed_args.append({
                            "name": f"arg{i}",
                            "data": "__FILE__",
                            "dtype": str(arr.dtype),
                            "_array": arr,
                        })
            else:
                processed_args.append({
                    "name": f"arg{i}",
                    "data": arg,
                })

        # Process DataFrame column data
        for key, arr in data_arrays.items():
            if key.startswith("_col_"):
                param_name = key[5:]  # Remove "_col_" prefix
                col_name = data_arrays.get(f"_colname_{param_name}", param_name)
                if should_store_inline(arr):
                    processed_args.append({
                        "name": col_name,
                        "param": param_name,
                        "data": to_serializable(arr),
                        "dtype": str(arr.dtype),
                    })
                else:
                    processed_args.append({
                        "name": col_name,
                        "param": param_name,
                        "data": "__FILE__",
                        "dtype": str(arr.dtype),
                        "_array": arr,
                    })

        # Process kwarg arrays
        processed_kwargs = dict(kwargs)
        for key, value in kwargs.items():
            if value == "__ARRAY__":
                arr_key = f"_kwarg_{key}"
                if arr_key in data_arrays:
                    arr = data_arrays[arr_key]
                    if should_store_inline(arr):
                        processed_kwargs[key] = to_serializable(arr)
                    else:
                        # Mark for file storage
                        processed_kwargs[key] = "__FILE__"
                        processed_kwargs[f"_array_{key}"] = arr

        # Create call record
        from .._recorder import CallRecord

        record = CallRecord(
            id=call_id,
            function=f"sns.{func_name}",
            args=processed_args,
            kwargs=processed_kwargs,
            ax_position=self._position,
        )

        # Add to axes record
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        ax_record.add_call(record)

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
