#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Statistical bracket annotations for matplotlib axes.

Provides functions to draw, manage, and query significance brackets
(the horizontal bar + tick marks + stars pattern common in scientific figures).

No dependency on scitex.stats — accepts pre-computed p-values and star strings.
"""

__all__ = [
    "add_stat_bracket",
    "remove_stat_bracket",
    "update_stat_bracket",
    "list_stat_brackets",
]

import uuid
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------
BRACKET_LINEWIDTH = 1.2
BRACKET_COLOR = "black"
BRACKET_TICK_HEIGHT_FRAC = 0.02  # fraction of y-range
BRACKET_TEXT_OFFSET_FRAC = 0.01  # fraction of y-range above bracket line
BRACKET_FONTSIZE = 10


def _ensure_bracket_store(ax: Any) -> None:
    """Lazily initialise ax._stat_brackets if absent."""
    if not hasattr(ax, "_stat_brackets"):
        ax._stat_brackets = {}


def _get_y_range(ax: Any) -> float:
    """Return the current y-axis range, guarding against zero."""
    y_min, y_max = ax.get_ylim()
    y_range = y_max - y_min
    return y_range if y_range != 0 else 1.0


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------


def _draw_bracket_style(
    ax: Any,
    x1: float,
    x2: float,
    y: float,
    text: str,
    color: str,
    linewidth: float,
    fontsize: float,
    **kwargs,
) -> List[Any]:
    """Draw a full bracket: horizontal bar, two vertical ticks, centred text.

    Returns list of created matplotlib artists.
    """
    artists = []
    y_range = _get_y_range(ax)
    tick_h = y_range * BRACKET_TICK_HEIGHT_FRAC
    text_y = y + y_range * BRACKET_TEXT_OFFSET_FRAC

    # Horizontal bar
    (hline,) = ax.plot(
        [x1, x2],
        [y, y],
        color=color,
        linewidth=linewidth,
        clip_on=False,
        transform=ax.transData,
    )
    artists.append(hline)

    # Left vertical tick (downward)
    (ltick,) = ax.plot(
        [x1, x1],
        [y - tick_h, y],
        color=color,
        linewidth=linewidth,
        clip_on=False,
    )
    artists.append(ltick)

    # Right vertical tick (downward)
    (rtick,) = ax.plot(
        [x2, x2],
        [y - tick_h, y],
        color=color,
        linewidth=linewidth,
        clip_on=False,
    )
    artists.append(rtick)

    # Text centred above bar
    x_mid = (x1 + x2) / 2.0
    txt = ax.text(
        x_mid,
        text_y,
        text,
        ha="center",
        va="bottom",
        fontsize=fontsize,
        color=color,
        clip_on=False,
        **{
            k: v
            for k, v in kwargs.items()
            if k in ("fontweight", "fontstyle", "zorder")
        },
    )
    artists.append(txt)

    return artists


def _draw_asterisk_style(
    ax: Any,
    x1: float,
    x2: float,
    y: float,
    text: str,
    color: str,
    linewidth: float,
    fontsize: float,
    **kwargs,
) -> List[Any]:
    """Draw only centred text — no bracket lines."""
    x_mid = (x1 + x2) / 2.0
    y_range = _get_y_range(ax)
    text_y = y + y_range * BRACKET_TEXT_OFFSET_FRAC

    txt = ax.text(
        x_mid,
        text_y,
        text,
        ha="center",
        va="bottom",
        fontsize=fontsize,
        color=color,
        clip_on=False,
        **{
            k: v
            for k, v in kwargs.items()
            if k in ("fontweight", "fontstyle", "zorder")
        },
    )
    return [txt]


def _draw_compact_style(
    ax: Any,
    x1: float,
    x2: float,
    y: float,
    text: str,
    color: str,
    linewidth: float,
    fontsize: float,
    **kwargs,
) -> List[Any]:
    """Draw a smaller bracket (reduced tick height and font)."""
    compact_linewidth = max(linewidth * 0.8, 0.6)
    compact_fontsize = max(fontsize * 0.8, 6)
    return _draw_bracket_style(
        ax,
        x1,
        x2,
        y,
        text,
        color=color,
        linewidth=compact_linewidth,
        fontsize=compact_fontsize,
        **kwargs,
    )


def _draw_text_style(
    ax: Any,
    x1: float,
    x2: float,
    y: float,
    text: str,
    color: str,
    linewidth: float,
    fontsize: float,
    **kwargs,
) -> List[Any]:
    """Draw plain text annotation at (midpoint, y)."""
    x_mid = (x1 + x2) / 2.0
    txt = ax.text(
        x_mid,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=color,
        clip_on=False,
        **{
            k: v
            for k, v in kwargs.items()
            if k in ("fontweight", "fontstyle", "zorder")
        },
    )
    return [txt]


_STYLE_DRAWERS = {
    "bracket": _draw_bracket_style,
    "asterisk": _draw_asterisk_style,
    "compact": _draw_compact_style,
    "text": _draw_text_style,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def add_stat_bracket(
    ax: Any,
    x1: float,
    x2: float,
    p_value: float,
    stars: str = "",
    y: Optional[float] = None,
    style: str = "bracket",
    label: str = "",
    effect_size: Optional[float] = None,
    effect_size_name: Optional[str] = None,
    bracket_id: Optional[str] = None,
    color: str = BRACKET_COLOR,
    linewidth: float = BRACKET_LINEWIDTH,
    fontsize: float = BRACKET_FONTSIZE,
    **kwargs,
) -> str:
    """Add a statistical significance bracket to a matplotlib axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    x1 : float
        X position of the left end of the bracket.
    x2 : float
        X position of the right end of the bracket.
    p_value : float
        The p-value (stored in metadata; not used for display unless
        ``stars`` is empty and ``label`` is empty).
    stars : str, optional
        Significance stars string, e.g. ``"***"``. If empty and ``label``
        is also empty, the p-value is formatted as text (``"p=0.03"``).
    y : float, optional
        Y coordinate for the bracket line. If None, computed automatically
        using :func:`auto_y_position`.
    style : {"bracket", "asterisk", "compact", "text"}
        Visual style of the annotation. Default: ``"bracket"``.
    label : str, optional
        Custom text label. Takes precedence over ``stars``.
    effect_size : float, optional
        Effect size value (stored in metadata only, not displayed unless
        included in ``label``).
    effect_size_name : str, optional
        Name of the effect size metric (metadata only).
    bracket_id : str, optional
        Unique identifier for this bracket. Auto-generated UUID if None.
    color : str, optional
        Line and text color. Default: ``"black"``.
    linewidth : float, optional
        Line width. Default: 1.2.
    fontsize : float, optional
        Font size for the annotation text. Default: 10.
    **kwargs
        Additional keyword arguments forwarded to drawing helpers
        (``fontweight``, ``fontstyle``, ``zorder``).

    Returns
    -------
    str
        The bracket_id of the created bracket.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import figrecipe._annotations as ann
    >>> fig, ax = plt.subplots()
    >>> ax.bar([1, 2], [3, 5])
    >>> ann.add_stat_bracket(ax, x1=1, x2=2, p_value=0.01, stars="**")
    """
    from ._auto_placement import auto_y_position

    _ensure_bracket_store(ax)

    if bracket_id is None:
        bracket_id = str(uuid.uuid4())

    # Resolve display text
    if label:
        display_text = label
    elif stars:
        display_text = stars
    else:
        display_text = f"p={p_value:.3g}"

    # Auto-compute y if not provided
    if y is None:
        y = auto_y_position(ax, x1, x2)

    # Validate style
    if style not in _STYLE_DRAWERS:
        raise ValueError(
            f"Unknown bracket style {style!r}. Choose from {list(_STYLE_DRAWERS)!r}."
        )

    drawer = _STYLE_DRAWERS[style]
    artists = drawer(
        ax,
        x1=x1,
        x2=x2,
        y=y,
        text=display_text,
        color=color,
        linewidth=linewidth,
        fontsize=fontsize,
        **kwargs,
    )

    # Store metadata
    ax._stat_brackets[bracket_id] = {
        "bracket_id": bracket_id,
        "x1": float(x1),
        "x2": float(x2),
        "p_value": float(p_value),
        "stars": stars,
        "label": label,
        "y": float(y),
        "style": style,
        "effect_size": effect_size,
        "effect_size_name": effect_size_name,
        "artists": artists,
    }

    return bracket_id


def remove_stat_bracket(ax: Any, bracket_id: str) -> bool:
    """Remove a statistical bracket and its artists from the axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    bracket_id : str
        ID of the bracket to remove (as returned by :func:`add_stat_bracket`).

    Returns
    -------
    bool
        True if the bracket was found and removed, False otherwise.
    """
    _ensure_bracket_store(ax)

    if bracket_id not in ax._stat_brackets:
        return False

    meta = ax._stat_brackets.pop(bracket_id)
    for artist in meta.get("artists", []):
        try:
            artist.remove()
        except (ValueError, NotImplementedError):
            pass

    return True


def update_stat_bracket(ax: Any, bracket_id: str, **kwargs) -> bool:
    """Update an existing statistical bracket with new properties.

    Removes the old bracket and re-adds it with the updated parameters.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    bracket_id : str
        ID of the bracket to update.
    **kwargs
        Any keyword argument accepted by :func:`add_stat_bracket`.

    Returns
    -------
    bool
        True if the bracket was found and updated, False otherwise.
    """
    _ensure_bracket_store(ax)

    if bracket_id not in ax._stat_brackets:
        return False

    # Extract current metadata (without artists)
    old_meta = {
        k: v for k, v in ax._stat_brackets[bracket_id].items() if k != "artists"
    }

    # Remove old bracket
    remove_stat_bracket(ax, bracket_id)

    # Merge old meta with new kwargs; caller overrides existing values
    merged = {**old_meta, **kwargs}
    merged.pop("bracket_id", None)  # re-use same ID below

    add_stat_bracket(ax, bracket_id=bracket_id, **merged)
    return True


def list_stat_brackets(ax: Any) -> List[Dict]:
    """Return a list of metadata dicts for all brackets on the axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.

    Returns
    -------
    list of dict
        Each entry contains bracket metadata (bracket_id, x1, x2, p_value,
        stars, label, y, style, effect_size, effect_size_name).
        The ``artists`` key is excluded.
    """
    _ensure_bracket_store(ax)

    result = []
    for meta in ax._stat_brackets.values():
        entry = {k: v for k, v in meta.items() if k != "artists"}
        result.append(entry)

    return result


# EOF
