#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Statistical specialized plots: ECDF and shaded line plots."""

__all__ = ["ecdf", "shaded_line"]

import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from matplotlib.axes import Axes


def ecdf(
    ax: Axes,
    values: np.ndarray,
    **kwargs: Any,
) -> Tuple[Axes, Dict[str, np.ndarray]]:
    """Plot Empirical Cumulative Distribution Function (ECDF).

    The ECDF shows the proportion of data points less than or equal to each
    value, representing the empirical estimate of the cumulative distribution.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Matplotlib axis to plot on.
    values : array-like, shape (n_samples,)
        1D array of values to compute and plot ECDF for.
        NaN values are automatically ignored.
    **kwargs : dict
        Additional arguments passed to plot function.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the ECDF plot.
    data : dict
        Dictionary containing ECDF data:
        - x: sorted data values
        - y: cumulative percentages (0-100)
        - n: total number of data points
        - x_step, y_step: step plot coordinates

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> data = np.random.randn(100)
    >>> fig, ax = fr.subplots()
    >>> ax, ecdf_data = fr.ecdf(ax, data)
    """
    # Unwrap recording axes if needed
    mpl_ax = ax._ax if hasattr(ax, "_ax") else ax

    # Flatten and handle NaN values
    values = np.asarray(values).ravel()

    if np.isnan(values).any():
        warnings.warn("NaN values are ignored for ECDF plot.", stacklevel=2)
    values = values[~np.isnan(values)]
    n_samples = len(values)

    if n_samples == 0:
        warnings.warn("No valid data points for ECDF plot.", stacklevel=2)
        return ax, {"x": np.array([]), "y": np.array([]), "n": 0}

    # Sort data and compute ECDF values
    data_sorted = np.sort(values)
    ecdf_perc = 100 * np.arange(1, n_samples + 1) / n_samples

    # Create step coordinates
    x_step = np.repeat(data_sorted, 2)[1:]
    y_step = np.repeat(ecdf_perc, 2)[:-1]

    # Apply default linewidth if not specified
    if "linewidth" not in kwargs and "lw" not in kwargs:
        kwargs["linewidth"] = 0.2 * 2.83465  # 0.2mm in points

    # Add sample size to label if provided
    if "label" in kwargs and kwargs["label"]:
        kwargs["label"] = f"{kwargs['label']} ($n$={n_samples})"

    # Plot ECDF using steps
    mpl_ax.plot(x_step, y_step, drawstyle="steps-post", **kwargs)

    # Set y-axis limits
    mpl_ax.set_ylim(0, 100)

    # Return data dictionary
    data = {
        "x": data_sorted,
        "y": ecdf_perc,
        "n": n_samples,
        "x_step": x_step,
        "y_step": y_step,
    }

    return ax, data


def shaded_line(
    ax: Axes,
    x: Union[np.ndarray, List[np.ndarray]],
    y_lower: Union[np.ndarray, List[np.ndarray]],
    y_middle: Union[np.ndarray, List[np.ndarray]],
    y_upper: Union[np.ndarray, List[np.ndarray]],
    color: Optional[Union[str, List[str]]] = None,
    alpha: float = 0.3,
    **kwargs: Any,
) -> Tuple[Axes, Union[Dict, List[Dict]]]:
    """Plot line(s) with shaded uncertainty regions.

    Useful for plotting mean/median with confidence intervals or standard
    deviation bands.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on.
    x : np.ndarray or list of np.ndarray
        X values (single array or list for multiple lines).
    y_lower : np.ndarray or list of np.ndarray
        Lower bound y values.
    y_middle : np.ndarray or list of np.ndarray
        Middle (mean/median) y values.
    y_upper : np.ndarray or list of np.ndarray
        Upper bound y values.
    color : str or list of str, optional
        Color(s) for lines and shaded regions.
    alpha : float, default 0.3
        Transparency for shaded region.
    **kwargs : dict
        Additional keyword arguments passed to plot().

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot(s).
    data : dict or list of dict
        Dictionary/dictionaries with plot data (x, y_lower, y_middle, y_upper).

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> x = np.linspace(0, 10, 100)
    >>> y_mean = np.sin(x)
    >>> y_std = 0.2
    >>> fig, ax = fr.subplots()
    >>> ax, data = fr.shaded_line(
    ...     ax, x, y_mean - y_std, y_mean, y_mean + y_std,
    ...     color='blue', alpha=0.3
    ... )
    """
    # Check if single or multiple lines
    is_single = not (
        isinstance(x, list)
        and isinstance(y_lower, list)
        and isinstance(y_middle, list)
        and isinstance(y_upper, list)
    )

    if is_single:
        return _plot_single_shaded_line(
            ax, x, y_lower, y_middle, y_upper, color=color, alpha=alpha, **kwargs
        )
    else:
        return _plot_multiple_shaded_lines(
            ax, x, y_lower, y_middle, y_upper, color=color, alpha=alpha, **kwargs
        )


def _plot_single_shaded_line(
    ax: Axes,
    x: np.ndarray,
    y_lower: np.ndarray,
    y_middle: np.ndarray,
    y_upper: np.ndarray,
    color: Optional[str] = None,
    alpha: float = 0.3,
    **kwargs: Any,
) -> Tuple[Axes, Dict[str, np.ndarray]]:
    """Plot a single line with shaded area."""
    # Unwrap recording axes if needed
    mpl_ax = ax._ax if hasattr(ax, "_ax") else ax

    # Convert to arrays
    x = np.asarray(x)
    y_lower = np.asarray(y_lower)
    y_middle = np.asarray(y_middle)
    y_upper = np.asarray(y_upper)

    # Validate lengths
    if not (len(x) == len(y_middle) == len(y_lower) == len(y_upper)):
        raise ValueError("All arrays must have the same length")

    # Extract label for legend
    label = kwargs.pop("label", None)

    # Plot the middle line
    mpl_ax.plot(x, y_middle, color=color, alpha=1.0, label=label, **kwargs)

    # Plot the shaded region
    fill_kwargs = {k: v for k, v in kwargs.items() if k not in ["linewidth", "lw"]}
    mpl_ax.fill_between(
        x, y_lower, y_upper, alpha=alpha, color=color, edgecolor="none", **fill_kwargs
    )

    # Return data
    data = {
        "x": x,
        "y_lower": y_lower,
        "y_middle": y_middle,
        "y_upper": y_upper,
    }

    return ax, data


