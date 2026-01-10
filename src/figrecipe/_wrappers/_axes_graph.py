#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Graph visualization method implementation for RecordingAxes."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from matplotlib.axes import Axes

    from .._recorder import Recorder


# Default graph styling values
GRAPH_DEFAULTS = {
    "layout": "spring",
    "node_size": 100,
    "node_color": "#3498db",
    "node_alpha": 0.8,
    "node_shape": "o",
    "node_edgecolors": "white",
    "node_linewidths": 0.5,
    "edge_width": 1.0,
    "edge_color": "gray",
    "edge_alpha": 0.4,
    "edge_style": "solid",
    "arrowsize": 10,
    "arrowstyle": "-|>",
    "connectionstyle": "arc3,rad=0.0",
    "labels": False,
    "font_size": 6,
    "font_color": "black",
    "font_weight": "normal",
    "font_family": "sans-serif",
    "colormap": "viridis",
}


def graph_plot(
    ax: "Axes",
    G,
    recorder: "Recorder",
    position: tuple,
    track: bool,
    call_id: Optional[str],
    *,
    preset: Optional[str] = None,
    pos=None,
    seed: int = 42,
    # Explicit styling overrides
    layout: Optional[str] = None,
    node_size=None,
    node_color=None,
    node_alpha: Optional[float] = None,
    node_shape: Optional[str] = None,
    node_edgecolors: Optional[str] = None,
    node_linewidths: Optional[float] = None,
    edge_width=None,
    edge_color=None,
    edge_alpha: Optional[float] = None,
    edge_style: Optional[str] = None,
    arrows=None,
    arrowsize: Optional[float] = None,
    arrowstyle: Optional[str] = None,
    connectionstyle: Optional[str] = None,
    labels=None,
    font_size: Optional[float] = None,
    font_color: Optional[str] = None,
    font_weight: Optional[str] = None,
    font_family: Optional[str] = None,
    colormap: Optional[str] = None,
    vmin=None,
    vmax=None,
    **layout_kwargs,
) -> Dict[str, Any]:
    """Draw a NetworkX graph with publication-quality styling.

    Returns
    -------
    dict
        Dictionary with 'pos', 'node_collection', 'edge_collection'.
    """
    from .._graph import draw_graph

    # Build kwargs from defaults -> preset -> explicit args
    kwargs = _build_graph_kwargs(
        preset=preset,
        layout=layout,
        node_size=node_size,
        node_color=node_color,
        node_alpha=node_alpha,
        node_shape=node_shape,
        node_edgecolors=node_edgecolors,
        node_linewidths=node_linewidths,
        edge_width=edge_width,
        edge_color=edge_color,
        edge_alpha=edge_alpha,
        edge_style=edge_style,
        arrows=arrows,
        arrowsize=arrowsize,
        arrowstyle=arrowstyle,
        connectionstyle=connectionstyle,
        labels=labels,
        font_size=font_size,
        font_color=font_color,
        font_weight=font_weight,
        font_family=font_family,
        colormap=colormap,
        vmin=vmin,
        vmax=vmax,
    )

    # Draw the graph
    result = draw_graph(
        ax,
        G,
        pos=pos,
        seed=seed,
        **kwargs,
        **layout_kwargs,
    )

    # Record for reproducibility
    if track:
        _record_graph_call(
            recorder,
            position,
            call_id,
            G,
            result,
            kwargs,
            seed,
            preset,
        )

    return result


def _build_graph_kwargs(
    preset: Optional[str] = None,
    **explicit_kwargs,
) -> Dict[str, Any]:
    """Build graph kwargs from defaults, preset, and explicit overrides."""
    from .._graph_presets import get_preset

    # Start with defaults
    kwargs = GRAPH_DEFAULTS.copy()

    # Overlay preset values
    if preset:
        preset_kwargs = get_preset(preset)
        kwargs.update(preset_kwargs)

    # Overlay explicit args (only if not None)
    for key, value in explicit_kwargs.items():
        if value is not None:
            kwargs[key] = value

    return kwargs


def _record_graph_call(
    recorder: "Recorder",
    position: tuple,
    call_id: Optional[str],
    G,
    result: Dict[str, Any],
    kwargs: Dict[str, Any],
    seed: int,
    preset: Optional[str],
) -> None:
    """Record graph call for reproducibility."""
    from .._graph import graph_to_record
    from .._recorder import CallRecord

    final_id = call_id if call_id else recorder._generate_call_id("graph")

    # Build style kwargs for recording (replace callables with marker)
    record_style = kwargs.copy()
    record_style["seed"] = seed
    record_style["preset"] = preset
    for key in ["node_size", "node_color", "edge_width", "edge_color"]:
        if callable(record_style.get(key)):
            record_style[key] = "custom"

    # Serialize graph data for recipe
    graph_record = graph_to_record(G, pos=result["pos"], **record_style)

    record = CallRecord(
        id=final_id,
        function="graph",
        args=[],
        kwargs={"graph_data": graph_record},
        ax_position=position,
    )
    ax_record = recorder.figure_record.get_or_create_axes(*position)
    ax_record.add_call(record)


# EOF
