#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Load and query matplotlib function signatures."""

import inspect
from typing import Any, Dict, List, Optional, Set

import matplotlib.pyplot as plt


# Cache for signatures
_SIGNATURE_CACHE: Dict[str, Dict[str, Any]] = {}


def get_signature(method_name: str) -> Dict[str, Any]:
    """Get signature for a matplotlib Axes method.

    Parameters
    ----------
    method_name : str
        Name of the method (e.g., 'plot', 'scatter').

    Returns
    -------
    dict
        Signature information with 'args' and 'kwargs' keys.
    """
    if method_name in _SIGNATURE_CACHE:
        return _SIGNATURE_CACHE[method_name]

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

    args = []
    kwargs = {}

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            args.append({"name": f"*{name}", "type": "*args"})
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            kwargs["**kwargs"] = {"type": "**kwargs"}
        elif param.default is inspect.Parameter.empty:
            # Positional argument
            args.append({
                "name": name,
                "type": _get_type_str(param.annotation),
            })
        else:
            # Keyword argument with default
            kwargs[name] = {
                "type": _get_type_str(param.annotation),
                "default": _serialize_default(param.default),
            }

    result = {"args": args, "kwargs": kwargs}
    _SIGNATURE_CACHE[method_name] = result
    return result


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

    # If method accepts **kwargs, all are valid
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

    Returns
    -------
    list
        Names of plotting methods.
    """
    fig, ax = plt.subplots()
    plt.close(fig)

    # Common plotting methods
    methods = [
        "plot", "scatter", "bar", "barh", "hist", "hist2d",
        "boxplot", "violinplot", "pie", "errorbar", "fill",
        "fill_between", "fill_betweenx", "stackplot", "stem",
        "step", "imshow", "pcolor", "pcolormesh", "contour",
        "contourf", "quiver", "barbs", "streamplot", "hexbin",
        "eventplot", "stairs", "ecdf",
    ]

    # Filter to only those that exist
    return [m for m in methods if hasattr(ax, m)]
