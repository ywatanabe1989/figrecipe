#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heatmap and confusion matrix specialized plots."""

__all__ = ["heatmap", "conf_mat"]

from typing import Any, List, Optional, Tuple, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.image import AxesImage


def heatmap(
    ax: Axes,
    values_2d: np.ndarray,
    x_labels: Optional[List[str]] = None,
    y_labels: Optional[List[str]] = None,
    cmap: str = "viridis",
    cbar_label: str = "",
    annot_format: str = "{x:.1f}",
    show_annot: bool = True,
    annot_color_light: str = "black",
    annot_color_dark: str = "white",
    **kwargs: Any,
) -> Tuple[Axes, AxesImage, Optional[Colorbar]]:
    """Plot an annotated heatmap with automatic annotation color switching.

    Creates a heatmap visualization with optional cell annotations. Annotation
    text colors are automatically switched based on background brightness for
    optimal readability.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to plot on.
    values_2d : np.ndarray, shape (n_rows, n_cols)
        2D array of data to display as heatmap.
    x_labels : list of str, optional
        Labels for the x-axis (columns).
    y_labels : list of str, optional
        Labels for the y-axis (rows).
    cmap : str, default "viridis"
        Colormap name to use.
    cbar_label : str, default ""
        Label for the colorbar.
    annot_format : str, default "{x:.1f}"
        Format string for cell annotations.
    show_annot : bool, default True
        Whether to annotate the heatmap with values.
    annot_color_light : str, default "black"
        Text color for annotations on lighter backgrounds.
    annot_color_dark : str, default "white"
        Text color for annotations on darker backgrounds.
    **kwargs : dict
        Additional keyword arguments passed to imshow().

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the heatmap.
    im : matplotlib.image.AxesImage
        The image object created by imshow.
    cbar : matplotlib.colorbar.Colorbar or None
        The colorbar object (None if no colorbar).

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> data = np.random.rand(5, 10)
    >>> fig, ax = fr.subplots()
    >>> ax, im, cbar = fr.heatmap(
    ...     ax, data,
    ...     x_labels=[f"X{i}" for i in range(10)],
    ...     y_labels=[f"Y{i}" for i in range(5)],
    ...     cmap="Blues"
    ... )
    """
    # Unwrap recording axes if needed
    mpl_ax = ax._ax if hasattr(ax, "_ax") else ax

    # Create heatmap
    im = mpl_ax.imshow(values_2d, cmap=cmap, **kwargs)

    # Add colorbar
    cbar = mpl_ax.figure.colorbar(im, ax=mpl_ax)
    if cbar_label:
        cbar.ax.set_ylabel(cbar_label, rotation=-90, va="bottom")

    # Style colorbar
    _style_colorbar(cbar)

    # Set tick labels
    _set_heatmap_ticks(mpl_ax, values_2d, x_labels, y_labels)

    # Configure axes appearance
    _configure_heatmap_axes(mpl_ax, values_2d)

    # Add annotations if requested
    if show_annot:
        text_colors = _get_annotation_colors(cmap, annot_color_light, annot_color_dark)
        _annotate_heatmap(im, values_2d, annot_format, text_colors)

    return ax, im, cbar


def conf_mat(
    ax: Axes,
    conf_mat_2d: np.ndarray,
    x_labels: Optional[List[str]] = None,
    y_labels: Optional[List[str]] = None,
    title: str = "Confusion Matrix",
    cmap: str = "Blues",
    label_rotation: Tuple[float, float] = (15, 15),
    calc_bacc: bool = True,
    **kwargs: Any,
) -> Union[Axes, Tuple[Axes, float]]:
    """Create a confusion matrix heatmap with optional balanced accuracy.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Matplotlib axes to plot on.
    conf_mat_2d : np.ndarray, shape (n_classes, n_classes)
        2D confusion matrix data (true labels x predicted labels).
    x_labels : list of str, optional
        Labels for predicted classes.
    y_labels : list of str, optional
        Labels for true classes.
    title : str, optional
        Plot title.
    cmap : str, optional
        Colormap name.
    label_rotation : tuple of float, optional
        (x, y) label rotation angles.
    calc_bacc : bool, optional
        Whether to calculate and return balanced accuracy.
    **kwargs : dict
        Additional arguments passed to imshow().

    Returns
    -------
    ax : matplotlib.axes.Axes
        Axes with the confusion matrix.
    bacc : float, optional
        Balanced accuracy (if calc_bacc=True).

    Examples
    --------
    >>> import figrecipe as fr
    >>> import numpy as np
    >>> data = np.array([[45, 5, 2], [3, 42, 8], [1, 6, 48]])
    >>> fig, ax = fr.subplots()
    >>> ax, bacc = fr.conf_mat(ax, data, x_labels=['A','B','C'],
    ...                        y_labels=['X','Y','Z'], calc_bacc=True)
    >>> print(f"Balanced Accuracy: {bacc:.3f}")
    """
    # Unwrap recording axes if needed
    mpl_ax = ax._ax if hasattr(ax, "_ax") else ax

    # Calculate balanced accuracy
    bacc_val = _calc_balanced_accuracy(conf_mat_2d)
    display_title = f"{title} (bACC = {bacc_val:.3f})" if calc_bacc else title

    # Plot heatmap
    mpl_ax.imshow(conf_mat_2d, cmap=cmap, vmin=0, **kwargs)

    # Add annotations (integer format for counts)
    n_rows, n_cols = conf_mat_2d.shape
    text_colors = _get_annotation_colors(cmap, "black", "white")
    threshold = np.max(conf_mat_2d) * 0.7

    for i in range(n_rows):
        for j in range(n_cols):
            val = conf_mat_2d[i, j]
            color = text_colors[1] if val > threshold else text_colors[0]
            mpl_ax.text(
                j,
                i,
                f"{int(val):,d}",
                ha="center",
                va="center",
                color=color,
                fontsize=6,
            )

    # Set labels
    mpl_ax.set_xlabel("Predicted label")
    mpl_ax.set_ylabel("True label")
    mpl_ax.set_title(display_title)

    # Set tick labels
    if x_labels is not None:
        mpl_ax.set_xticks(range(n_cols))
        mpl_ax.set_xticklabels(x_labels, rotation=label_rotation[0], ha="right")
    if y_labels is not None:
        mpl_ax.set_yticks(range(n_rows))
        mpl_ax.set_yticklabels(y_labels, rotation=label_rotation[1], ha="right")

    # Set aspect ratio for square cells
    if n_rows == n_cols:
        mpl_ax.set_aspect("equal", adjustable="box")

    if calc_bacc:
        return ax, bacc_val
    return ax


