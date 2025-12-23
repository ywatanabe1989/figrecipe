#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-23 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/src/figrecipe/_signatures/_loader.py

"""Load and query matplotlib function signatures with deep inspection.

Parses *args/**kwargs from docstrings and expands them to actual parameters.
"""

import inspect
import re
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt

# Cache for signatures
_SIGNATURE_CACHE: Dict[str, Dict[str, Any]] = {}


# -----------------------------------------------------------------------------
# Docstring parsing
# -----------------------------------------------------------------------------
def _parse_parameter_types(docstring: Optional[str]) -> Dict[str, str]:
    """Extract parameter types from NumPy-style docstring Parameters section."""
    if not docstring:
        return {}

    types = {}

    # Find Parameters section
    params_match = re.search(
        r"Parameters\s*[-]+\s*(.*?)(?:\n\s*Returns|\n\s*See Also|\n\s*Notes|\n\s*Examples|\n\s*Other Parameters|\Z)",
        docstring,
        re.DOTALL,
    )
    if not params_match:
        return {}

    params_text = params_match.group(1)

    # Parse lines like "x, y : array-like or float" or "fmt : str, optional"
    for match in re.finditer(
        r"^(\w+(?:\s*,\s*\w+)*)\s*:\s*(.+?)(?=\n\s*\n|\n\w+\s*:|\Z)",
        params_text,
        re.MULTILINE | re.DOTALL,
    ):
        names_str = match.group(1)
        type_str = match.group(2).split("\n")[0].strip()  # First line only

        # Clean up type string
        type_str = re.sub(r",?\s*optional\s*$", "", type_str).strip()
        type_str = re.sub(
            r",?\s*default[^,]*$", "", type_str, flags=re.IGNORECASE
        ).strip()

        # Handle multiple names like "x, y"
        for name in re.split(r"\s*,\s*", names_str):
            name = name.strip()
            if name:
                types[name.lower()] = type_str

    return types


