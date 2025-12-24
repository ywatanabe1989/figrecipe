#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-23 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/src/figrecipe/_signatures/_loader.py

"""Load and query matplotlib function signatures with deep inspection.

Parses *args/**kwargs from docstrings and expands them to actual parameters.
"""

import inspect
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt

from ._kwargs import get_kwargs_mapping
from ._parsing import extract_args_from_docstring, parse_parameter_types

# Cache for signatures
_SIGNATURE_CACHE: Dict[str, Dict[str, Any]] = {}


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
    param_types = parse_parameter_types(method.__doc__)

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

            # Handle POSITIONAL_OR_KEYWORD and POSITIONAL_ONLY parameters
            if param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            ):
                args.append(
                    {
                        "name": name,
                        "type": typehint,
                    }
                )
                if param.default is not inspect.Parameter.empty:
                    kwargs[name] = {
                        "type": typehint,
                        "default": _serialize_default(param.default),
                    }
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                kwargs[name] = {
                    "type": typehint,
                    "default": _serialize_default(param.default)
                    if param.default is not inspect.Parameter.empty
                    else None,
                }

    # Expand *args from docstring
    if has_var_positional:
        docstring_args = extract_args_from_docstring(method.__doc__, method_name)
        if docstring_args:
            for i, arg in enumerate(docstring_args):
                args.insert(i, arg)
        else:
            args.insert(0, {"name": "*args", "type": "*args"})

    # Expand **kwargs based on function type
    if has_var_keyword and expand_kwargs:
        kwargs_mapping = get_kwargs_mapping()
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
        "missing": [],
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

    return sorted([m for m in PLOTTING_METHODS if hasattr(ax, m)])


# EOF
