#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main composition logic for combining multiple figures."""

from pathlib import Path
from typing import Any, Dict, Tuple, Union

from numpy.typing import NDArray

from .._recorder import FigureRecord
from .._serializer import load_recipe
from .._wrappers import RecordingAxes, RecordingFigure


def compose(
    layout: Tuple[int, int],
    sources: Dict[Tuple[int, int], Union[str, Path, FigureRecord, Tuple]],
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, NDArray]]:
    """Compose a new figure from multiple recipe sources.

    Parameters
    ----------
    layout : tuple
        (nrows, ncols) for the new composite figure.
    sources : dict
        Mapping of (row, col) -> source specification.
        Source can be:
        - str/Path: Recipe file path (uses first axes)
        - FigureRecord: Direct record (uses first axes)
        - Tuple[source, ax_key]: Specific axes from source

    **kwargs
        Additional arguments passed to subplots().

    Returns
    -------
    fig : RecordingFigure
        Composed figure.
    axes : RecordingAxes or ndarray of RecordingAxes
        Axes of the composed figure.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, axes = fr.compose(
    ...     layout=(1, 2),
    ...     sources={
    ...         (0, 0): "experiment_a.yaml",
    ...         (0, 1): "experiment_b.yaml",
    ...     }
    ... )
    """
    from .. import subplots

    nrows, ncols = layout
    fig, axes = subplots(nrows=nrows, ncols=ncols, **kwargs)

    for (row, col), source_spec in sources.items():
        source_record, ax_key = _parse_source_spec(source_spec)
        ax_record = source_record.axes.get(ax_key)

        if ax_record is None:
            available = list(source_record.axes.keys())
            raise ValueError(
                f"Axes '{ax_key}' not found in source. Available: {available}"
            )

        target_ax = _get_axes_at(axes, row, col, nrows, ncols)
        _replay_axes_record(target_ax, ax_record, fig.record, row, col)

    return fig, axes


def _parse_source_spec(
    spec: Union[str, Path, FigureRecord, Tuple],
) -> Tuple[FigureRecord, str]:
    """Parse source specification into (FigureRecord, ax_key).

    Parameters
    ----------
    spec : various
        Source specification.

    Returns
    -------
    tuple
        (FigureRecord, ax_key)
    """
    if isinstance(spec, (str, Path)):
        return load_recipe(spec), "ax_0_0"
    elif isinstance(spec, FigureRecord):
        return spec, "ax_0_0"
    elif isinstance(spec, tuple) and len(spec) == 2:
        source, ax_key = spec
        if isinstance(source, (str, Path)):
            return load_recipe(source), ax_key
        elif isinstance(source, FigureRecord):
            return source, ax_key
        raise TypeError(f"Invalid source in tuple: {type(source)}")
    raise TypeError(f"Invalid source spec type: {type(spec)}")


def _get_axes_at(
    axes: Union[RecordingAxes, NDArray],
    row: int,
    col: int,
    nrows: int,
    ncols: int,
) -> RecordingAxes:
    """Get axes at position, handling different array shapes.

    Parameters
    ----------
    axes : RecordingAxes or ndarray
        Axes object(s) from subplots.
    row, col : int
        Target position.
    nrows, ncols : int
        Grid dimensions.

    Returns
    -------
    RecordingAxes
        Axes at the specified position.
    """
    if nrows == 1 and ncols == 1:
        return axes
    elif nrows == 1:
        return axes[col]
    elif ncols == 1:
        return axes[row]
    else:
        return axes[row, col]


def _replay_axes_record(
    target_ax: RecordingAxes,
    ax_record,
    fig_record: FigureRecord,
    row: int,
    col: int,
) -> None:
    """Replay all calls from ax_record onto target axes.

    Parameters
    ----------
    target_ax : RecordingAxes
        Target axes to replay onto.
    ax_record : AxesRecord
        Source axes record with calls.
    fig_record : FigureRecord
        Figure record to update.
    row, col : int
        Target position for recording.
    """
    from .._reproducer._core import _replay_call

    mpl_ax = target_ax._ax if hasattr(target_ax, "_ax") else target_ax
    result_cache: Dict[str, Any] = {}

    # Replay plotting calls
    for call in ax_record.calls:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    # Replay decoration calls
    for call in ax_record.decorations:
        result = _replay_call(mpl_ax, call, result_cache)
        if result is not None:
            result_cache[call.id] = result

    # Update figure record with imported axes
    ax_key = f"ax_{row}_{col}"
    fig_record.axes[ax_key] = ax_record


__all__ = ["compose"]
