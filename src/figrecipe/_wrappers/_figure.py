#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapped Figure that manages recording."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from ._axes import RecordingAxes

if TYPE_CHECKING:
    from .._recorder import FigureRecord, Recorder


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

    def _get_style_fontsize(self, key: str, default: float) -> float:
        """Get fontsize from loaded style."""
        try:
            from ..styles._style_loader import _STYLE_CACHE

            if _STYLE_CACHE is not None:
                fonts = getattr(_STYLE_CACHE, "fonts", None)
                if fonts is not None:
                    return getattr(fonts, key, default)
        except Exception:
            pass
        return default

    def _get_theme_text_color(self, default: str = "black") -> str:
        """Get text color from loaded style's theme settings."""
        try:
            from ..styles._style_loader import _STYLE_CACHE

            if _STYLE_CACHE is not None:
                theme = getattr(_STYLE_CACHE, "theme", None)
                if theme is not None:
                    mode = getattr(theme, "mode", "light")
                    theme_colors = getattr(theme, mode, None)
                    if theme_colors is not None:
                        return getattr(theme_colors, "text", default)
        except Exception:
            pass
        return default

    def suptitle(self, t: str, **kwargs) -> Any:
        """Set super title for the figure and record it.

        Parameters
        ----------
        t : str
            The super title text.
        **kwargs
            Additional arguments passed to matplotlib's suptitle().

        Returns
        -------
        Text
            The matplotlib Text object.
        """
        # Auto-apply fontsize from style if not specified
        if "fontsize" not in kwargs:
            kwargs["fontsize"] = self._get_style_fontsize("suptitle_pt", 10)
        # Record the suptitle call
        self._recorder.figure_record.suptitle = {"text": t, "kwargs": kwargs}
        # Call the underlying figure's suptitle
        return self._fig.suptitle(t, **kwargs)

    def supxlabel(self, t: str, **kwargs) -> Any:
        """Set super x-label for the figure and record it.

        Parameters
        ----------
        t : str
            The super x-label text.
        **kwargs
            Additional arguments passed to matplotlib's supxlabel().

        Returns
        -------
        Text
            The matplotlib Text object.
        """
        # Auto-apply fontsize from style if not specified
        if "fontsize" not in kwargs:
            kwargs["fontsize"] = self._get_style_fontsize("supxlabel_pt", 8)
        # Record the supxlabel call
        self._recorder.figure_record.supxlabel = {"text": t, "kwargs": kwargs}
        # Call the underlying figure's supxlabel
        return self._fig.supxlabel(t, **kwargs)

    def supylabel(self, t: str, **kwargs) -> Any:
        """Set super y-label for the figure and record it.

        Parameters
        ----------
        t : str
            The super y-label text.
        **kwargs
            Additional arguments passed to matplotlib's supylabel().

        Returns
        -------
        Text
            The matplotlib Text object.
        """
        # Auto-apply fontsize from style if not specified
        if "fontsize" not in kwargs:
            kwargs["fontsize"] = self._get_style_fontsize("supylabel_pt", 8)
        # Record the supylabel call
        self._recorder.figure_record.supylabel = {"text": t, "kwargs": kwargs}
        # Call the underlying figure's supylabel
        return self._fig.supylabel(t, **kwargs)

    def add_panel_labels(
        self,
        labels: Optional[List[str]] = None,
        loc: str = "upper left",
        offset: Tuple[float, float] = (-0.1, 1.05),
        fontsize: Optional[float] = None,
        fontweight: str = "bold",
        **kwargs,
    ) -> List[Any]:
        """Add panel labels (A, B, C, D, etc.) to multi-panel figures.

        Parameters
        ----------
        labels : list of str, optional
            Custom labels. If None, uses uppercase letters (A, B, C, ...).
        loc : str
            Location hint: 'upper left' (default), 'upper right', 'lower left', 'lower right'.
        offset : tuple of float
            (x, y) offset in axes coordinates from the corner.
            Default is (-0.1, 1.05) for upper left positioning.
        fontsize : float, optional
            Font size in points. If None, uses style's title_pt or 10.
        fontweight : str
            Font weight (default: 'bold').
        **kwargs
            Additional arguments passed to ax.text().

        Returns
        -------
        list of Text
            The matplotlib Text objects created.

        Examples
        --------
        >>> fig, axes = fr.subplots(2, 2)
        >>> fig.add_panel_labels()  # Adds A, B, C, D
        >>> fig.add_panel_labels(['i', 'ii', 'iii', 'iv'])  # Custom labels
        >>> fig.add_panel_labels(loc='upper right', offset=(1.05, 1.05))
        """
        from ._panel_labels import add_panel_labels as _add_panel_labels

        # Get fontsize from style if not specified
        if fontsize is None:
            fontsize = self._get_style_fontsize("title_pt", 10)

        # Get theme text color (unless user provided 'color' in kwargs)
        if "color" not in kwargs:
            text_color = self._get_theme_text_color()
        else:
            text_color = kwargs.pop("color")

        def record_callback(info):
            self._recorder.figure_record.panel_labels = info

        return _add_panel_labels(
            all_axes=self.flat,
            labels=labels,
            loc=loc,
            offset=offset,
            fontsize=fontsize,
            fontweight=fontweight,
            text_color=text_color,
            record_callback=record_callback,
            **kwargs,
        )

    def set_title_metadata(self, title: str) -> "RecordingFigure":
        """Set figure title metadata (not rendered, stored in recipe).

        This is for storing a publication/reference title for the figure,
        separate from suptitle which is rendered on the figure.

        Parameters
        ----------
        title : str
            The figure title for publication/reference.

        Returns
        -------
        RecordingFigure
            Self for method chaining.

        Examples
        --------
        >>> fig, ax = fr.subplots()
        >>> fig.set_title_metadata("Effect of temperature on reaction rate")
        >>> fig.set_caption("Figure 1. Reaction rates measured at various temperatures.")
        """
        self._recorder.figure_record.title_metadata = title
        return self

    def set_caption(self, caption: str) -> "RecordingFigure":
        """Set figure caption metadata (not rendered, stored in recipe).

        This is for storing a publication caption for the figure,
        typically used in scientific papers (e.g., "Fig. 1. Description...").

        Parameters
        ----------
        caption : str
            The figure caption text.

        Returns
        -------
        RecordingFigure
            Self for method chaining.

        Examples
        --------
        >>> fig, ax = fr.subplots()
        >>> fig.set_caption("Figure 1. Temperature dependence of reaction rates.")
        """
        self._recorder.figure_record.caption = caption
        return self

    @property
    def title_metadata(self) -> Optional[str]:
        """Get the figure title metadata."""
        return self._recorder.figure_record.title_metadata

    @property
    def caption(self) -> Optional[str]:
        """Get the figure caption metadata."""
        return self._recorder.figure_record.caption

    def set_stats(self, stats: Dict[str, Any]) -> "RecordingFigure":
        """Set figure-level statistics metadata (not rendered, stored in recipe).

        Parameters
        ----------
        stats : dict
            Statistics dictionary (comparisons, summary, correction_method, alpha).
        """
        self._recorder.figure_record.stats = stats
        return self

    @property
    def stats(self) -> Optional[Dict[str, Any]]:
        """Get the figure-level statistics metadata."""
        return self._recorder.figure_record.stats

    def generate_caption(self, style: str = "publication", template: str = None) -> str:
        """Generate caption from stored stats. Styles: publication, brief, detailed."""
        from ._caption_generator import generate_figure_caption

        panels = [ax.caption for ax in self.flat if ax.caption]
        return generate_figure_caption(
            self.title_metadata, panels, self.stats, style, template
        )

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to underlying figure."""
        return getattr(self._fig, name)

    def savefig(
        self,
        fname,
        save_recipe: bool = True,
        recipe_format: Literal["csv", "npz", "inline"] = "csv",
        verbose: bool = True,
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
        verbose : bool
            If True (default), print save status.
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
        # Finalize ticks and special plots before saving
        from ..styles._style_applier import finalize_special_plots, finalize_ticks
        from ..styles._style_loader import get_current_style_dict

        style_dict = get_current_style_dict()
        for ax in self._fig.get_axes():
            finalize_ticks(ax)
            finalize_special_plots(ax, style_dict)

        # Handle file-like objects (BytesIO, etc.) - just pass through
        if hasattr(fname, "write"):
            self._fig.savefig(fname, **kwargs)
            return fname

        fname = Path(fname)
        self._fig.savefig(fname, **kwargs)

        if save_recipe:
            recipe_path = fname.with_suffix(".yaml")
            self.save_recipe(recipe_path, include_data=True, data_format=recipe_format)
            if verbose:
                print(f"Saved: {fname} + {recipe_path}")
            return fname, recipe_path

        if verbose:
            print(f"Saved: {fname}")
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

        return save_recipe(
            self._recorder.figure_record, path, include_data, data_format
        )


def create_recording_subplots(
    nrows: int = 1,
    ncols: int = 1,
    recorder: Optional["Recorder"] = None,
    panel_labels: bool = False,
    **kwargs,
) -> Tuple[RecordingFigure, Union[RecordingAxes, NDArray]]:
    """Create a figure with recording-enabled axes.

    Parameters
    ----------
    nrows : int
        Number of rows.
    ncols : int
        Number of columns.
    recorder : Recorder, optional
        Recorder instance. Created if not provided.
    panel_labels : bool
        If True and figure has multiple panels, automatically add
        panel labels (A, B, C, D, ...). Default is False.
    **kwargs
        Passed to plt.subplots().

    Returns
    -------
    fig : RecordingFigure
        Wrapped figure.
    axes : RecordingAxes or ndarray
        Wrapped axes (single if 1x1, otherwise numpy array matching matplotlib).

    Examples
    --------
    >>> fig, axes = fr.subplots(2, 2, panel_labels=True)  # Auto-adds A, B, C, D
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

    # Handle 1D or 2D arrays - reshape to (nrows, ncols) for uniform processing
    mpl_axes_arr = np.asarray(mpl_axes)
    if mpl_axes_arr.ndim == 1:
        mpl_axes_arr = mpl_axes_arr.reshape(nrows, ncols)

    wrapped_axes = []
    for i in range(nrows):
        row = []
        for j in range(ncols):
            row.append(RecordingAxes(mpl_axes_arr[i, j], recorder, position=(i, j)))
        wrapped_axes.append(row)

    wrapped_fig = RecordingFigure(fig, recorder, wrapped_axes)

    # Add panel labels if requested (multi-panel figures only)
    if panel_labels:
        wrapped_fig.add_panel_labels()

    # Return in same shape as matplotlib (numpy arrays for consistency)
    if nrows == 1:
        # 1xN -> 1D array of shape (N,)
        return wrapped_fig, np.array(wrapped_axes[0], dtype=object)
    elif ncols == 1:
        # Nx1 -> 1D array of shape (N,)
        return wrapped_fig, np.array([row[0] for row in wrapped_axes], dtype=object)
    else:
        # NxM -> 2D array
        return wrapped_fig, np.array(wrapped_axes, dtype=object)
