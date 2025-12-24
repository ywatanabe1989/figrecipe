#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eventplot: event/spike raster demo."""


def plot_eventplot(plt, rng, ax=None):
    """Event/spike raster demo.

    Demonstrates: ax.eventplot()
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Multiple event sequences
    events = [rng.uniform(0, 10, 20) for _ in range(5)]
    ax.eventplot(events, id="eventplot")
    ax.set_xlabel("Time")
    ax.set_ylabel("Channel")
    ax.set_title("eventplot")
    return fig, ax


# EOF
