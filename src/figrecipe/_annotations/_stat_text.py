#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple text-based statistical annotations for matplotlib axes.

Provides lightweight text annotations with state management (add / remove / list).
Intended for annotations that do not require the full bracket rendering of
_stat_bracket.py — e.g. per-group p-value labels, single-point markers, or
free-form annotation text placed at a specific coordinate.

No dependency on scitex.stats or any scitex package.
"""

__all__ = [
    "add_stat_text",
    "remove_stat_text",
    "list_stat_texts",
]

import uuid
from typing import Any, Dict, List, Optional

# Default text style
_DEFAULT_FONTSIZE = 9
_DEFAULT_COLOR = "black"
_DEFAULT_HA = "center"
_DEFAULT_VA = "bottom"


def _ensure_text_store(ax: Any) -> None:
    """Lazily initialise ax._stat_texts if absent."""
    if not hasattr(ax, "_stat_texts"):
        ax._stat_texts = {}


def add_stat_text(
    ax: Any,
    x: float,
    y: float,
    text: str,
    style: str = "default",
    text_id: Optional[str] = None,
    color: str = _DEFAULT_COLOR,
    fontsize: float = _DEFAULT_FONTSIZE,
    ha: str = _DEFAULT_HA,
    va: str = _DEFAULT_VA,
    **kwargs,
) -> str:
    """Add a text annotation at a specific position on the axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    x : float
        X coordinate for the text.
    y : float
        Y coordinate for the text.
    text : str
        The annotation text (e.g. ``"p<0.001"`` or ``"n=12"``).
    style : str, optional
        Named style hint (currently unused internally; stored in metadata
        for downstream consumers). Default: ``"default"``.
    text_id : str, optional
        Unique identifier. Auto-generated UUID if None.
    color : str, optional
        Text color. Default: ``"black"``.
    fontsize : float, optional
        Font size. Default: 9.
    ha : str, optional
        Horizontal alignment (``"left"``, ``"center"``, ``"right"``).
        Default: ``"center"``.
    va : str, optional
        Vertical alignment (``"top"``, ``"center"``, ``"bottom"``).
        Default: ``"bottom"``.
    **kwargs
        Additional keyword arguments forwarded to ``ax.text()``
        (e.g. ``fontweight``, ``fontstyle``, ``zorder``, ``rotation``).

    Returns
    -------
    str
        The text_id of the created annotation.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import figrecipe._annotations as ann
    >>> fig, ax = plt.subplots()
    >>> ax.bar([1, 2], [3, 5])
    >>> ann.add_stat_text(ax, x=1.5, y=5.2, text="p=0.04")
    """
    _ensure_text_store(ax)

    if text_id is None:
        text_id = str(uuid.uuid4())

    artist = ax.text(
        x,
        y,
        text,
        ha=ha,
        va=va,
        fontsize=fontsize,
        color=color,
        clip_on=False,
        **kwargs,
    )

    ax._stat_texts[text_id] = {
        "text_id": text_id,
        "x": float(x),
        "y": float(y),
        "text": text,
        "style": style,
        "color": color,
        "fontsize": fontsize,
        "ha": ha,
        "va": va,
        "artist": artist,
    }

    return text_id


def remove_stat_text(ax: Any, text_id: str) -> bool:
    """Remove a text annotation and its artist from the axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    text_id : str
        ID of the annotation to remove.

    Returns
    -------
    bool
        True if found and removed, False otherwise.
    """
    _ensure_text_store(ax)

    if text_id not in ax._stat_texts:
        return False

    meta = ax._stat_texts.pop(text_id)
    artist = meta.get("artist")
    if artist is not None:
        try:
            artist.remove()
        except (ValueError, NotImplementedError):
            pass

    return True


def list_stat_texts(ax: Any) -> List[Dict]:
    """Return metadata for all text annotations on the axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.

    Returns
    -------
    list of dict
        Each entry contains annotation metadata (text_id, x, y, text,
        style, color, fontsize, ha, va). The ``artist`` key is excluded.
    """
    _ensure_text_store(ax)

    result = []
    for meta in ax._stat_texts.values():
        entry = {k: v for k, v in meta.items() if k != "artist"}
        result.append(entry)

    return result


# EOF
