#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plotspec - Record and reproduce matplotlib figures.

A lightweight library for capturing matplotlib plotting calls and
reproducing figures from saved recipes.

Examples
--------
Recording a figure:

>>> import plotspec as ps
>>> import numpy as np
>>>
>>> x = np.linspace(0, 10, 100)
>>> y = np.sin(x)
>>>
>>> fig, ax = ps.subplots()
>>> ax.plot(x, y, color='red', linewidth=2, id='sine_wave')
>>> ax.set_xlabel('Time')
>>> ax.set_ylabel('Amplitude')
>>> ps.save(fig, 'my_figure.yaml')

Reproducing a figure:

>>> fig, ax = ps.reproduce('my_figure.yaml')
>>> plt.show()

Inspecting a recipe:

>>> info = ps.info('my_figure.yaml')
>>> print(info['calls'])
"""

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ._recorder import Recorder, FigureRecord, CallRecord
from ._wrappers import RecordingAxes, RecordingFigure
from ._wrappers._figure import create_recording_subplots
from ._serializer import save_recipe, load_recipe, recipe_to_dict
from ._reproducer import reproduce as _reproduce, get_recipe_info
from ._utils._numpy_io import DataFormat

# Lazy import for seaborn to avoid hard dependency
_sns_recorder = None


def _get_sns():
    """Get the seaborn recorder (lazy initialization)."""
    global _sns_recorder
    if _sns_recorder is None:
        from ._seaborn import get_seaborn_recorder
        _sns_recorder = get_seaborn_recorder()
    return _sns_recorder


class _SeabornProxy:
    """Proxy object for seaborn access via ps.sns."""

    def __getattr__(self, name: str):
        return getattr(_get_sns(), name)


# Create seaborn proxy
sns = _SeabornProxy()

__version__ = "0.1.0"
__all__ = [
    # Main API
    "subplots",
    "save",
    "reproduce",
    "info",
    "load",
    # Seaborn support
    "sns",
    # Classes (for type hints)
    "RecordingFigure",
    "RecordingAxes",
    "FigureRecord",
    "CallRecord",
    # Version
    "__version__",
]


def subplots(
    nrows: int = 1,
    ncols: int = 1,
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, List[RecordingAxes]]]:
    """Create a figure with recording-enabled axes.

    This is a drop-in replacement for plt.subplots() that wraps the
    returned figure and axes with recording capabilities.

    Parameters
    ----------
    nrows : int
        Number of rows of subplots.
    ncols : int
        Number of columns of subplots.
    **kwargs
        Additional arguments passed to plt.subplots().

    Returns
    -------
    fig : RecordingFigure
        Wrapped figure object.
    axes : RecordingAxes or list of RecordingAxes
        Wrapped axes (single for 1x1, list otherwise).

    Examples
    --------
    >>> import plotspec as ps
    >>> fig, ax = ps.subplots()
    >>> ax.plot([1, 2, 3], [4, 5, 6], color='blue')
    >>> ps.save(fig, 'simple.yaml')

    >>> fig, axes = ps.subplots(2, 2, figsize=(10, 8))
    >>> axes[0][0].scatter(x, y)
    >>> axes[1][1].hist(data)
    """
    return create_recording_subplots(nrows, ncols, **kwargs)


def save(
    fig: Union[RecordingFigure, Figure],
    path: Union[str, Path],
    include_data: bool = True,
    data_format: DataFormat = "csv",
) -> Path:
    """Save a figure's recipe to file.

    Parameters
    ----------
    fig : RecordingFigure or Figure
        The figure to save. Must be a RecordingFigure for recipe saving.
    path : str or Path
        Output path. Use .yaml extension for recipe format.
    include_data : bool
        If True, save large arrays to separate files.
    data_format : str
        Format for data files: 'csv' (default), 'npz', or 'inline'.
        - 'csv': Human-readable CSV files with dtype header
        - 'npz': Compressed numpy binary format (efficient)
        - 'inline': Store all data directly in YAML

    Returns
    -------
    Path
        Path to saved file.

    Examples
    --------
    >>> import plotspec as ps
    >>> fig, ax = ps.subplots()
    >>> ax.plot(x, y, color='red', id='my_data')
    >>> ps.save(fig, 'experiment.yaml')  # Uses CSV (default)
    >>> ps.save(fig, 'experiment.yaml', data_format='npz')  # Binary

    Notes
    -----
    The recipe file contains:
    - Figure metadata (size, DPI, matplotlib version)
    - All plotting calls with their arguments
    - References to data files for large arrays
    """
    path = Path(path)

    if isinstance(fig, RecordingFigure):
        return fig.save_recipe(path, include_data=include_data, data_format=data_format)
    else:
        raise TypeError(
            "Expected RecordingFigure. Use ps.subplots() to create "
            "a recording-enabled figure."
        )


def reproduce(
    path: Union[str, Path],
    calls: Optional[List[str]] = None,
    skip_decorations: bool = False,
) -> Tuple[Figure, Union[Axes, List[Axes]]]:
    """Reproduce a figure from a recipe file.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.
    calls : list of str, optional
        If provided, only reproduce these specific call IDs.
    skip_decorations : bool
        If True, skip decoration calls (labels, legends, etc.).

    Returns
    -------
    fig : matplotlib.figure.Figure
        Reproduced figure.
    axes : Axes or list of Axes
        Reproduced axes.

    Examples
    --------
    >>> import plotspec as ps
    >>> fig, ax = ps.reproduce('experiment.yaml')
    >>> plt.show()

    >>> # Reproduce only specific plots
    >>> fig, ax = ps.reproduce('experiment.yaml', calls=['scatter_001'])
    """
    return _reproduce(path, calls=calls, skip_decorations=skip_decorations)


def info(path: Union[str, Path]) -> Dict[str, Any]:
    """Get information about a recipe without reproducing.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    dict
        Recipe information including figure ID, creation time,
        matplotlib version, size, and list of calls.

    Examples
    --------
    >>> import plotspec as ps
    >>> recipe_info = ps.info('experiment.yaml')
    >>> print(f"Created: {recipe_info['created']}")
    >>> print(f"Calls: {len(recipe_info['calls'])}")
    """
    return get_recipe_info(path)


def load(path: Union[str, Path]) -> FigureRecord:
    """Load a recipe as a FigureRecord object.

    Parameters
    ----------
    path : str or Path
        Path to .yaml recipe file.

    Returns
    -------
    FigureRecord
        The loaded figure record.

    Examples
    --------
    >>> import plotspec as ps
    >>> record = ps.load('experiment.yaml')
    >>> # Modify the record
    >>> record.axes['ax_0_0'].calls[0].kwargs['color'] = 'blue'
    >>> # Reproduce with modifications
    >>> fig, ax = ps.reproduce_from_record(record)
    """
    return load_recipe(path)
