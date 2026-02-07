#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagram replay functionality for recipe reproduction.

Handles reconstructing diagrams from serialized recipe data
and redrawing them using the stored positions and styling.
"""

from typing import Any

from matplotlib.axes import Axes

from .._recorder import CallRecord


def replay_diagram_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a diagram call from a recipe.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to draw on.
    call : CallRecord
        The diagram call record containing serialized diagram data.

    Returns
    -------
    dict
        Result containing renderer and positions.
    """
    from .._diagram._native_render import DiagramRenderer

    kwargs = call.kwargs.copy()
    diagram_data = kwargs.pop("diagram_data", None)

    if diagram_data is None:
        import warnings

        warnings.warn("Diagram call missing diagram_data")
        return None

    # Reconstruct renderer from serialized data
    renderer = DiagramRenderer.from_dict(diagram_data)

    # Render to axes
    renderer._render_edges(ax)
    renderer._render_nodes(ax)

    # Configure axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    # Add title if specified
    if renderer.spec.title:
        from .._diagram._styles_native import FONT_CONFIG

        ax.set_title(
            renderer.spec.title,
            fontsize=FONT_CONFIG["title_size"],
            fontweight="bold",
        )

    return {
        "renderer": renderer,
        "positions": renderer._positions,
    }


def replay_schematic_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a schematic call from a recipe.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to draw on.
    call : CallRecord
        The schematic call record containing serialized data.

    Returns
    -------
    tuple
        (figure, axes) after rendering.
    """
    from .._schematic._schematic import Schematic

    kwargs = call.kwargs.copy()
    schematic_data = kwargs.pop("schematic_data", None)

    if schematic_data is None:
        import warnings

        warnings.warn("Schematic call missing schematic_data")
        return None

    # Reconstruct schematic from serialized data
    info = Schematic.from_dict(schematic_data)

    # Render to provided axes
    fig, rendered_ax = info.render(ax=ax)

    # Resize figure to match schematic's coordinate space
    x_range = info.xlim[1] - info.xlim[0]
    y_range = info.ylim[1] - info.ylim[0]
    fig.set_size_inches(x_range / 25.4, y_range / 25.4)

    return fig, rendered_ax


__all__ = ["replay_diagram_call", "replay_schematic_call"]
