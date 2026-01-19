#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class and shared utilities for plot stylers.

All plot stylers inherit from PlotStyler and follow a consistent interface
for applying publication-quality styling to matplotlib plot elements.
"""

__all__ = ["PlotStyler", "mm_to_pt", "get_style_value", "get_color_palette"]

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .._style_loader import get_style


def mm_to_pt(mm: float) -> float:
    """Convert millimeters to points.

    Parameters
    ----------
    mm : float
        Value in millimeters.

    Returns
    -------
    float
        Value in points (1 pt = 1/72 inch).
    """
    return mm * 72.0 / 25.4


def get_style_value(
    *keys: str,
    default: Any = None,
    style: Optional[Any] = None,
) -> Any:
    """Get a nested value from style with fallback.

    Parameters
    ----------
    *keys : str
        Nested keys to traverse (e.g., "boxplot", "line_mm").
    default : Any
        Default value if key not found.
    style : DotDict, optional
        Style object. If None, uses current global style.

    Returns
    -------
    Any
        The style value or default.

    Examples
    --------
    >>> get_style_value("boxplot", "line_mm", default=0.2)
    0.2
    >>> get_style_value("lines", "trace_mm", default=0.2)
    0.2
    """
    if style is None:
        style = get_style()

    value = style
    for key in keys:
        value = getattr(value, key, None)
        if value is None:
            return default
    return value if value is not None else default


def get_color_palette(style: Optional[Any] = None) -> List[str]:
    """Get the color palette from style as hex strings.

    Parameters
    ----------
    style : DotDict, optional
        Style object. If None, uses current global style.

    Returns
    -------
    list of str
        List of hex color strings.
    """
    from .._color_resolver import get_color_map

    color_map = get_color_map()

    # Return colors in standard order
    color_names = [
        "blue",
        "red",
        "green",
        "yellow",
        "purple",
        "orange",
        "lightblue",
        "pink",
    ]

    return [color_map.get(name, f"C{i}") for i, name in enumerate(color_names)]


class PlotStyler(ABC):
    """Abstract base class for plot stylers.

    All plot stylers should inherit from this class and implement
    the `apply` method.

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current global style.

    Attributes
    ----------
    style : DotDict
        The style configuration object.

    Examples
    --------
    >>> class MyStyler(PlotStyler):
    ...     def apply(self, artist, **overrides):
    ...         # Apply styling to artist
    ...         pass
    """

    # Style section name (override in subclass)
    style_section: str = ""

    def __init__(self, style: Optional[Any] = None):
        """Initialize the styler with a style configuration."""
        self._style = style

    @property
    def style(self) -> Any:
        """Get the style configuration (lazy-loaded)."""
        if self._style is None:
            self._style = get_style()
        return self._style

    def get_param(self, key: str, default: Any = None) -> Any:
        """Get a parameter from this styler's section or fallback.

        Parameters
        ----------
        key : str
            Parameter name.
        default : Any
            Default value if not found.

        Returns
        -------
        Any
            The parameter value.
        """
        # Try section-specific value first
        if self.style_section:
            value = get_style_value(self.style_section, key, style=self.style)
            if value is not None:
                return value

        # Fallback to common sections
        fallbacks = {
            "line_mm": ("lines", "trace_mm"),
            "linewidth_mm": ("lines", "trace_mm"),
            "edge_mm": ("lines", "trace_mm"),
            "size_mm": ("markers", "size_mm"),
            "flier_mm": ("markers", "flier_mm"),
        }

        if key in fallbacks:
            section, fallback_key = fallbacks[key]
            value = get_style_value(section, fallback_key, style=self.style)
            if value is not None:
                return value

        return default

    @abstractmethod
    def apply(self, artist: Any, **overrides) -> Any:
        """Apply styling to a plot artist.

        Parameters
        ----------
        artist : Any
            The matplotlib artist/container to style.
        **overrides
            Override specific style parameters.

        Returns
        -------
        Any
            The styled artist (same object, modified in place).
        """
        pass

    def __call__(self, artist: Any, **overrides) -> Any:
        """Allow calling styler as a function."""
        return self.apply(artist, **overrides)


# EOF
