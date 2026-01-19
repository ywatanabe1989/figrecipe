#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Neuroscience specialized plots: raster plots for spike data."""

__all__ = ["raster"]

from bisect import bisect_left
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes


def raster(
    ax: Axes,
    spike_times: List[np.ndarray],
    time: Optional[np.ndarray] = None,
    labels: Optional[List[str]] = None,
    colors: Optional[List[str]] = None,
    orientation: str = "horizontal",
    y_offset: Optional[float] = None,
    lineoffsets: Optional[np.ndarray] = None,
    linelengths: Optional[float] = None,
    n_xticks: int = 4,
    **kwargs: Any,
) -> Tuple[Axes, Dict[str, Any]]:
    """Create a spike raster plot using eventplot.

    Visualizes spike timing data where each row represents a trial or neuron,
    and vertical lines indicate spike occurrences.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes on which to draw the raster plot.
    spike_times : list of array-like, shape (n_trials,)
        List of spike/event time arrays, one per trial/channel.
        Each element is an array of spike times.
    time : array-like, optional
        Time indices for digitizing events (for return data).
    labels : list of str, optional
        Labels for each channel/trial.
    colors : list, optional
        Colors for each channel/trial.
    orientation : str, optional
        Orientation: "horizontal" (default) or "vertical".
    y_offset : float, optional
        Vertical spacing between trials/channels (default: 1.0).
    lineoffsets : array-like, optional
        Y-positions for each trial/channel (overrides automatic positioning).
    linelengths : float, optional
        Height of each spike mark (default: 0.8 * y_offset).
    n_xticks : int, optional
        Number of x-axis ticks (default: 4).
    **kwargs : dict
        Additional keyword arguments for eventplot.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the raster plot.
    data : dict
        Dictionary containing:
        - spike_times: the input spike times
        - digital: digitized spike matrix (n_trials x n_timepoints)
        - time: time indices

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> # Generate random spike times for 10 neurons
    >>> np.random.seed(42)
    >>> spike_times = [
    ...     np.sort(np.random.choice(1000, np.random.randint(10, 50), replace=False))
    ...     for _ in range(10)
    ... ]
    >>> fig, ax = fr.subplots()
    >>> ax, data = fr.raster(ax, spike_times)
    """
    # Unwrap recording axes if needed
    mpl_ax = ax._ax if hasattr(ax, "_ax") else ax

    # Ensure spike_times is properly formatted
    spike_times = _ensure_list(spike_times)
    n_trials = len(spike_times)

    # Handle colors
    colors = _handle_colors(colors, n_trials)

    # Handle vertical positioning
    if y_offset is None:
        y_offset = 1.0
    if lineoffsets is None:
        lineoffsets = np.arange(n_trials) * y_offset

    # Ensure lineoffsets matches spike_times length
    lineoffsets = _ensure_lineoffsets(lineoffsets, n_trials)

    # Set linelengths to prevent overlap
    if linelengths is None:
        linelengths = y_offset * 0.8

    # Add sample size to label if provided
    if kwargs.get("label"):
        kwargs["label"] = f"{kwargs['label']} ($n$={n_trials})"

    # Plot each trial
    for i, (spikes, color, offset) in enumerate(zip(spike_times, colors, lineoffsets)):
        label = _get_label(labels, i)
        mpl_ax.eventplot(
            spikes,
            lineoffsets=offset,
            linelengths=linelengths,
            orientation=orientation,
            colors=color,
            label=label,
            **kwargs,
        )

    # Set axis labels if provided
    if labels is not None:
        mpl_ax.legend()

    # Create digitized output
    digital_data, time_out = _spike_times_to_digital(spike_times, time, lineoffsets)

    # Return data
    data = {
        "spike_times": spike_times,
        "digital": digital_data,
        "time": time_out,
        "n_trials": n_trials,
    }

    return ax, data


def _ensure_list(spike_times: List) -> List[np.ndarray]:
    """Ensure each element is an array-like of spike times."""
    result = []
    for spikes in spike_times:
        if isinstance(spikes, (int, float)):
            result.append([spikes])
        else:
            result.append(np.asarray(spikes))
    return result


def _handle_colors(colors: Optional[List], n_trials: int) -> List:
    """Handle color specification for raster plot."""
    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    if len(colors) < n_trials:
        colors = colors * (n_trials // len(colors) + 1)
    return colors[:n_trials]


def _ensure_lineoffsets(lineoffsets: np.ndarray, n_trials: int) -> np.ndarray:
    """Ensure lineoffsets has correct length."""
    lineoffsets = np.asarray(lineoffsets)
    if len(lineoffsets) < n_trials:
        extra = np.arange(len(lineoffsets), n_trials)
        lineoffsets = np.concatenate([lineoffsets, extra])
    return lineoffsets[:n_trials]


def _get_label(labels: Optional[List[str]], idx: int) -> Optional[str]:
    """Get label for a specific trial."""
    if labels is not None and idx < len(labels):
        return labels[idx]
    return None


def _spike_times_to_digital(
    spike_times: List[np.ndarray],
    time: Optional[np.ndarray],
    lineoffsets: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Convert spike times to digital matrix.

    Parameters
    ----------
    spike_times : list of arrays
        Spike times for each trial.
    time : array or None
        Time indices. If None, creates linspace from 0 to max spike time.
    lineoffsets : array
        Y-positions for each trial.

    Returns
    -------
    digital : np.ndarray, shape (n_trials, n_timepoints)
        Digital matrix with spike positions.
    time : np.ndarray
        Time indices used.
    """
    # Determine time range
    all_spikes = [s for spikes in spike_times for s in spikes if len(spikes) > 0]
    if len(all_spikes) == 0:
        max_time = 1.0
    else:
        max_time = max(all_spikes)

    if time is None:
        time = np.linspace(0, max_time, 1000)
    else:
        time = np.asarray(time)

    n_trials = len(spike_times)
    n_timepoints = len(time)

    # Create digital matrix (NaN for no spike)
    digital = np.full((n_trials, n_timepoints), np.nan, dtype=float)

    for i_trial, spikes in enumerate(spike_times):
        for spike_time in spikes:
            # Find insertion point
            idx = bisect_left(time, spike_time)
            if idx >= n_timepoints:
                idx = n_timepoints - 1
            # Use lineoffset position
            if i_trial < len(lineoffsets):
                digital[i_trial, idx] = lineoffsets[i_trial]
            else:
                digital[i_trial, idx] = i_trial

    return digital, time


# EOF
