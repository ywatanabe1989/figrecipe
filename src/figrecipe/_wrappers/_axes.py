#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapped Axes that records all plotting calls."""

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

import numpy as np
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

    # Methods whose results can be referenced by other methods (e.g., clabel needs ContourSet)
    RESULT_REFERENCEABLE_METHODS = {"contour", "contourf"}
    # Methods that take results from other methods as arguments
    RESULT_REFERENCING_METHODS = {"clabel"}

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
        # Map matplotlib result objects (by id) to their source call_id
        self._result_refs: Dict[int, str] = {}

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
        """Create a wrapper function that records the call."""
        from ._axes_helpers import record_call_with_color_capture

        def wrapper(
            *args,
            id: Optional[str] = None,
            track: bool = True,
            stats: Optional[Dict[str, Any]] = None,
            **kwargs,
        ):
            # Call matplotlib method (without stats - it's metadata only)
            result = method(*args, **kwargs)
            if self._track and track:
                # Re-add stats to kwargs for recording
                record_kwargs = kwargs.copy()
                if stats is not None:
                    record_kwargs["stats"] = stats
                record_call_with_color_capture(
                    self._recorder,
                    self._position,
                    method_name,
                    args,
                    record_kwargs,
                    result,
                    id,
                    self._result_refs,
                    self.RESULT_REFERENCING_METHODS,
                    self.RESULT_REFERENCEABLE_METHODS,
                )
            return result

        return wrapper

    def set_caption(self, caption: str) -> "RecordingAxes":
        """Set panel caption metadata (not rendered, stored in recipe).

        This is for storing a description for this panel/axis,
        typically used in multi-panel scientific figures
        (e.g., "(A) Control group measurements").

        Parameters
        ----------
        caption : str
            The panel caption text.

        Returns
        -------
        RecordingAxes
            Self for method chaining.

        Examples
        --------
        >>> fig, axes = fr.subplots(1, 2)
        >>> axes[0].set_caption("(A) Control group")
        >>> axes[1].set_caption("(B) Treatment group")
        """
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        ax_record.caption = caption
        return self

    @property
    def panel_caption(self) -> Optional[str]:
        """Get the panel caption metadata."""
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        return ax_record.caption

    def set_stats(self, stats: Dict[str, Any]) -> "RecordingAxes":
        """Set panel-level statistics metadata (not rendered, stored in recipe).

        This is for storing statistical summary or comparison results
        for this panel/axis, such as group means, sample sizes, or
        comparison p-values.

        Parameters
        ----------
        stats : dict
            Statistics dictionary. Common keys include:
            - n: sample size
            - mean: mean value
            - std: standard deviation
            - sem: standard error of the mean
            - comparisons: list of comparison results

        Returns
        -------
        RecordingAxes
            Self for method chaining.

        Examples
        --------
        >>> fig, axes = fr.subplots(1, 2)
        >>> axes[0].set_stats({"n": 50, "mean": 3.2, "std": 1.1})
        >>> axes[1].set_stats({
        ...     "n": 48,
        ...     "mean": 5.1,
        ...     "comparisons": [{"vs": "control", "p_value": 0.003}]
        ... })
        """
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        ax_record.stats = stats
        return self

    @property
    def stats(self) -> Optional[Dict[str, Any]]:
        """Get the panel-level statistics metadata."""
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        return ax_record.stats

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
        """Record a seaborn plotting call."""
        if not self._track:
            return

        from ._axes_seaborn import record_seaborn_call

        record_seaborn_call(
            self._recorder,
            self._position,
            func_name,
            args,
            kwargs,
            data_arrays,
            call_id,
        )

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

    def pie(
        self,
        x,
        *,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Pie chart with automatic SCITEX styling."""
        from ._axes_plots import pie_plot

        return pie_plot(
            self._ax,
            x,
            self._recorder,
            self._position,
            self._track and track,
            id,
            **kwargs,
        )

    def imshow(
        self,
        X,
        *,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Display image with automatic SCITEX styling."""
        from ._axes_plots import imshow_plot

        return imshow_plot(
            self._ax,
            X,
            self._recorder,
            self._position,
            self._track and track,
            id,
            **kwargs,
        )

    def violinplot(
        self,
        dataset,
        positions=None,
        *,
        id: Optional[str] = None,
        track: bool = True,
        inner: Optional[str] = None,
        **kwargs,
    ):
        """Violin plot with support for inner display options."""
        from ._axes_plots import violinplot_plot

        return violinplot_plot(
            self._ax,
            dataset,
            positions,
            self._recorder,
            self._position,
            self._track and track,
            id,
            inner,
            **kwargs,
        )

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

    def joyplot(
        self,
        arrays,
        *,
        overlap: float = 0.5,
        fill_alpha: float = 0.7,
        line_alpha: float = 1.0,
        colors=None,
        labels=None,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Create a joyplot (ridgeline plot) for distribution comparison."""
        from ._axes_plots import joyplot_plot

        return joyplot_plot(
            self._ax,
            self,
            arrays,
            self._recorder,
            self._position,
            self._track and track,
            id,
            overlap,
            fill_alpha,
            line_alpha,
            colors,
            labels,
            **kwargs,
        )

    def swarmplot(
        self,
        data,
        positions=None,
        *,
        size: float = None,
        color=None,
        alpha: float = 0.7,
        jitter: float = 0.3,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Create a swarm plot (beeswarm plot) showing individual data points."""
        from ._axes_plots import swarmplot_plot

        return swarmplot_plot(
            self._ax,
            data,
            positions,
            self._recorder,
            self._position,
            self._track and track,
            id,
            size,
            color,
            alpha,
            jitter,
            **kwargs,
        )

    @property
    def caption(self) -> Optional[str]:
        """Get the panel caption metadata."""
        ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
        return ax_record.caption

    def generate_panel_caption(
        self, label: Optional[str] = None, style: str = "publication"
    ) -> str:
        """Generate a caption for this panel from stats metadata."""
        from ._caption_generator import generate_panel_caption

        return generate_panel_caption(label=label, stats=self.stats, style=style)

    def add_stat_annotation(
        self,
        x1: float,
        x2: float,
        p_value: Optional[float] = None,
        text: Optional[str] = None,
        y: Optional[float] = None,
        style: str = "stars",
        bracket_height: Optional[float] = None,
        text_offset: Optional[float] = None,
        color: Optional[str] = None,
        linewidth: Optional[float] = None,
        fontsize: Optional[float] = None,
        fontweight: Optional[str] = None,
        id: Optional[str] = None,
        track: bool = True,
        **kwargs,
    ):
        """Add a statistical comparison annotation (bracket with stars/p-value).

        Parameters
        ----------
        x1, x2 : float
            X positions of the two groups being compared.
        p_value : float, optional
            P-value for automatic star conversion.
        text : str, optional
            Custom text (overrides p_value formatting).
        y : float, optional
            Y position for bracket (auto-calculated if None).
        style : str
            "stars", "p_value", "both", or "bracket_only".
        """
        from ._stat_annotation import draw_stat_annotation

        # Draw the annotation
        artists = draw_stat_annotation(
            self._ax,
            x1,
            x2,
            y=y,
            text=text,
            p_value=p_value,
            style=style,
            bracket_height=bracket_height,
            text_offset=text_offset,
            color=color,
            linewidth=linewidth,
            fontsize=fontsize,
            fontweight=fontweight,
            **kwargs,
        )

        # Record if tracking
        if self._track and track:
            call_id = id if id else self._recorder._generate_call_id("stat_annotation")
            record_kwargs = {
                "x1": x1,
                "x2": x2,
                "p_value": p_value,
                "text": text,
                "y": y,
                "style": style,
                "bracket_height": bracket_height,
                "text_offset": text_offset,
                "color": color,
                "linewidth": linewidth,
                "fontsize": fontsize,
            }
            record_kwargs.update(kwargs)
            # Remove None values
            record_kwargs = {k: v for k, v in record_kwargs.items() if v is not None}

            from .._recorder import CallRecord

            record = CallRecord(
                id=call_id,
                function="stat_annotation",
                args=[],
                kwargs=record_kwargs,
                ax_position=self._position,
            )
            ax_record = self._recorder.figure_record.get_or_create_axes(*self._position)
            ax_record.add_decoration(record)

        return artists


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
