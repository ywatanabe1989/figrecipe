#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Violin plot helper functions for RecordingAxes."""

from typing import Any, Dict, List

import numpy as np


def add_violin_inner_box(
    ax,
    dataset: List,
    positions: List,
    style: Dict[str, Any],
) -> None:
    """Add box plot inside violin.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    dataset : array-like
        Data arrays for each violin.
    positions : array-like
        X positions of violins.
    style : dict
        Violin style configuration.
    """
    from ..styles._style_applier import mm_to_pt

    whisker_lw = mm_to_pt(style.get("whisker_mm", 0.2))
    median_size = mm_to_pt(style.get("median_mm", 0.8))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        q1, median, q3 = np.percentile(data, [25, 50, 75])
        iqr = q3 - q1
        whisker_low = max(data.min(), q1 - 1.5 * iqr)
        whisker_high = min(data.max(), q3 + 1.5 * iqr)

        # Draw box (Q1 to Q3)
        ax.vlines(pos, q1, q3, colors="black", linewidths=whisker_lw, zorder=3)
        # Draw whiskers
        ax.vlines(
            pos,
            whisker_low,
            q1,
            colors="black",
            linewidths=whisker_lw * 0.5,
            zorder=3,
        )
        ax.vlines(
            pos,
            q3,
            whisker_high,
            colors="black",
            linewidths=whisker_lw * 0.5,
            zorder=3,
        )
        # Draw median as a white dot with black edge
        ax.scatter(
            [pos],
            [median],
            s=median_size**2,
            c="white",
            edgecolors="black",
            linewidths=whisker_lw,
            zorder=4,
        )


def add_violin_inner_swarm(
    ax,
    dataset: List,
    positions: List,
    style: Dict[str, Any],
) -> None:
    """Add swarm points inside violin.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    dataset : array-like
        Data arrays for each violin.
    positions : array-like
        X positions of violins.
    style : dict
        Violin style configuration.
    """
    from ..styles._style_applier import mm_to_pt

    point_size = mm_to_pt(style.get("median_mm", 0.8))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        n = len(data)

        # Simple swarm: jitter x positions
        jitter = np.random.default_rng(42).uniform(-0.15, 0.15, n)
        x_positions = pos + jitter

        ax.scatter(x_positions, data, s=point_size**2, c="black", alpha=0.5, zorder=3)


def add_violin_inner_stick(
    ax,
    dataset: List,
    positions: List,
    style: Dict[str, Any],
) -> None:
    """Add stick (line) markers inside violin for each data point.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    dataset : array-like
        Data arrays for each violin.
    positions : array-like
        X positions of violins.
    style : dict
        Violin style configuration.
    """
    from ..styles._style_applier import mm_to_pt

    lw = mm_to_pt(style.get("whisker_mm", 0.2))

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        # Draw short horizontal lines at each data point
        for val in data:
            ax.hlines(
                val,
                pos - 0.05,
                pos + 0.05,
                colors="black",
                linewidths=lw * 0.5,
                alpha=0.3,
                zorder=3,
            )


def add_violin_inner_point(
    ax,
    dataset: List,
    positions: List,
    style: Dict[str, Any],
) -> None:
    """Add point markers inside violin for each data point.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to draw on.
    dataset : array-like
        Data arrays for each violin.
    positions : array-like
        X positions of violins.
    style : dict
        Violin style configuration.
    """
    from ..styles._style_applier import mm_to_pt

    point_size = mm_to_pt(style.get("median_mm", 0.8)) * 0.5

    for data, pos in zip(dataset, positions):
        data = np.asarray(data)
        x_positions = np.full_like(data, pos)
        ax.scatter(x_positions, data, s=point_size**2, c="black", alpha=0.3, zorder=3)


__all__ = [
    "add_violin_inner_box",
    "add_violin_inner_swarm",
    "add_violin_inner_stick",
    "add_violin_inner_point",
]

# EOF
