#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagram visualization method implementation for RecordingAxes."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .._recorder import Recorder


def diagram_plot(
    ax: "Axes",
    diagram,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    *,
    layout: str = "layered",
    direction: Optional[str] = None,
    positions: Optional[Dict[str, tuple]] = None,
) -> Dict[str, Any]:
    """Draw a FigRecipe Diagram with native matplotlib rendering.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to draw on.
    diagram : Diagram or DiagramSpec or dict
        The diagram to render. Can be:
        - Diagram instance
        - DiagramSpec instance
        - Dictionary with diagram specification
    recorder : Recorder
        The recorder instance for tracking calls.
    position : tuple
        (row, col) position in the figure grid.
    track : bool
        Whether to record this call.
    call_id : str, optional
        Custom ID for this call.
    layout : str
        Layout algorithm: layered, grid, spring, kamada_kawai
    direction : str, optional
        Layout direction: LR, TB, RL, BT.
    positions : dict, optional
        Manual node positions {node_id: (x, y)}.

    Returns
    -------
    dict
        Dictionary with 'renderer', 'positions', and 'artists'.
    """
    from .._diagram._native_render import DiagramRenderer
    from .._diagram._schema import DiagramSpec

    # Convert input to DiagramSpec
    if hasattr(diagram, "spec"):
        # Diagram instance
        spec = diagram.spec
    elif isinstance(diagram, DiagramSpec):
        spec = diagram
    elif isinstance(diagram, dict):
        spec = DiagramSpec.from_dict(diagram)
    else:
        raise TypeError(
            f"diagram must be Diagram, DiagramSpec, or dict, got {type(diagram)}"
        )

    # Create renderer
    renderer = DiagramRenderer(spec, layout=layout, direction=direction)

    # Use manual positions if provided
    if positions:
        renderer._positions = {k: tuple(v) for k, v in positions.items()}
        # Compute node sizes
        from .._diagram._shapes import estimate_node_bounds

        for node in spec.nodes:
            w, h = estimate_node_bounds(node.label, node.shape)
            renderer._node_sizes[node.id] = (w, h)
    else:
        renderer.compute_positions()

    # Render to axes (passing existing ax)
    renderer._render_edges(ax)
    renderer._render_nodes(ax)

    # Configure axes for diagram display
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    # Add title if specified
    if spec.title:
        from .._diagram._styles_native import FONT_CONFIG

        ax.set_title(
            spec.title,
            fontsize=FONT_CONFIG["title_size"],
            fontweight="bold",
        )

    result = {
        "renderer": renderer,
        "positions": renderer._positions,
    }

    # Record for reproducibility
    if track:
        _record_diagram_call(
            recorder,
            position,
            call_id,
            renderer,
            layout,
            direction,
        )

    return result


def _record_diagram_call(
    recorder: "Recorder",
    position: tuple,
    call_id: Optional[str],
    renderer,
    layout: str,
    direction: Optional[str],
) -> None:
    """Record diagram call for reproducibility."""
    from .._recorder import CallRecord

    final_id = call_id if call_id else recorder._generate_call_id("diagram")

    # Serialize diagram data for recipe
    diagram_data = renderer.to_dict()

    record = CallRecord(
        id=final_id,
        function="diagram",
        args=[],
        kwargs={"diagram_data": diagram_data},
        ax_position=position,
    )
    ax_record = recorder.figure_record.get_or_create_axes(*position)
    ax_record.add_call(record)


__all__ = ["diagram_plot"]
