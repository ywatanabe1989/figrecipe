#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eventplot: event/spike raster demo."""

from figrecipe.styles import load_style


def plot_eventplot(plt, rng, ax=None):
    """Event/spike raster demo with multiple channels and legend.

    Demonstrates: ax.eventplot() with SCITEX color palette and legend
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Get SCITEX color palette
    style = load_style()
    palette = style.get("colors", {}).get("palette", [])
    colors = [tuple(v / 255.0 for v in c) for c in palette[:3]]

    # Multiple named event sequences with legend
    channels = [
        ("Neuron A", rng.uniform(0, 10, 20)),
        ("Neuron B", rng.uniform(0, 10, 15)),
        ("Neuron C", rng.uniform(0, 10, 25)),
    ]

    for i, ((label, events), color) in enumerate(zip(channels, colors)):
        ax.eventplot(
            [events], lineoffsets=i, colors=[color], label=label, id=f"event_{label}"
        )

    ax.set_xlabel("Time")
    ax.set_ylabel("Channel")
    ax.set_title("eventplot")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels([c[0] for c in channels])
    ax.legend()
    return fig, ax


# EOF