def _style_colorbar(cbar: Colorbar) -> None:
    """Apply consistent styling to colorbar."""
    from matplotlib.ticker import MaxNLocator

    cbar.outline.set_linewidth(0.2 * 2.83465)  # 0.2mm in points
    cbar.ax.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=3))
    cbar.ax.tick_params(width=0.2 * 2.83465, length=0.8 * 2.83465)


def _set_heatmap_ticks(
    ax: Axes,
    data: np.ndarray,
    x_labels: Optional[List[str]],
    y_labels: Optional[List[str]],
) -> None:
    """Set tick labels for heatmap."""
    n_rows, n_cols = data.shape

    if x_labels is not None:
        ax.set_xticks(range(n_cols))
        ax.set_xticklabels(x_labels)
    else:
        ax.set_xticks(range(n_cols))

    if y_labels is not None:
        ax.set_yticks(range(n_rows))
        ax.set_yticklabels(y_labels)
    else:
        ax.set_yticks(range(n_rows))


def _configure_heatmap_axes(ax: Axes, data: np.ndarray) -> None:
    """Configure axes appearance for heatmap."""
    n_rows, n_cols = data.shape

    # Show all 4 spines
    for spine in ax.spines.values():
        spine.set_visible(True)

    # Set aspect ratio for square cells
    ax.set_aspect("equal", adjustable="box")

    # Configure tick positions
    ax.tick_params(top=False, bottom=True, labeltop=False, labelbottom=True)

    # Add minor ticks for grid lines
    ax.set_xticks(np.arange(n_cols + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n_rows + 1) - 0.5, minor=True)
    ax.tick_params(which="minor", bottom=False, left=False)


def _get_annotation_colors(
    cmap: str, color_light: str, color_dark: str
) -> Tuple[str, str]:
    """Determine annotation colors based on colormap brightness.

    Uses ITU-R BT.709 coefficients for perceived brightness.
    """
    cmap_obj = plt.get_cmap(cmap)

    # Sample at low value
    dark_color = cmap_obj(0.1)
    dark_brightness = (
        0.2126 * dark_color[0] + 0.7152 * dark_color[1] + 0.0722 * dark_color[2]
    )

    if dark_brightness < 0.5:
        return (color_light, color_dark)
    else:
        return (color_dark, color_light)


def _calc_annotation_fontsize(n_rows: int, n_cols: int) -> float:
    """Calculate dynamic annotation font size based on cell count."""
    max_dim = max(n_rows, n_cols)

    if max_dim <= 5:
        return 6.0
    elif max_dim <= 10:
        return 6.0 - (max_dim - 5) * 0.2
    elif max_dim <= 20:
        return 5.0 - (max_dim - 10) * 0.1
    else:
        return max(3.0, 4.0 - (max_dim - 20) * 0.05)


def _annotate_heatmap(
    im: AxesImage, data: np.ndarray, valfmt: str, text_colors: Tuple[str, str]
) -> None:
    """Add value annotations to heatmap cells."""
    fontsize = _calc_annotation_fontsize(data.shape[0], data.shape[1])
    threshold = im.norm(data.max()) * 0.7

    formatter = matplotlib.ticker.StrMethodFormatter(valfmt)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            color = text_colors[int(im.norm(data[i, j]) > threshold)]
            im.axes.text(
                j,
                i,
                formatter(data[i, j], None),
                ha="center",
                va="center",
                color=color,
                fontsize=fontsize,
            )


def _calc_balanced_accuracy(conf_mat: np.ndarray) -> float:
    """Calculate balanced accuracy from confusion matrix.

    Balanced accuracy = average of per-class recall (sensitivity).
    """
    n_classes = conf_mat.shape[0]
    recalls = []

    for i in range(n_classes):
        true_positives = conf_mat[i, i]
        class_total = conf_mat[i, :].sum()
        if class_total > 0:
            recalls.append(true_positives / class_total)

    return np.mean(recalls) if recalls else 0.0


# EOF
