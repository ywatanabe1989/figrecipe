#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style loader for plotspec.

Loads style configuration from YAML file and provides centralized access
to all style parameters.

Usage:
    from plotspec.styles import load_style, get_style, STYLE

    # Load default style
    style = load_style()
    fig, ax = ps.subplots(**style.to_subplots_kwargs())

    # Access individual style parameters
    line_width = STYLE.lines.trace_mm
"""

__all__ = ["load_style", "get_style", "reload_style", "STYLE", "to_subplots_kwargs"]

from pathlib import Path
from typing import Any, Dict, Optional, Union

from ruamel.yaml import YAML


# Path to default style file
_DEFAULT_STYLE_PATH = Path(__file__).parent / "PLOTSPEC_STYLE.yaml"

# Global style cache
_STYLE_CACHE: Optional["DotDict"] = None


class DotDict(dict):
    """Dictionary with dot-notation access to nested keys.

    Examples
    --------
    >>> d = DotDict({"axes": {"width_mm": 40}})
    >>> d.axes.width_mm
    40
    """

    def __getattr__(self, key: str) -> Any:
        # Handle special methods first
        if key == 'to_subplots_kwargs':
            return lambda: to_subplots_kwargs(self)
        try:
            value = self[key]
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
                self[key] = value
            return value
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{key}'")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default, supporting nested keys with dots."""
        if "." in key:
            parts = key.split(".")
            value = self
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value
        return super().get(key, default)


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml(path: Union[str, Path]) -> Dict:
    """Load YAML file and return as dictionary."""
    yaml = YAML()
    yaml.preserve_quotes = True
    with open(path, "r") as f:
        return dict(yaml.load(f))


def reload_style(path: Optional[Union[str, Path]] = None) -> DotDict:
    """Reload style from YAML file (clears cache).

    Parameters
    ----------
    path : str or Path, optional
        Path to YAML style file. If None, uses default PLOTSPEC_STYLE.yaml

    Returns
    -------
    DotDict
        Style configuration as DotDict for dot-access
    """
    global _STYLE_CACHE
    _STYLE_CACHE = None
    return load_style(path)


def load_style(path: Optional[Union[str, Path]] = None) -> DotDict:
    """Load style configuration from YAML file.

    Parameters
    ----------
    path : str or Path, optional
        Path to YAML style file. If None, uses default PLOTSPEC_STYLE.yaml

    Returns
    -------
    DotDict
        Style configuration as DotDict for dot-access

    Examples
    --------
    >>> style = load_style()
    >>> style.fonts.axis_label_pt
    8
    >>> style.lines.trace_mm
    0.3
    """
    global _STYLE_CACHE

    # Use cache if available and no custom path
    if _STYLE_CACHE is not None and path is None:
        return _STYLE_CACHE

    # Load from file
    style_path = Path(path) if path else _DEFAULT_STYLE_PATH
    if not style_path.exists():
        raise FileNotFoundError(f"Style file not found: {style_path}")

    style_dict = _load_yaml(style_path)

    # Convert to DotDict for convenient access
    style = DotDict(style_dict)

    # Cache if using default
    if path is None:
        _STYLE_CACHE = style

    return style


def get_style() -> DotDict:
    """Get the current loaded style (loads default if not yet loaded).

    Returns
    -------
    DotDict
        Current style configuration
    """
    global _STYLE_CACHE
    if _STYLE_CACHE is None:
        return load_style()
    return _STYLE_CACHE


def to_subplots_kwargs(style: Optional[DotDict] = None) -> Dict[str, Any]:
    """Convert style DotDict to kwargs for ps.subplots().

    Parameters
    ----------
    style : DotDict, optional
        Style configuration. If None, uses current loaded style.

    Returns
    -------
    dict
        Keyword arguments for ps.subplots()

    Examples
    --------
    >>> style = load_style()
    >>> kwargs = to_subplots_kwargs(style)
    >>> fig, ax = ps.subplots(**kwargs)
    """
    if style is None:
        style = get_style()

    result = {
        # Axes dimensions
        "axes_width_mm": style.axes.width_mm,
        "axes_height_mm": style.axes.height_mm,
        "axes_thickness_mm": style.axes.thickness_mm,
        # Margins
        "margin_left_mm": style.margins.left_mm,
        "margin_right_mm": style.margins.right_mm,
        "margin_bottom_mm": style.margins.bottom_mm,
        "margin_top_mm": style.margins.top_mm,
        # Spacing
        "space_w_mm": style.spacing.horizontal_mm,
        "space_h_mm": style.spacing.vertical_mm,
        # Ticks
        "tick_length_mm": style.ticks.length_mm,
        "tick_thickness_mm": style.ticks.thickness_mm,
        "n_ticks": style.ticks.n_ticks,
        # Lines
        "trace_thickness_mm": style.lines.trace_mm,
        # Markers
        "marker_size_mm": style.markers.size_mm,
        # Fonts
        "font_family": style.fonts.family,
        "axis_font_size_pt": style.fonts.axis_label_pt,
        "tick_font_size_pt": style.fonts.tick_label_pt,
        "title_font_size_pt": style.fonts.title_pt,
        "suptitle_font_size_pt": style.fonts.suptitle_pt,
        "legend_font_size_pt": style.fonts.legend_pt,
        # Padding
        "label_pad_pt": style.padding.label_pt,
        "tick_pad_pt": style.padding.tick_pt,
        "title_pad_pt": style.padding.title_pt,
        # Output
        "dpi": style.output.dpi,
        # Theme
        "theme": style.theme.mode,
    }

    # Add color palette if available
    if "colors" in style and "palette" in style.colors:
        result["color_palette"] = list(style.colors.palette)

    return result


# Lazy-loaded global STYLE object
class _StyleProxy:
    """Proxy object that loads style on first access."""

    def __getattr__(self, name: str) -> Any:
        return getattr(get_style(), name)

    def __repr__(self) -> str:
        return repr(get_style())

    def to_subplots_kwargs(self) -> Dict[str, Any]:
        """Convert style to subplots kwargs."""
        return to_subplots_kwargs()


STYLE = _StyleProxy()


if __name__ == "__main__":
    # Test loading
    print("Loading default style...")
    style = load_style()
    print(f"  axes.width_mm: {style.axes.width_mm}")
    print(f"  fonts.axis_label_pt: {style.fonts.axis_label_pt}")
    print(f"  lines.trace_mm: {style.lines.trace_mm}")

    print("\nConverting to subplots kwargs...")
    kwargs = to_subplots_kwargs()
    for k, v in list(kwargs.items())[:5]:
        print(f"  {k}: {v}")

    print("\nUsing STYLE proxy...")
    print(f"  STYLE.fonts.family: {STYLE.fonts.family}")
