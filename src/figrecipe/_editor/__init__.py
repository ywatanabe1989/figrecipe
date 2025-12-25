#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figrecipe GUI Editor - Interactive figure styling with hitmap-based element selection.

This module provides a Flask-based web editor for interactively adjusting
figure styles. It supports both live RecordingFigure objects and saved
recipe files (.yaml).

Usage
-----
>>> import figrecipe as fr
>>> fig, ax = fr.subplots()
>>> ax.plot(x, y, id='data')
>>> fr.edit(fig)  # Opens browser with interactive editor

>>> # Or from saved recipe
>>> fr.edit('recipe.yaml')
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from .._wrappers import RecordingFigure
from ._flask_app import FigureEditor


def edit(
    source: Optional[Union[RecordingFigure, str, Path]] = None,
    style: Optional[Union[str, Dict[str, Any]]] = None,
    port: int = 5050,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    hot_reload: bool = False,
    working_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Launch interactive GUI editor for figure styling.

    Opens a browser-based editor that allows interactive adjustment of
    figure styles using hitmap-based element selection.

    Parameters
    ----------
    source : RecordingFigure, str, Path, or None
        Either a live RecordingFigure object, path to a .yaml/.png file,
        or None to create a new blank figure.
    style : str or dict, optional
        Style preset name (e.g., 'SCITEX', 'SCITEX_DARK') or style dict.
        If None, uses the currently loaded global style.
    port : int, optional
        Flask server port (default: 5050). Auto-finds available port if occupied.
    open_browser : bool, optional
        Whether to open browser automatically (default: True).
    hot_reload : bool, optional
        Enable hot reload - server restarts when source files change (default: False).
        Like Django's development server. Browser auto-refreshes on reconnect.
    working_dir : str or Path, optional
        Working directory for file switching feature (default: current directory).
        The file switcher will list recipe files from this directory.

    Returns
    -------
    dict
        Final style overrides after editing session.

    Raises
    ------
    ImportError
        If Flask is not installed.
    TypeError
        If source is neither RecordingFigure nor valid path.
    FileNotFoundError
        If recipe file path does not exist.

    Examples
    --------
    Edit a live figure:

    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots()
    >>> ax.plot([1, 2, 3], [1, 4, 9], id='quadratic')
    >>> overrides = fr.edit(fig)

    Edit a saved recipe:

    >>> overrides = fr.edit('my_figure.yaml')

    With explicit style:

    >>> overrides = fr.edit(fig, style='SCITEX_DARK')
    """
    import importlib.util

    if importlib.util.find_spec("flask") is None:
        raise ImportError(
            "Flask is required for the GUI editor. "
            "Install with: pip install figrecipe[editor] or pip install flask"
        )

    import tempfile

    from ._flask_app import FigureEditor
    from ._hitmap import generate_hitmap, hitmap_to_base64

    # Handle different input types
    fig, recipe_path = _resolve_source(source)

    # Load style if string preset name provided
    style_dict = _resolve_style(style)

    # Save static PNG FIRST - this is the source of truth for initial display
    mpl_fig = fig.fig if hasattr(fig, "fig") else fig
    static_png_path = Path(tempfile.mktemp(suffix="_figrecipe_static.png"))
    mpl_fig.savefig(static_png_path, format="png", dpi=150, bbox_inches="tight")

    # Generate hitmap ONCE at this point
    # Pass RecordingFigure to preserve record for plot type detection
    hitmap, color_map = generate_hitmap(fig)
    hitmap_base64 = hitmap_to_base64(hitmap)

    # Resolve working directory
    resolved_working_dir = Path(working_dir) if working_dir else Path.cwd()

    # Create and run editor with pre-rendered static PNG
    editor = FigureEditor(
        fig=fig,
        recipe_path=recipe_path,
        style=style_dict,
        port=port,
        host=host,
        static_png_path=static_png_path,
        hitmap_base64=hitmap_base64,
        color_map=color_map,
        hot_reload=hot_reload,
        working_dir=resolved_working_dir,
    )

    return editor.run(open_browser=open_browser)


def _resolve_source(source: Optional[Union[RecordingFigure, str, Path]]):
    """
    Resolve source to figure and optional recipe path.

    Parameters
    ----------
    source : RecordingFigure, str, Path, or None
        Input source. If None, creates a new blank figure.
        If PNG path, tries to find associated YAML recipe.

    Returns
    -------
    tuple
        (RecordingFigure, Path or None)
    """
    # Handle None - create new blank figure
    if source is None:
        from .. import subplots

        fig, ax = subplots()
        ax.set_title("New Figure")
        ax.text(
            0.5,
            0.5,
            "Add plots using fr.edit(fig)",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
            color="gray",
        )
        return fig, None

    if isinstance(source, RecordingFigure):
        return source, None

    # Handle matplotlib Figure (e.g., from reproduce())
    from matplotlib.figure import Figure

    if isinstance(source, Figure):
        from .._recorder import FigureRecord, Recorder
        from .._wrappers._figure import RecordingFigure as RF

        wrapped_fig = RF.__new__(RF)
        wrapped_fig._fig = source
        wrapped_fig._axes = [[ax] for ax in source.axes]  # 2D list format
        wrapped_fig._recorder = Recorder()
        wrapped_fig._recorder._figure_record = FigureRecord(
            figsize=tuple(source.get_size_inches()),
            dpi=int(source.dpi),
        )
        return wrapped_fig, None

    # Assume it's a path
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Handle PNG path - find associated YAML
    if path.suffix.lower() == ".png":
        yaml_path = path.with_suffix(".yaml")
        if yaml_path.exists():
            path = yaml_path
        else:
            yml_path = path.with_suffix(".yml")
            if yml_path.exists():
                path = yml_path
            else:
                raise FileNotFoundError(
                    f"No recipe found for {path.name}. "
                    f"Expected {yaml_path.name} or {yml_path.name}"
                )

    if path.suffix.lower() not in (".yaml", ".yml"):
        raise ValueError(f"Expected .yaml, .yml, or .png file, got: {path.suffix}")

    # Load recipe and reproduce figure
    from .._reproducer import reproduce

    fig, axes = reproduce(path)

    # Wrap in RecordingFigure if needed
    if not isinstance(fig, RecordingFigure):
        from .._wrappers._figure import RecordingFigure as RF

        # Create a minimal wrapper
        wrapped_fig = RF.__new__(RF)
        wrapped_fig.fig = fig
        wrapped_fig._axes = axes if isinstance(axes, list) else [axes]
        from .._recorder import FigureRecord

        wrapped_fig.record = FigureRecord(
            figsize=fig.get_size_inches().tolist(),
            dpi=fig.dpi,
        )
        fig = wrapped_fig

    return fig, path


def _resolve_style(
    style: Optional[Union[str, Dict[str, Any]]],
) -> Optional[Dict[str, Any]]:
    """
    Resolve style to dictionary.

    Parameters
    ----------
    style : str, dict, or None
        Style preset name or dict.

    Returns
    -------
    dict or None
        Style dictionary.
    """
    if style is None:
        # Use global style if loaded
        from ..styles._style_loader import _STYLE_CACHE

        if _STYLE_CACHE is not None:
            from ..styles import to_subplots_kwargs

            return to_subplots_kwargs(_STYLE_CACHE)
        return None

    if isinstance(style, dict):
        return style

    if isinstance(style, str):
        from ..styles import load_style, to_subplots_kwargs

        loaded = load_style(style)
        return to_subplots_kwargs(loaded) if loaded else None

    raise TypeError(f"style must be str, dict, or None, got {type(style)}")


__all__ = ["edit", "FigureEditor"]
