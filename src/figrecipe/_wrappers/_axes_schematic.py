#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schematic visualization mixin for RecordingAxes."""

from typing import TYPE_CHECKING, Optional, Tuple

from matplotlib.figure import Figure

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .._recorder import Recorder


class SchematicMixin:
    """Mixin providing schematic method for RecordingAxes."""

    # These will be set by the main class
    _ax: "Axes"
    _recorder: "Recorder"
    _position: tuple
    _track: bool

    def schematic(
        self,
        schematic,
        *,
        id: Optional[str] = None,
        track: bool = True,
    ):
        """Draw a FigRecipe Schematic with native matplotlib rendering.

        Parameters
        ----------
        schematic : Schematic or dict
            The schematic to render. Can be:
            - Schematic instance
            - Dictionary with schematic specification
        id : str, optional
            Custom ID for this call.
        track : bool
            Whether to record this call for reproducibility.

        Returns
        -------
        tuple
            (figure, axes) after rendering.
        """
        return schematic_plot(
            self._ax,
            schematic,
            self._recorder,
            self._position,
            self._track and track,
            id,
        )


def schematic_plot(
    ax: "Axes",
    schematic,
    recorder: "Recorder",
    position: Tuple[int, int],
    track: bool,
    call_id: Optional[str],
) -> Tuple[Figure, "Axes"]:
    """Draw a FigRecipe Schematic with native matplotlib rendering.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to draw on.
    schematic : Schematic or dict
        The schematic to render. Can be:
        - Schematic instance
        - Dictionary with schematic specification
    recorder : Recorder
        The recorder instance for tracking calls.
    position : tuple
        (row, col) position in the figure grid.
    track : bool
        Whether to record this call.
    call_id : str, optional
        Custom ID for this call.

    Returns
    -------
    tuple
        (figure, axes) after rendering.
    """

    from .._diagram._schematic import Schematic

    # Convert dict to Schematic if needed
    if isinstance(schematic, dict):
        info = Schematic.from_dict(schematic)
    elif isinstance(schematic, Schematic):
        info = schematic
    else:
        raise TypeError(f"schematic must be Schematic or dict, got {type(schematic)}")

    # Render to the provided axes
    fig, rendered_ax = info.render(ax=ax)

    # Resize figure to match schematic's coordinate space
    x_range = info.xlim[1] - info.xlim[0]
    y_range = info.ylim[1] - info.ylim[0]
    fig.set_size_inches(x_range / 25.4, y_range / 25.4)

    # Record for reproducibility
    if track:
        _record_schematic_call(
            recorder,
            position,
            call_id,
            info,
        )

    return fig, rendered_ax


def _record_schematic_call(
    recorder: "Recorder",
    position: Tuple[int, int],
    call_id: Optional[str],
    info,
) -> None:
    """Record schematic call for reproducibility."""
    from .._recorder import CallRecord

    final_id = call_id if call_id else recorder._generate_call_id("schematic")

    # Serialize schematic data for recipe
    schematic_data = info.to_dict()

    record = CallRecord(
        id=final_id,
        function="schematic",
        args=[],
        kwargs={"schematic_data": schematic_data},
        ax_position=position,
    )
    ax_record = recorder.figure_record.get_or_create_axes(*position)
    ax_record.add_call(record)


__all__ = ["SchematicMixin", "schematic_plot"]
