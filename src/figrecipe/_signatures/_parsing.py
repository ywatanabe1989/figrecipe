#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Docstring parsing utilities for matplotlib signature extraction."""

import re
from typing import Any, Dict, List, Optional


def parse_parameter_types(docstring: Optional[str]) -> Dict[str, str]:
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
        type_str = match.group(2).split("\n")[0].strip()

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


def parse_args_pattern(
    args_str: str, param_types: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Parse args pattern like '[x], y, [fmt]' into list of arg dicts."""
    if not args_str:
        return []

    args = []
    parts = re.split(r",\s*", args_str)

    for part in parts:
        part = part.strip()
        if not part or part == "/":
            continue

        optional = part.startswith("[") and part.endswith("]")
        if optional:
            name = part[1:-1].strip()
        else:
            name = part.strip("[]").strip()

        if name and name not in ("...", "*"):
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


def extract_args_from_docstring(
    docstring: Optional[str], func_name: str = ""
) -> List[Dict[str, Any]]:
    """Extract *args as flattened list from docstring call signature."""
    if not docstring:
        return []

    # First, parse parameter types
    param_types = parse_parameter_types(docstring)

    # Check for manual pattern first
    if func_name in MANUAL_ARGS_PATTERNS:
        return parse_args_pattern(MANUAL_ARGS_PATTERNS[func_name], param_types)

    # Look for "Call signature:" patterns
    patterns = [
        r"Call signatures?::\s*\n\s*(.*?)(?:\n\n|\n[A-Z])",
        r"^\s*(\w+\([^)]+\))\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, docstring, re.MULTILINE | re.DOTALL)
        if match:
            sig_text = match.group(1).strip()
            first_line = sig_text.split("\n")[0].strip()
            inner_match = re.search(r"\(([^*]+?)(?:,\s*\*|,\s*data|\))", first_line)
            if inner_match:
                args_str = inner_match.group(1).strip().rstrip(",")
                return parse_args_pattern(args_str, param_types)
    return []


__all__ = [
    "parse_parameter_types",
    "parse_args_pattern",
    "extract_args_from_docstring",
    "MANUAL_ARGS_PATTERNS",
]

# EOF