def _parse_args_pattern(
    args_str: str, param_types: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Parse args pattern like '[x], y, [fmt]' into list of arg dicts."""
    if not args_str:
        return []

    args = []
    # Split by comma, handling brackets
    parts = re.split(r",\s*", args_str)

    for part in parts:
        part = part.strip()
        if not part or part == "/":  # Skip empty or positional-only marker
            continue

        # Check if optional (wrapped in [])
        optional = part.startswith("[") and part.endswith("]")
        if optional:
            name = part[1:-1].strip()
        else:
            # Handle cases like "[X, Y,] Z" where Z is required
            name = part.strip("[]").strip()

        if name and name not in ("...", "*"):
            # Look up type from parsed parameters
            type_str = param_types.get(name.lower())
            args.append(
                {
                    "name": name,
                    "type": type_str,
                    "optional": optional,
                }
            )

    return args


# Manual *args patterns for functions without parseable call signatures
MANUAL_ARGS_PATTERNS = {
    "fill": "[x], y, [color]",
    "stackplot": "x, *ys",
    "legend": "[handles], [labels]",
    "stem": "[locs], heads",
    "tricontour": "[triangulation], x, y, z, [levels]",
    "tricontourf": "[triangulation], x, y, z, [levels]",
    "triplot": "[triangulation], x, y, [triangles]",
    "loglog": "[x], y, [fmt]",
    "semilogx": "[x], y, [fmt]",
    "semilogy": "[x], y, [fmt]",
    "barbs": "[X], [Y], U, V, [C]",
    "quiver": "[X], [Y], U, V, [C]",
    "pcolor": "[X], [Y], C",
    "pcolormesh": "[X], [Y], C",
    "pcolorfast": "[X], [Y], C",
    "acorr": "x",
    "xcorr": "x, y",
    "plot": "[x], y, [fmt]",
}


def _extract_args_from_docstring(
    docstring: Optional[str], func_name: str = ""
) -> List[Dict[str, Any]]:
    """Extract *args as flattened list from docstring call signature."""
    if not docstring:
        return []

    # First, parse parameter types
    param_types = _parse_parameter_types(docstring)

    # Check for manual pattern first
    if func_name in MANUAL_ARGS_PATTERNS:
        return _parse_args_pattern(MANUAL_ARGS_PATTERNS[func_name], param_types)

    # Look for "Call signature:" patterns
    patterns = [
        r"Call signatures?::\s*\n\s*(.*?)(?:\n\n|\n[A-Z])",
        r"^\s*(\w+\([^)]+\))\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, docstring, re.MULTILINE | re.DOTALL)
        if match:
            sig_text = match.group(1).strip()
            # Extract first signature line
            first_line = sig_text.split("\n")[0].strip()
            # Parse the args from signature like "plot([x], y, [fmt], *, ...)"
            inner_match = re.search(r"\(([^*]+?)(?:,\s*\*|,\s*data|\))", first_line)
            if inner_match:
                args_str = inner_match.group(1).strip().rstrip(",")
                return _parse_args_pattern(args_str, param_types)
    return []


# -----------------------------------------------------------------------------
# Kwargs expansion via set_* method introspection
# -----------------------------------------------------------------------------
def _get_setter_type(obj: Any, prop_name: str) -> Optional[str]:
    """Get type from set_* method docstring."""
    setter_name = f"set_{prop_name}"
    if not hasattr(obj, setter_name):
        return None

    method = getattr(obj, setter_name)
    if not method.__doc__:
        return None

    # Parse Parameters section
    match = re.search(
        r"Parameters\s*[-]+\s*\n\s*(\w+)\s*:\s*(.+?)(?:\n\s*\n|\Z)",
        method.__doc__,
        re.DOTALL,
    )
    if match:
        type_str = match.group(2).split("\n")[0].strip()
        return type_str
    return None


def _build_kwargs_with_types() -> (
    tuple[
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
        List[Dict[str, Any]],
    ]
):
    """Build kwargs lists with types from matplotlib classes."""
    from matplotlib.artist import Artist
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.text import Text

    # Create instances for introspection
    line = Line2D([0], [0])
    patch = Patch()
    text = Text()
    artist = Artist()

    def get_type(obj, name):
        return _get_setter_type(obj, name)

    ARTIST_KWARGS = [
        {"name": "agg_filter", "type": get_type(artist, "agg_filter"), "default": None},
        {"name": "alpha", "type": get_type(artist, "alpha"), "default": None},
        {"name": "animated", "type": get_type(artist, "animated"), "default": False},
        {"name": "clip_box", "type": get_type(artist, "clip_box"), "default": None},
        {"name": "clip_on", "type": get_type(artist, "clip_on"), "default": True},
        {"name": "clip_path", "type": get_type(artist, "clip_path"), "default": None},
        {"name": "gid", "type": get_type(artist, "gid"), "default": None},
        {"name": "label", "type": get_type(artist, "label"), "default": ""},
        {
            "name": "path_effects",
            "type": get_type(artist, "path_effects"),
            "default": None,
        },
        {"name": "picker", "type": get_type(artist, "picker"), "default": None},
        {"name": "rasterized", "type": get_type(artist, "rasterized"), "default": None},
        {
            "name": "sketch_params",
            "type": get_type(artist, "sketch_params"),
            "default": None,
        },
        {"name": "snap", "type": get_type(artist, "snap"), "default": None},
        {"name": "transform", "type": get_type(artist, "transform"), "default": None},
        {"name": "url", "type": get_type(artist, "url"), "default": None},
        {"name": "visible", "type": get_type(artist, "visible"), "default": True},
        {"name": "zorder", "type": get_type(artist, "zorder"), "default": None},
    ]

    LINE2D_KWARGS = [
        {"name": "color", "type": get_type(line, "color"), "default": None},
        {"name": "linestyle", "type": get_type(line, "linestyle"), "default": "-"},
        {"name": "linewidth", "type": get_type(line, "linewidth"), "default": None},
        {"name": "marker", "type": get_type(line, "marker"), "default": ""},
        {
            "name": "markeredgecolor",
            "type": get_type(line, "markeredgecolor"),
            "default": None,
        },
        {
            "name": "markeredgewidth",
            "type": get_type(line, "markeredgewidth"),
            "default": None,
        },
        {
            "name": "markerfacecolor",
            "type": get_type(line, "markerfacecolor"),
            "default": None,
        },
        {"name": "markersize", "type": get_type(line, "markersize"), "default": None},
        {"name": "antialiased", "type": get_type(line, "antialiased"), "default": True},
        {
            "name": "dash_capstyle",
            "type": get_type(line, "dash_capstyle"),
            "default": "butt",
        },
        {
            "name": "dash_joinstyle",
            "type": get_type(line, "dash_joinstyle"),
            "default": "round",
        },
        {
            "name": "solid_capstyle",
            "type": get_type(line, "solid_capstyle"),
            "default": "projecting",
        },
        {
            "name": "solid_joinstyle",
            "type": get_type(line, "solid_joinstyle"),
            "default": "round",
        },
        {
            "name": "drawstyle",
            "type": get_type(line, "drawstyle"),
            "default": "default",
        },
        {"name": "fillstyle", "type": get_type(line, "fillstyle"), "default": "full"},
    ]

    PATCH_KWARGS = [
        {"name": "color", "type": get_type(patch, "color"), "default": None},
        {"name": "edgecolor", "type": get_type(patch, "edgecolor"), "default": None},
        {"name": "facecolor", "type": get_type(patch, "facecolor"), "default": None},
        {"name": "fill", "type": get_type(patch, "fill"), "default": True},
        {"name": "hatch", "type": get_type(patch, "hatch"), "default": None},
        {"name": "linestyle", "type": get_type(patch, "linestyle"), "default": "-"},
        {"name": "linewidth", "type": get_type(patch, "linewidth"), "default": None},
        {
            "name": "antialiased",
            "type": get_type(patch, "antialiased"),
            "default": None,
        },
        {"name": "capstyle", "type": get_type(patch, "capstyle"), "default": "butt"},
        {"name": "joinstyle", "type": get_type(patch, "joinstyle"), "default": "miter"},
    ]

    TEXT_KWARGS = [
        {"name": "color", "type": get_type(text, "color"), "default": "black"},
        {"name": "fontfamily", "type": get_type(text, "fontfamily"), "default": None},
        {"name": "fontsize", "type": get_type(text, "fontsize"), "default": None},
        {"name": "fontstretch", "type": get_type(text, "fontstretch"), "default": None},
        {"name": "fontstyle", "type": get_type(text, "fontstyle"), "default": "normal"},
        {
            "name": "fontvariant",
            "type": get_type(text, "fontvariant"),
            "default": "normal",
        },
        {
            "name": "fontweight",
            "type": get_type(text, "fontweight"),
            "default": "normal",
        },
        {
            "name": "horizontalalignment",
            "type": get_type(text, "horizontalalignment"),
            "default": "center",
        },
        {
            "name": "verticalalignment",
            "type": get_type(text, "verticalalignment"),
            "default": "center",
        },
        {"name": "rotation", "type": get_type(text, "rotation"), "default": None},
        {"name": "linespacing", "type": get_type(text, "linespacing"), "default": None},
        {
            "name": "multialignment",
            "type": get_type(text, "multialignment"),
            "default": None,
        },
        {"name": "wrap", "type": get_type(text, "wrap"), "default": False},
    ]

    return ARTIST_KWARGS, LINE2D_KWARGS, PATCH_KWARGS, TEXT_KWARGS


# Build kwargs with types (lazy initialization)
_KWARGS_CACHE: Optional[Dict[str, List[Dict[str, Any]]]] = None


def _get_kwargs_mapping() -> Dict[str, List[Dict[str, Any]]]:
    """Get kwargs mapping, building it lazily on first call."""
    global _KWARGS_CACHE
    if _KWARGS_CACHE is not None:
        return _KWARGS_CACHE

    ARTIST_KWARGS, LINE2D_KWARGS, PATCH_KWARGS, TEXT_KWARGS = _build_kwargs_with_types()

    _KWARGS_CACHE = {
        "plot": LINE2D_KWARGS + ARTIST_KWARGS,
        "scatter": ARTIST_KWARGS,
        "bar": PATCH_KWARGS + ARTIST_KWARGS,
        "barh": PATCH_KWARGS + ARTIST_KWARGS,
        "fill": PATCH_KWARGS + ARTIST_KWARGS,
        "fill_between": PATCH_KWARGS + ARTIST_KWARGS,
        "fill_betweenx": PATCH_KWARGS + ARTIST_KWARGS,
        "step": LINE2D_KWARGS + ARTIST_KWARGS,
        "errorbar": LINE2D_KWARGS + ARTIST_KWARGS,
        "hist": PATCH_KWARGS + ARTIST_KWARGS,
        "hist2d": ARTIST_KWARGS,
        "imshow": ARTIST_KWARGS,
        "pcolor": ARTIST_KWARGS,
        "pcolormesh": ARTIST_KWARGS,
        "pcolorfast": ARTIST_KWARGS,
        "contour": ARTIST_KWARGS,
        "contourf": ARTIST_KWARGS,
        "hexbin": ARTIST_KWARGS,
        "quiver": ARTIST_KWARGS,
        "barbs": ARTIST_KWARGS,
        "specgram": ARTIST_KWARGS,
        "psd": LINE2D_KWARGS + ARTIST_KWARGS,
        "csd": LINE2D_KWARGS + ARTIST_KWARGS,
        "cohere": LINE2D_KWARGS + ARTIST_KWARGS,
        "acorr": LINE2D_KWARGS + ARTIST_KWARGS,
        "xcorr": LINE2D_KWARGS + ARTIST_KWARGS,
        "angle_spectrum": LINE2D_KWARGS + ARTIST_KWARGS,
        "magnitude_spectrum": LINE2D_KWARGS + ARTIST_KWARGS,
        "phase_spectrum": LINE2D_KWARGS + ARTIST_KWARGS,
        "stackplot": PATCH_KWARGS + ARTIST_KWARGS,
        "stairs": PATCH_KWARGS + ARTIST_KWARGS,
        "eventplot": ARTIST_KWARGS,
        "broken_barh": PATCH_KWARGS + ARTIST_KWARGS,
        "loglog": LINE2D_KWARGS + ARTIST_KWARGS,
        "semilogx": LINE2D_KWARGS + ARTIST_KWARGS,
        "semilogy": LINE2D_KWARGS + ARTIST_KWARGS,
        "annotate": TEXT_KWARGS + ARTIST_KWARGS,
        "text": TEXT_KWARGS + ARTIST_KWARGS,
        "arrow": PATCH_KWARGS + ARTIST_KWARGS,
        "axhline": LINE2D_KWARGS + ARTIST_KWARGS,
        "axvline": LINE2D_KWARGS + ARTIST_KWARGS,
        "hlines": ARTIST_KWARGS,
        "vlines": ARTIST_KWARGS,
        "axhspan": PATCH_KWARGS + ARTIST_KWARGS,
        "axvspan": PATCH_KWARGS + ARTIST_KWARGS,
        "axline": LINE2D_KWARGS + ARTIST_KWARGS,
        "legend": ARTIST_KWARGS,
        "grid": LINE2D_KWARGS + ARTIST_KWARGS,
        "table": ARTIST_KWARGS,
        "clabel": TEXT_KWARGS + ARTIST_KWARGS,
        "bar_label": TEXT_KWARGS + ARTIST_KWARGS,
        "quiverkey": ARTIST_KWARGS,
        "ecdf": LINE2D_KWARGS + ARTIST_KWARGS,
        "tricontour": ARTIST_KWARGS,
        "tricontourf": ARTIST_KWARGS,
        "tripcolor": ARTIST_KWARGS,
        "triplot": LINE2D_KWARGS + ARTIST_KWARGS,
        "matshow": ARTIST_KWARGS,
        "spy": ARTIST_KWARGS + LINE2D_KWARGS,
        "boxplot": ARTIST_KWARGS,
        "violinplot": ARTIST_KWARGS,
        "pie": PATCH_KWARGS + ARTIST_KWARGS,
        "stem": LINE2D_KWARGS + ARTIST_KWARGS,
    }

    return _KWARGS_CACHE


# -----------------------------------------------------------------------------
# Type helpers
# -----------------------------------------------------------------------------
def _get_type_str(annotation) -> Optional[str]:
    """Convert annotation to string."""
    if annotation is inspect.Parameter.empty:
        return None
    if hasattr(annotation, "__name__"):
        return annotation.__name__
    return str(annotation)


def _serialize_default(default) -> Any:
    """Serialize default value."""
    if default is inspect.Parameter.empty:
        return None
    if callable(default):
        return f"<{type(default).__name__}>"
    try:
        import json

        json.dumps(default)
        return default
    except (TypeError, ValueError):
        return repr(default)


# -----------------------------------------------------------------------------
# Main API
# -----------------------------------------------------------------------------
def get_signature(method_name: str, expand_kwargs: bool = True) -> Dict[str, Any]:
    """Get signature for a matplotlib Axes method with deep inspection.

    Parameters
    ----------
    method_name : str
        Name of the method (e.g., 'plot', 'scatter').
    expand_kwargs : bool
        If True, expand **kwargs to actual parameters.

    Returns
    -------
    dict
        Signature information with 'args' and 'kwargs' keys.
        Args and kwargs are expanded from docstrings when possible.
    """
    cache_key = f"{method_name}_{expand_kwargs}"
    if cache_key in _SIGNATURE_CACHE:
        return _SIGNATURE_CACHE[cache_key]

    # Create a temporary axes to introspect
    fig, ax = plt.subplots()
    plt.close(fig)

    method = getattr(ax, method_name, None)
    if method is None:
        return {"args": [], "kwargs": {}}

    try:
        sig = inspect.signature(method)
    except (ValueError, TypeError):
        return {"args": [], "kwargs": {}}

    # Parse parameter types from docstring
    param_types = _parse_parameter_types(method.__doc__)

    args = []
    kwargs = {}
    has_var_positional = False
    has_var_keyword = False

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            has_var_positional = True
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            has_var_keyword = True
        else:
            # Try annotation first, then docstring
            typehint = _get_type_str(param.annotation)
            if not typehint:
                typehint = param_types.get(name.lower())

            if param.default is inspect.Parameter.empty:
                # Positional argument
                args.append(
                    {
                        "name": name,
                        "type": typehint,
                    }
                )
            else:
                # Keyword argument with default
                kwargs[name] = {
                    "type": typehint,
                    "default": _serialize_default(param.default),
                }

    # Expand *args from docstring
    if has_var_positional:
        docstring_args = _extract_args_from_docstring(method.__doc__, method_name)
        if docstring_args:
            # Insert flattened args at the beginning
            for i, arg in enumerate(docstring_args):
                args.insert(i, arg)
        else:
            # No docstring info, keep generic *args
            args.insert(0, {"name": "*args", "type": "*args"})

    # Expand **kwargs based on function type
    if has_var_keyword and expand_kwargs:
        kwargs_mapping = _get_kwargs_mapping()
        if method_name in kwargs_mapping:
            expanded_kwargs = kwargs_mapping[method_name]
            existing_names = {p["name"] for p in args} | set(kwargs.keys())
            for kwarg in expanded_kwargs:
                if kwarg["name"] not in existing_names:
                    kwargs[kwarg["name"]] = {
                        "type": kwarg["type"],
                        "default": kwarg["default"],
                    }
        else:
            kwargs["**kwargs"] = {"type": "**kwargs"}
    elif has_var_keyword:
        kwargs["**kwargs"] = {"type": "**kwargs"}

    result = {"args": args, "kwargs": kwargs}
    _SIGNATURE_CACHE[cache_key] = result
    return result


def get_defaults(method_name: str) -> Dict[str, Any]:
    """Get default values for a method's kwargs.

    Parameters
    ----------
    method_name : str
        Name of the method.

    Returns
    -------
    dict
        Mapping of kwarg names to default values.
    """
    sig = get_signature(method_name)
    defaults = {}

    for name, info in sig.get("kwargs", {}).items():
        if name != "**kwargs" and "default" in info:
            defaults[name] = info["default"]

    return defaults


def validate_kwargs(
    method_name: str,
    kwargs: Dict[str, Any],
) -> Dict[str, List[str]]:
    """Validate kwargs against method signature.

    Parameters
    ----------
    method_name : str
        Name of the method.
    kwargs : dict
        Kwargs to validate.

    Returns
    -------
    dict
        Validation result with 'valid', 'unknown', and 'missing' keys.
    """
    sig = get_signature(method_name)
    known_kwargs = set(sig.get("kwargs", {}).keys()) - {"**kwargs"}

    # If method accepts **kwargs and we haven't expanded it, all are valid
    if "**kwargs" in sig.get("kwargs", {}):
        return {
            "valid": list(kwargs.keys()),
            "unknown": [],
            "missing": [],
        }

    valid = []
    unknown = []

    for key in kwargs:
        if key in known_kwargs:
            valid.append(key)
        else:
            unknown.append(key)

    return {
        "valid": valid,
        "unknown": unknown,
        "missing": [],  # Not checking required kwargs for now
    }


def list_plotting_methods() -> List[str]:
    """List all available plotting methods.

    Uses _params.PLOTTING_METHODS as single source of truth,
    filtered to methods that actually exist on the current matplotlib version.

    Returns
    -------
    list
        Names of plotting methods.
    """
    from .._params import PLOTTING_METHODS

    fig, ax = plt.subplots()
    plt.close(fig)

    # Use _params.PLOTTING_METHODS as single source of truth
    return sorted([m for m in PLOTTING_METHODS if hasattr(ax, m)])


# EOF
