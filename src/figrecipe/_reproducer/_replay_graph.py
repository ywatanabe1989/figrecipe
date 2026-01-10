#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Graph replay functionality for recipe reproduction.

Handles reconstructing NetworkX graphs from serialized recipe data
and redrawing them using the stored styling parameters.
"""

from typing import Any

from matplotlib.axes import Axes

from .._recorder import CallRecord


def replay_graph_call(ax: Axes, call: CallRecord) -> Any:
    """Replay a graph call from a recipe.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to draw on.
    call : CallRecord
        The graph call record containing serialized graph data.

    Returns
    -------
    dict
        Result from draw_graph containing positions and collections.
    """
    try:
        from .._graph import draw_graph, record_to_graph
    except ImportError:
        import warnings

        warnings.warn(
            "networkx is required to reproduce graph plots. "
            "Install with: pip install figrecipe[graph]"
        )
        return None

    kwargs = call.kwargs.copy()
    graph_data = kwargs.pop("graph_data", None)

    if graph_data is None:
        import warnings

        warnings.warn("Graph call missing graph_data")
        return None

    # Reconstruct graph from serialized data
    G, pos, style = record_to_graph(graph_data)

    # Merge stored style with any explicit kwargs
    draw_kwargs = style.copy()
    draw_kwargs.update(kwargs)

    # Use stored positions if available
    if pos:
        draw_kwargs["pos"] = pos

    # Draw the graph
    return draw_graph(ax, G, **draw_kwargs)


# EOF
