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


def edit(
    source: Union[RecordingFigure, str, Path],
    style: Optional[Union[str, Dict[str, Any]]] = None,
    port: int = 5050,
    open_browser: bool = True,
) -> Dict[str, Any]:
    """
    Launch interactive GUI editor for figure styling.

    Opens a browser-based editor that allows interactive adjustment of
    figure styles using hitmap-based element selection.

    Parameters
    ----------
    source : RecordingFigure, str, or Path
        Either a live RecordingFigure object or path to a .yaml recipe file.
    style : str or dict, optional
        Style preset name (e.g., 'SCITEX', 'SCITEX_DARK') or style dict.
        If None, uses the currently loaded global style.
    port : int, optional
        Flask server port (default: 5050). Auto-finds available port if occupied.
    open_browser : bool, optional
        Whether to open browser automatically (default: True).

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
    try:
        from flask import Flask
    except ImportError:
        raise ImportError(
            "Flask is required for the GUI editor. "
            "Install with: pip install figrecipe[editor] or pip install flask"
        )

    from ._flask_app import FigureEditor

    # Handle different input types
    fig, recipe_path = _resolve_source(source)

    # Load style if string preset name provided
    style_dict = _resolve_style(style)

    # Create and run editor
    editor = FigureEditor(
        fig=fig,
        recipe_path=recipe_path,
        style=style_dict,
        port=port,
    )

    return editor.run(open_browser=open_browser)


def _resolve_source(source: Union[RecordingFigure, str, Path]):
    """
    Resolve source to figure and optional recipe path.

    Parameters
    ----------
    source : RecordingFigure, str, or Path
        Input source.

    Returns
    -------
    tuple
        (RecordingFigure or None, Path or None)
    """
    if isinstance(source, RecordingFigure):
        return source, None

    # Assume it's a path
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Recipe file not found: {path}")

    if path.suffix.lower() not in ('.yaml', '.yml'):
        raise ValueError(f"Expected .yaml or .yml file, got: {path.suffix}")

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


def _resolve_style(style: Optional[Union[str, Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
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


__all__ = ["edit"]
