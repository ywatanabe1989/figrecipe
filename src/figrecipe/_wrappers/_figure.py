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

    def get_panels_bbox(self) -> Dict[str, Any]:
        """Get bounding boxes: each panel (axes + title + labels) and unified bbox.

        Panel bbox includes axes frame, title, xlabel, ylabel - but NOT data content
        that extends beyond the panel (like graph node labels).

        Returns
        -------
        dict
            - 'panels': list of (left, bottom, right, top) for each panel
            - 'unified': (left, bottom, right, top) combined bbox of all panels
        """
        self._fig.canvas.draw()
        renderer = self._fig.canvas.get_renderer()

        fig_width_px = self._fig.get_figwidth() * self._fig.dpi
        fig_height_px = self._fig.get_figheight() * self._fig.dpi

        panels = []
        left_min, bottom_min = None, None
        right_max, top_max = None, None

        for ax in self._fig.get_axes():
            try:
                # Start with axes frame
                pos = ax.get_position()
                left, bottom = pos.x0, pos.y0
                right, top = pos.x1, pos.y1

                # Extend for title
                title = ax.title
                if title.get_text():
                    tb = title.get_window_extent(renderer)
                    top = max(top, tb.y1 / fig_height_px)

                # Extend for xlabel
                xlabel = ax.xaxis.label
                if xlabel.get_text():
                    xb = xlabel.get_window_extent(renderer)
                    bottom = min(bottom, xb.y0 / fig_height_px)

                # Extend for ylabel
                ylabel = ax.yaxis.label
                if ylabel.get_text():
                    yb = ylabel.get_window_extent(renderer)
                    left = min(left, yb.x0 / fig_width_px)

                # Extend for tick labels
                for tick in ax.xaxis.get_ticklabels():
                    tb = tick.get_window_extent(renderer)
                    if tb.width > 0:
                        bottom = min(bottom, tb.y0 / fig_height_px)

                for tick in ax.yaxis.get_ticklabels():
                    tb = tick.get_window_extent(renderer)
                    if tb.width > 0:
                        left = min(left, tb.x0 / fig_width_px)

                panels.append((left, bottom, right, top))

                if left_min is None or left < left_min:
                    left_min = left
                if bottom_min is None or bottom < bottom_min:
                    bottom_min = bottom
                if right_max is None or right > right_max:
                    right_max = right
                if top_max is None or top > top_max:
                    top_max = top
            except Exception:
                pass

        unified = (left_min, bottom_min, right_max, top_max) if left_min is not None else None
        return {'panels': panels, 'unified': unified}

    def render_caption(
        self,
        caption: Optional[str] = None,
        fontsize: float = 6,
        gap_mm: float = 2.0,
        linespacing: float = 1.2,
    ) -> "RecordingFigure":
        """Render caption below the figure, wrapped to panels bbox width.

        Caption is positioned just below the panels with a small gap,
        and wrapped precisely to match the panels bbox width.

        Parameters
        ----------
        caption : str, optional
            Caption text. If None, uses stored caption from set_caption().
        fontsize : float
            Font size in points (default: 6).
        gap_mm : float
            Gap between panels and caption in mm (default: 2.0).
        linespacing : float
            Line spacing multiplier (default: 1.2).

        Returns
        -------
        RecordingFigure
            Self for method chaining.
        """
        text = caption if caption is not None else self.caption
        if not text:
            return self

        # Get panels bbox (axes + title + labels, excludes data content like graph nodes)
        bbox_info = self.get_panels_bbox()
        unified = bbox_info.get('unified')

        if unified is None:
            left_frac, bottom_frac, right_frac, top_frac = 0.1, 0.15, 0.9, 0.9
        else:
            left_frac, bottom_frac, right_frac, top_frac = unified

        fig_height_inches = self._fig.get_figheight()
        fig_width_inches = self._fig.get_figwidth()
        dpi = self._fig.dpi

        # Gap in figure fraction
        gap_frac = (gap_mm / 25.4) / fig_height_inches

        # Target width in pixels
        target_width_px = (right_frac - left_frac) * fig_width_inches * dpi

        # Wrap text by measuring actual rendered width
        from matplotlib.textpath import TextPath
        from matplotlib.font_manager import FontProperties

        font_props = FontProperties(size=fontsize)
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            # Use TextPath for accurate width measurement
            tp = TextPath((0, 0), test_line, prop=font_props)
            text_width_pts = tp.get_extents().width
            # Convert points to pixels (1 point = dpi/72 pixels)
            text_width_px = text_width_pts * (dpi / 72)

            if text_width_px <= target_width_px or not current_line:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        wrapped_text = '\n'.join(lines)

        # Position caption
        y_pos = bottom_frac - gap_frac
        x_pos = left_frac

        self._fig.text(
            x_pos, y_pos, wrapped_text,
            ha='left', va='top', fontsize=fontsize,
            transform=self._fig.transFigure,
            linespacing=linespacing,
        )

        return self

    def set_background(self, color: str = "white") -> "RecordingFigure":
        """Set figure and axes background color.

        Use this to override theme's transparent background with a solid color.
        Affects both show() and save() output.

        Parameters
        ----------
        color : str
            Background color (default: "white").

        Returns
        -------
        RecordingFigure
            Self for method chaining.

        Examples
        --------
        >>> fig, ax = fr.subplots()
        >>> fig.set_background('white')  # Solid white background
        >>> fig.savefig('output.png')    # Will have white background
        """
        self._fig.set_facecolor(color)
        self._fig.patch.set_alpha(1.0)
        for ax in self._fig.get_axes():
            ax.set_facecolor(color)
            ax.patch.set_alpha(1.0)
        # Mark that user wants opaque output (overrides style's transparent setting)
        self._explicit_background = color
        return self

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
        background: Optional[str] = None,
        **kwargs,
    ):
        """Save the figure image and optionally the recipe.

        Delegates to fr.save() for consistent behavior.

        Parameters
        ----------
        fname : str or Path
            Output path for the image file.
        save_recipe : bool
            If True (default), also save a YAML recipe alongside the image.
        recipe_format : str
            Format for data in recipe: 'csv' (default), 'npz', or 'inline'.
        verbose : bool
            If True (default), print save status.
        background : str, optional
            Background color (e.g., 'white'). If None, uses set_background()
            value or style default. Use 'transparent' for transparent.
        **kwargs
            Passed to underlying save function (dpi, etc.).

        Returns
        -------
        Path or tuple
            If save_recipe=False: image path.
            If save_recipe=True: (image_path, recipe_path) tuple.
        """
        # Handle file-like objects (BytesIO, etc.) - just pass through to matplotlib
        if hasattr(fname, "write"):
            self._fig.savefig(fname, **kwargs)
            return fname

        # Delegate to the unified save function
        from .._api._save import save_figure

        image_path, yaml_path, _ = save_figure(
            fig=self,
            path=fname,
            include_data=save_recipe,
            data_format=recipe_format,
            validate=False,  # savefig doesn't validate by default
            verbose=verbose,
            background=background,
            **kwargs,
        )

        if save_recipe:
            return image_path, yaml_path
        return image_path

    def save_recipe(
        self,
        path: Union[str, Path],
        include_data: bool = True,
        data_format: Literal["csv", "npz", "inline"] = "csv",
        csv_format: Literal["single", "separate"] = "separate",
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
        csv_format : str
            CSV structure: 'separate' (default) or 'single' (scitex-compatible).
        """
        from .._serializer import save_recipe

        return save_recipe(
            self._recorder.figure_record, path, include_data, data_format, csv_format
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
