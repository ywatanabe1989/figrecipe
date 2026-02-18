#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shaded line plots: mean+-std, mean+-CI, median+-IQR.

Ported from scitex.plt.ax._plot for figrecipe integration.
"""

from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from matplotlib.axes import Axes


def _format_sample_size(values_2d: np.ndarray) -> str:
    """Format sample size, showing range if variable due to NaN."""
    if values_2d.ndim == 1:
        return "1"
    n_per_point = np.sum(~np.isnan(values_2d), axis=0)
    n_min, n_max = int(n_per_point.min()), int(n_per_point.max())
    return str(n_min) if n_min == n_max else f"{n_min}-{n_max}"


def _plot_single_shaded_line(
    ax: Axes,
    xx: np.ndarray,
    y_lower: np.ndarray,
    y_middle: np.ndarray,
    y_upper: np.ndarray,
    color=None,
    alpha: float = 0.3,
    **kwargs,
) -> Tuple[Axes, pd.DataFrame]:
    """Plot a single line with shaded region."""
    label = kwargs.pop("label", None)
    ax.plot(xx, y_middle, color=color, alpha=alpha, label=label, **kwargs)
    fill_kw = {k: v for k, v in kwargs.items()}
    fill_kw["linewidth"] = 0
    fill_kw["edgecolor"] = "none"
    ax.fill_between(xx, y_lower, y_upper, alpha=alpha, color=color, **fill_kw)
    return ax, pd.DataFrame(
        {"x": xx, "y_lower": y_lower, "y_middle": y_middle, "y_upper": y_upper}
    )


def _plot_multi_shaded_line(
    ax: Axes,
    xs: List[np.ndarray],
    ys_lower: List[np.ndarray],
    ys_middle: List[np.ndarray],
    ys_upper: List[np.ndarray],
    color=None,
    **kwargs,
) -> Tuple[Axes, List[pd.DataFrame]]:
    """Plot multiple lines with shaded regions."""
    results = []
    colors = color
    if colors is not None and not isinstance(colors, list):
        colors = [colors] * len(xs)

    for idx, (xx, yl, ym, yu) in enumerate(zip(xs, ys_lower, ys_middle, ys_upper)):
        kw = kwargs.copy()
        if colors is not None:
            kw["color"] = colors[idx]
        _, df = _plot_single_shaded_line(ax, xx, yl, ym, yu, **kw)
        results.append(df)
    return ax, results


def stx_shaded_line(
    ax: Axes,
    xs: Union[np.ndarray, List[np.ndarray]],
    ys_lower: Union[np.ndarray, List[np.ndarray]],
    ys_middle: Union[np.ndarray, List[np.ndarray]],
    ys_upper: Union[np.ndarray, List[np.ndarray]],
    color=None,
    **kwargs,
) -> Tuple[Axes, Union[pd.DataFrame, List[pd.DataFrame]]]:
    """Plot line(s) with shaded uncertainty regions.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes.
    xs : array or list of arrays
        X values.
    ys_lower, ys_middle, ys_upper : array or list of arrays
        Lower bound, middle, and upper bound y values.
    color : color or list of colors, optional
        Line/fill colors.

    Returns
    -------
    ax : Axes
    data : DataFrame or list of DataFrames
    """
    is_single = not (
        isinstance(xs, list)
        and isinstance(ys_lower, list)
        and isinstance(ys_middle, list)
        and isinstance(ys_upper, list)
    )
    if is_single:
        return _plot_single_shaded_line(
            ax, xs, ys_lower, ys_middle, ys_upper, color=color, **kwargs
        )
    return _plot_multi_shaded_line(
        ax, xs, ys_lower, ys_middle, ys_upper, color=color, **kwargs
    )


def stx_line(ax: Axes, values_1d, xx=None, **kwargs):
    """Plot a simple line.

    Parameters
    ----------
    ax : Axes
    values_1d : array-like, shape (n_points,)
    xx : array-like, optional
        X coordinates. Default: arange.

    Returns
    -------
    ax, df : Axes, DataFrame
    """
    values_1d = np.asarray(values_1d)
    if xx is None:
        xx = np.arange(len(values_1d))
    else:
        xx = np.asarray(xx)
    ax.plot(xx, values_1d, **kwargs)
    return ax, pd.DataFrame({"x": xx, "y": values_1d})


def stx_mean_std(ax: Axes, values_2d, xx=None, sd=1, **kwargs):
    """Plot mean line with +-sd shading.

    Parameters
    ----------
    ax : Axes
    values_2d : array-like, shape (n_samples, n_points) or (n_points,)
    xx : array-like, optional
    sd : float
        Number of standard deviations. Default 1.

    Returns
    -------
    ax, data : Axes, DataFrame
    """
    values_2d = np.asarray(values_2d)
    n_pts = values_2d.shape[1] if values_2d.ndim > 1 else len(values_2d)
    if xx is None:
        xx = np.arange(n_pts)
    else:
        xx = np.asarray(xx)

    if values_2d.ndim == 1:
        central = values_2d
        error = np.zeros_like(central)
    else:
        central = np.nanmean(values_2d, axis=0)
        error = np.nanstd(values_2d, axis=0) * sd

    if "label" in kwargs and kwargs["label"]:
        n_str = _format_sample_size(values_2d)
        kwargs["label"] = f"{kwargs['label']} ($n$={n_str})"

    return stx_shaded_line(ax, xx, central - error, central, central + error, **kwargs)


def stx_mean_ci(ax: Axes, values_2d, xx=None, perc=95, **kwargs):
    """Plot mean line with confidence interval shading.

    Parameters
    ----------
    ax : Axes
    values_2d : array-like, shape (n_samples, n_points) or (n_points,)
    xx : array-like, optional
    perc : float
        Confidence interval percentage (0-100). Default 95.

    Returns
    -------
    ax, data : Axes, DataFrame
    """
    values_2d = np.asarray(values_2d)
    n_pts = values_2d.shape[1] if values_2d.ndim > 1 else len(values_2d)
    if xx is None:
        xx = np.arange(n_pts)
    else:
        xx = np.asarray(xx)

    if values_2d.ndim == 1:
        central, y_lower, y_upper = values_2d, values_2d, values_2d
    else:
        central = np.nanmean(values_2d, axis=0)
        alpha = 1 - perc / 100
        y_lower = np.nanpercentile(values_2d, alpha / 2 * 100, axis=0)
        y_upper = np.nanpercentile(values_2d, (1 - alpha / 2) * 100, axis=0)

    if "label" in kwargs and kwargs["label"]:
        n_str = _format_sample_size(values_2d)
        kwargs["label"] = f"{kwargs['label']} ($n$={n_str}, CI={perc}%)"

    return stx_shaded_line(ax, xx, y_lower, central, y_upper, **kwargs)


def stx_median_iqr(ax: Axes, values_2d, xx=None, **kwargs):
    """Plot median line with IQR (Q1-Q3) shading.

    Parameters
    ----------
    ax : Axes
    values_2d : array-like, shape (n_samples, n_points) or (n_points,)
    xx : array-like, optional

    Returns
    -------
    ax, data : Axes, DataFrame
    """
    values_2d = np.asarray(values_2d)
    n_pts = values_2d.shape[1] if values_2d.ndim > 1 else len(values_2d)
    if xx is None:
        xx = np.arange(n_pts)
    else:
        xx = np.asarray(xx)

    if values_2d.ndim == 1:
        central, y_lower, y_upper = values_2d, values_2d, values_2d
    else:
        central = np.nanmedian(values_2d, axis=0)
        y_lower = np.nanpercentile(values_2d, 25, axis=0)
        y_upper = np.nanpercentile(values_2d, 75, axis=0)

    if "label" in kwargs and kwargs["label"]:
        n_str = _format_sample_size(values_2d)
        kwargs["label"] = f"{kwargs['label']} ($n$={n_str}, IQR)"

    return stx_shaded_line(ax, xx, y_lower, central, y_upper, **kwargs)


__all__ = [
    "stx_line",
    "stx_mean_ci",
    "stx_mean_std",
    "stx_median_iqr",
    "stx_shaded_line",
]

# EOF
