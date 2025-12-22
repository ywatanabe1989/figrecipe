#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Style loader for figrecipe.

Loads style configuration from YAML file and provides centralized access
to all style parameters.

Usage:
    from figrecipe.styles import load_style, get_style, STYLE

    # Load default style
    style = load_style()
    fig, ax = ps.subplots(**style.to_subplots_kwargs())

    # Access individual style parameters
    line_width = STYLE.lines.trace_mm
"""

__all__ = [
    "load_style",
    "unload_style",
    "get_style",
    "reload_style",
    "list_presets",
    "STYLE",
    "to_subplots_kwargs",
]

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ruamel.yaml import YAML


# Path to presets directory
_PRESETS_DIR = Path(__file__).parent / "presets"

# Path to default style file (for backwards compatibility)
_DEFAULT_STYLE_PATH = Path(__file__).parent / "FIGRECIPE_STYLE.yaml"

# Preset aliases (for branding - FigRecipe is part of SciTeX ecosystem)
_PRESET_ALIASES = {
    "FIGRECIPE": "SCITEX",
}

# Global style cache
_STYLE_CACHE: Optional["DotDict"] = None
_CURRENT_STYLE_NAME: Optional[str] = None


def list_presets() -> List[str]:
    """List available style presets.

    Returns
    -------
    list of str
        Names of available presets.
        Use `dark=True` parameter for dark variants.

    Examples
    --------
    >>> fr.list_presets()
    ['MATPLOTLIB', 'SCITEX']

    >>> fr.load_style("SCITEX")           # Scientific publication style
    >>> fr.load_style("SCITEX", dark=True)  # Dark variant
    >>> fr.load_style("MATPLOTLIB")       # Vanilla matplotlib
    """
    # Show only user-facing presets (not internal file names)
    return ["MATPLOTLIB", "SCITEX"]


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


def reload_style(style: Optional[Union[str, Path]] = None) -> DotDict:
    """Reload style from YAML file (clears cache).

    Parameters
    ----------
    style : str or Path, optional
        Style preset name (e.g., "SCIENTIFIC") or path to YAML file.
        If None, uses default SCIENTIFIC preset.

    Returns
    -------
    DotDict
        Style configuration as DotDict for dot-access
    """
    global _STYLE_CACHE, _CURRENT_STYLE_NAME
    _STYLE_CACHE = None
    _CURRENT_STYLE_NAME = None
    return load_style(style)


def _apply_dark_theme(style_dict: Dict) -> Dict:
    """Apply dark theme transformation to a style dictionary.

    Changes only UI elements (background, text, spines, ticks) -
    NOT the data/figure colors for scientific integrity.

    Parameters
    ----------
    style_dict : dict
        Original style dictionary

    Returns
    -------
    dict
        Style dictionary with dark theme applied
    """
    import copy
    result = copy.deepcopy(style_dict)

    # Monaco/VS Code dark theme colors (from scitex-cloud UIUX.md)
    dark_colors = {
        "figure_bg": "#1e1e1e",     # VS Code main background
        "axes_bg": "#1e1e1e",       # Same as figure background
        "legend_bg": "#1e1e1e",     # Same as figure background
        "text": "#d4d4d4",          # VS Code default text
        "spine": "#3c3c3c",         # Subtle border color
        "tick": "#d4d4d4",          # Match text
        "grid": "#3a3a3a",          # Subtle grid
    }

    # Update theme section
    if "theme" not in result:
        result["theme"] = {}
    result["theme"]["mode"] = "dark"
    result["theme"]["dark"] = dark_colors

    # Update output to not be transparent (dark bg needs to show)
    if "output" in result:
        result["output"]["transparent"] = False

    return result


def unload_style() -> None:
    """Unload the current style and reset to matplotlib defaults.

    After calling this, subsequent `subplots()` calls will use vanilla
    matplotlib behavior without FigRecipe styling.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fr.load_style("SCITEX")  # Apply scientific style
    >>> fig, ax = fr.subplots()  # Styled
    >>> fr.unload_style()        # Reset to matplotlib defaults
    >>> fig, ax = fr.subplots()  # Vanilla matplotlib
    """
    global _STYLE_CACHE, _CURRENT_STYLE_NAME
    _STYLE_CACHE = None
    _CURRENT_STYLE_NAME = None

    # Reset matplotlib rcParams to defaults
    import matplotlib as mpl
    mpl.rcParams.update(mpl.rcParamsDefault)


def load_style(style: Optional[Union[str, Path, bool]] = "SCITEX", dark: bool = False) -> Optional[DotDict]:
    """Load style configuration from preset or YAML file.

    Parameters
    ----------
    style : str, Path, bool, or None
        One of:
        - "SCITEX" / "FIGRECIPE": Scientific publication style (default)
        - "MATPLOTLIB": Vanilla matplotlib defaults
        - Path to custom YAML file: "/path/to/my_style.yaml"
        - None or False: Unload style (reset to matplotlib defaults)
    dark : bool, optional
        If True, apply dark theme transformation (default: False)

    Returns
    -------
    DotDict or None
        Style configuration as DotDict for dot-access.
        Returns None if style is unloaded.

    Examples
    --------
    >>> import figrecipe as fr

    >>> # Load scientific style (default)
    >>> style = fr.load_style()
    >>> style = fr.load_style("SCITEX")  # explicit

    >>> # Load dark variant
    >>> fr.load_style("SCITEX_DARK")
    >>> fr.load_style("SCITEX", dark=True)  # equivalent

    >>> # Reset to vanilla matplotlib
    >>> fr.load_style(None)    # unload
    >>> fr.load_style(False)   # unload
    >>> fr.load_style("MATPLOTLIB")  # explicit vanilla

    >>> # Load custom YAML file
    >>> fr.load_style("/path/to/my_style.yaml")

    >>> # Access style values
    >>> style = fr.load_style("SCITEX")
    >>> style.fonts.axis_label_pt
    7
    """
    global _STYLE_CACHE, _CURRENT_STYLE_NAME

    # Handle None or False as unload
    if style is None or style is False:
        unload_style()
        return None

    # Handle _DARK suffix in style name
    apply_dark = dark
    base_style = style
    if isinstance(style, str) and style.upper().endswith("_DARK"):
        apply_dark = True
        base_style = style[:-5]  # Remove "_DARK" suffix

    # Build cache key
    cache_key = f"{base_style}{'_DARK' if apply_dark else ''}"

    # Use cache if available and same style requested
    if _STYLE_CACHE is not None and cache_key == _CURRENT_STYLE_NAME:
        return _STYLE_CACHE

    # Resolve aliases (e.g., SCITEX -> FIGRECIPE)
    if isinstance(base_style, str):
        resolved_style = _PRESET_ALIASES.get(base_style.upper(), base_style)
    else:
        resolved_style = base_style

    # Determine the style path
    if isinstance(resolved_style, Path) or (isinstance(resolved_style, str) and ("/" in resolved_style or "\\" in resolved_style or resolved_style.endswith(".yaml"))):
        # Explicit file path
        style_path = Path(resolved_style)
        style_name = str(resolved_style)
    else:
        # Preset name (e.g., "FIGRECIPE", "MATPLOTLIB")
        style_path = _PRESETS_DIR / f"{resolved_style.upper()}.yaml"
        style_name = resolved_style.upper()

    # Check if file exists
    if not style_path.exists():
        available = list_presets()
        raise FileNotFoundError(
            f"Style not found: {style}\n"
            f"Available presets: {available}\n"
            f"Or provide a path to a custom YAML file."
        )

    style_dict = _load_yaml(style_path)

    # Apply dark theme if requested
    if apply_dark:
        style_dict = _apply_dark_theme(style_dict)
        style_name = f"{style_name}_DARK"

    # Convert to DotDict for convenient access
    result = DotDict(style_dict)

    # Cache the style
    _STYLE_CACHE = result
    _CURRENT_STYLE_NAME = style_name

    return result


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

    # Add theme colors from preset if available
    theme_mode = style.theme.mode
    if "theme" in style and theme_mode in style.theme:
        result["theme_colors"] = dict(style.theme[theme_mode])

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
