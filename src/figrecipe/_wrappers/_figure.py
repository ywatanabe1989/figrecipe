#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapped Figure that manages recording."""

from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from ._axes import RecordingAxes

if TYPE_CHECKING:
    from .._recorder import Recorder, FigureRecord
    from .._utils._numpy_io import DataFormat


class RecordingFigure:
    """Wrapper around matplotlib Figure that manages recording.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The underlying matplotlib figure.
    recorder : Recorder
        The recorder instance.
    axes : list of RecordingAxes
        Wrapped axes objects.

    Examples
    --------
    >>> import figrecipe as ps
    >>> fig, ax = ps.subplots()
    >>> ax.plot([1, 2, 3], [4, 5, 6])
    >>> ps.save(fig, "my_figure.yaml")
    """

    def __init__(
        self,
        fig: Figure,
        recorder: "Recorder",
        axes: Union[RecordingAxes, List[RecordingAxes]],
    ):
        self._fig = fig
        self._recorder = recorder

        # Normalize axes to list
        if isinstance(axes, RecordingAxes):
            self._axes = [[axes]]
        elif isinstance(axes, list):
            if axes and isinstance(axes[0], list):
                self._axes = axes
            else:
                self._axes = [axes]
        else:
            self._axes = [[axes]]

    @property
    def fig(self) -> Figure:
        """Get the underlying matplotlib figure."""
        return self._fig

    @property
    def axes(self) -> List[List[RecordingAxes]]:
        """Get axes as 2D array."""
        return self._axes

    @property
    def flat(self) -> List[RecordingAxes]:
        """Get flattened list of all axes."""
        result = []
        for row in self._axes:
            for ax in row:
                result.append(ax)
        return result

    @property
    def record(self) -> "FigureRecord":
        """Get the figure record."""
        return self._recorder.figure_record

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to underlying figure."""
        return getattr(self._fig, name)

    def savefig(
        self,
        fname,
        save_recipe: bool = True,
        recipe_format: Literal["csv", "npz", "inline"] = "csv",
        **kwargs,
    ):
        """Save the figure image and optionally the recipe.

        Parameters
        ----------
        fname : str or Path
            Output path for the image file.
        save_recipe : bool
            If True (default), also save a YAML recipe alongside the image.
            Recipe will be saved with same name but .yaml extension.
        recipe_format : str
            Format for data in recipe: 'csv' (default), 'npz', or 'inline'.
        **kwargs
            Passed to matplotlib's savefig().

        Returns
        -------
        Path or tuple
            If save_recipe=False: image path.
            If save_recipe=True: (image_path, recipe_path) tuple.

        Examples
        --------
        >>> fig, ax = ps.subplots()
        >>> ax.plot(x, y, id='data')
        >>> fig.savefig('figure.png')  # Saves both figure.png and figure.yaml
        >>> fig.savefig('figure.png', save_recipe=False)  # Image only
        """
        # Handle file-like objects (BytesIO, etc.) - just pass through
        if hasattr(fname, 'write'):
            self._fig.savefig(fname, **kwargs)
            return fname

        fname = Path(fname)
        self._fig.savefig(fname, **kwargs)

        if save_recipe:
            recipe_path = fname.with_suffix(".yaml")
            self.save_recipe(recipe_path, include_data=True, data_format=recipe_format)
            return fname, recipe_path

        return fname

    def save_recipe(
        self,
        path: Union[str, Path],
        include_data: bool = True,
        data_format: Literal["csv", "npz", "inline"] = "csv",
    ) -> Path:
        """Save the recording recipe to YAML.

        Parameters
        ----------
        path : str or Path
            Output path for the recipe file.
        include_data : bool
            If True, save array data alongside recipe.
        data_format : str
            Format for data files: 'csv' (default), 'npz', or 'inline'.

        Returns
        -------
        Path
            Path to saved recipe file.
        """
        from .._serializer import save_recipe
        return save_recipe(self._recorder.figure_record, path, include_data, data_format)


def create_recording_subplots(
    nrows: int = 1,
    ncols: int = 1,
    recorder: Optional["Recorder"] = None,
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, List[RecordingAxes]]]:
    """Create a figure with recording-enabled axes.

    Parameters
    ----------
    nrows : int
        Number of rows.
    ncols : int
        Number of columns.
    recorder : Recorder, optional
        Recorder instance. Created if not provided.
    **kwargs
        Passed to plt.subplots().

    Returns
    -------
    fig : RecordingFigure
        Wrapped figure.
    axes : RecordingAxes or list
        Wrapped axes (single if 1x1, otherwise 2D array).
    """
    from .._recorder import Recorder

    if recorder is None:
        recorder = Recorder()

    # Create matplotlib figure
    fig, mpl_axes = plt.subplots(nrows, ncols, **kwargs)

    # Get figsize and dpi
    figsize = kwargs.get("figsize", fig.get_size_inches())
    dpi = kwargs.get("dpi", fig.dpi)

    # Start recording
    recorder.start_figure(figsize=tuple(figsize), dpi=int(dpi))

    # Wrap axes
    if nrows == 1 and ncols == 1:
        wrapped_ax = RecordingAxes(mpl_axes, recorder, position=(0, 0))
        wrapped_fig = RecordingFigure(fig, recorder, wrapped_ax)
        return wrapped_fig, wrapped_ax

    # Handle 1D or 2D arrays
    import numpy as np
    mpl_axes = np.atleast_2d(mpl_axes)

    wrapped_axes = []
    for i in range(mpl_axes.shape[0]):
        row = []
        for j in range(mpl_axes.shape[1]):
            row.append(RecordingAxes(mpl_axes[i, j], recorder, position=(i, j)))
        wrapped_axes.append(row)

    wrapped_fig = RecordingFigure(fig, recorder, wrapped_axes)

    # Return in same shape as matplotlib
    if nrows == 1:
        return wrapped_fig, wrapped_axes[0]
    elif ncols == 1:
        return wrapped_fig, [row[0] for row in wrapped_axes]
    else:
        return wrapped_fig, wrapped_axes