def _plot_multiple_shaded_lines(
    ax: Axes,
    xs: List[np.ndarray],
    ys_lower: List[np.ndarray],
    ys_middle: List[np.ndarray],
    ys_upper: List[np.ndarray],
    color: Optional[Union[str, List[str]]] = None,
    alpha: float = 0.3,
    **kwargs: Any,
) -> Tuple[Axes, List[Dict[str, np.ndarray]]]:
    """Plot multiple lines with shaded areas."""
    # Validate input lengths
    n_lines = len(xs)
    if not (len(ys_lower) == len(ys_middle) == len(ys_upper) == n_lines):
        raise ValueError("All input lists must have the same length")

    # Handle colors
    if color is None:
        colors = [None] * n_lines
    elif isinstance(color, str):
        colors = [color] * n_lines
    else:
        if len(color) != n_lines:
            raise ValueError("Number of colors must match number of lines")
        colors = color

    # Plot each line
    results = []
    for i, (x, y_lo, y_mid, y_up) in enumerate(zip(xs, ys_lower, ys_middle, ys_upper)):
        line_kwargs = kwargs.copy()
        _, data = _plot_single_shaded_line(
            ax, x, y_lo, y_mid, y_up, color=colors[i], alpha=alpha, **line_kwargs
        )
        results.append(data)

    return ax, results


def mean_std_line(
    ax: Axes,
    x: np.ndarray,
    y_samples: np.ndarray,
    axis: int = 0,
    n_std: float = 1.0,
    **kwargs: Any,
) -> Tuple[Axes, Dict[str, np.ndarray]]:
    """Plot mean with standard deviation bands.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on.
    x : np.ndarray
        X values.
    y_samples : np.ndarray, shape (n_samples, n_points) or (n_points, n_samples)
        2D array of samples to compute mean and std from.
    axis : int, default 0
        Axis along which to compute mean/std.
    n_std : float, default 1.0
        Number of standard deviations for the shaded region.
    **kwargs : dict
        Additional arguments passed to shaded_line().

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot.
    data : dict
        Dictionary with x, y_lower, y_middle, y_upper, std, n_samples.
    """
    y_samples = np.asarray(y_samples)
    y_mean = np.mean(y_samples, axis=axis)
    y_std = np.std(y_samples, axis=axis)

    y_lower = y_mean - n_std * y_std
    y_upper = y_mean + n_std * y_std

    ax, data = shaded_line(ax, x, y_lower, y_mean, y_upper, **kwargs)

    # Add additional stats
    data["std"] = y_std
    data["n_samples"] = y_samples.shape[axis]

    return ax, data


def mean_ci_line(
    ax: Axes,
    x: np.ndarray,
    y_samples: np.ndarray,
    axis: int = 0,
    ci: float = 95.0,
    **kwargs: Any,
) -> Tuple[Axes, Dict[str, np.ndarray]]:
    """Plot mean with confidence interval bands.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on.
    x : np.ndarray
        X values.
    y_samples : np.ndarray, shape (n_samples, n_points) or (n_points, n_samples)
        2D array of samples.
    axis : int, default 0
        Axis along which to compute statistics.
    ci : float, default 95.0
        Confidence interval percentage (e.g., 95 for 95% CI).
    **kwargs : dict
        Additional arguments passed to shaded_line().

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot.
    data : dict
        Dictionary with x, y_lower, y_middle, y_upper, ci, n_samples.
    """
    y_samples = np.asarray(y_samples)
    y_mean = np.mean(y_samples, axis=axis)

    # Calculate percentiles for CI
    lower_pct = (100 - ci) / 2
    upper_pct = 100 - lower_pct

    y_lower = np.percentile(y_samples, lower_pct, axis=axis)
    y_upper = np.percentile(y_samples, upper_pct, axis=axis)

    ax, data = shaded_line(ax, x, y_lower, y_mean, y_upper, **kwargs)

    # Add additional stats
    data["ci"] = ci
    data["n_samples"] = y_samples.shape[axis]

    return ax, data


def median_iqr_line(
    ax: Axes,
    x: np.ndarray,
    y_samples: np.ndarray,
    axis: int = 0,
    **kwargs: Any,
) -> Tuple[Axes, Dict[str, np.ndarray]]:
    """Plot median with interquartile range bands.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes to plot on.
    x : np.ndarray
        X values.
    y_samples : np.ndarray
        2D array of samples.
    axis : int, default 0
        Axis along which to compute statistics.
    **kwargs : dict
        Additional arguments passed to shaded_line().

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot.
    data : dict
        Dictionary with x, y_lower, y_middle, y_upper, n_samples.
    """
    y_samples = np.asarray(y_samples)
    y_median = np.median(y_samples, axis=axis)
    y_lower = np.percentile(y_samples, 25, axis=axis)
    y_upper = np.percentile(y_samples, 75, axis=axis)

    ax, data = shaded_line(ax, x, y_lower, y_median, y_upper, **kwargs)

    # Add additional stats
    data["n_samples"] = y_samples.shape[axis]

    return ax, data


# EOF
