#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagram visualization mixin for RecordingAxes."""

from typing import TYPE_CHECKING, Optional, Tuple

from matplotlib.figure import Figure

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .._recorder import Recorder


class DiagramMixin:
    """Mixin providing diagram method for RecordingAxes."""

    # These will be set by the main class
    _ax: "Axes"
    _recorder: "Recorder"
    _position: tuple
    _track: bool

    def diagram(
        self,
        diagram,
        *,
        id: Optional[str] = None,
        track: bool = True,
        auto_fix: bool = False,
    ):
        """Draw a box-and-arrow diagram with native matplotlib rendering.

        Parameters
        ----------
        diagram : Diagram or dict
            The diagram to render. Can be:
            - Diagram instance (or legacy Diagram)
            - Dictionary with diagram specification
        id : str, optional
            Custom ID for this call.
        track : bool
            Whether to record this call for reproducibility.
        auto_fix : bool
            Auto-resolve layout violations before rendering.

        Returns
        -------
        tuple
            (figure, axes) after rendering.
        """
        return schematic_plot(
            self._ax,
            diagram,
            self._recorder,
            self._position,
            self._track and track,
            id,
            auto_fix=auto_fix,
        )


def schematic_plot(
    ax: "Axes",
    schematic,
    recorder: "Recorder",
    position: Tuple[int, int],
    track: bool,
    call_id: Optional[str],
    *,
    auto_fix: bool = False,
) -> Tuple[Figure, "Axes"]:
    """Draw a FigRecipe Diagram with native matplotlib rendering.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to draw on.
    schematic : Diagram or dict
        The schematic to render. Can be:
        - Diagram instance
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

    from .._schematic._schematic import Diagram

    # Convert dict to Diagram if needed
    if isinstance(schematic, dict):
        info = Diagram.from_dict(schematic)
    elif isinstance(schematic, Diagram):
        info = schematic
    else:
        raise TypeError(f"schematic must be Diagram or dict, got {type(schematic)}")

    # Resolve auto-height before sizing the figure
    info._finalize_canvas_size()

    # Resize figure to match schematic's coordinate space BEFORE rendering
    fig = ax.figure
    x_range = info.xlim[1] - info.xlim[0]
    y_range = info.ylim[1] - info.ylim[0]
    fig.set_size_inches(x_range / 25.4, y_range / 25.4)

    # Render to the provided axes
    fig, rendered_ax = info.render(ax=ax, auto_fix=auto_fix)

    # Post-render validations (skipped inside render() when ax is provided)
    # Errors are stored on the figure so fr.save() can save _FAILED figures
    from .._schematic import _schematic_validate as _sv

    try:
        _sv.validate_all(info, fig=fig, ax=rendered_ax)
    except ValueError as e:
        if not hasattr(fig, "_schematic_validation_errors"):
            fig._schematic_validation_errors = []
        fig._schematic_validation_errors.append(str(e))

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

    final_id = call_id if call_id else recorder._generate_call_id("diagram")

    # Serialize diagram data for recipe
    diagram_data = info.to_dict()

    record = CallRecord(
        id=final_id,
        function="diagram",
        args=[],
        kwargs={"diagram_data": diagram_data},
        ax_position=position,
    )
    ax_record = recorder.figure_record.get_or_create_axes(*position)
    ax_record.add_call(record)


__all__ = ["DiagramMixin", "schematic_plot"]
