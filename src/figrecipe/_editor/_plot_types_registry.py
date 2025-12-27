#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registry for plot types using existing figrecipe infrastructure.

Uses:
- figrecipe._signatures for signature introspection
- figrecipe._dev.demo_plotters._categories for plot type organization
"""

from typing import Any, Dict, List

from .._dev.demo_plotters._categories import CATEGORIES as _PLOT_CATEGORIES
from .._dev.demo_plotters._categories import (
    CATEGORY_DISPLAY_NAMES as _PLOT_DISPLAY_NAMES,
)
from .._signatures import get_signature

# Decoration methods to add to the selector
DECORATION_METHODS: List[str] = [
    "text",
    "annotate",
    "arrow",
    "axhline",
    "axvline",
    "axhspan",
    "axvspan",
]

# Combined categories: plots + decorations
CATEGORIES: Dict[str, List[str]] = {
    **_PLOT_CATEGORIES,
    "decoration": DECORATION_METHODS,
}

CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    **_PLOT_DISPLAY_NAMES,
    "decoration": "Decoration & Annotation",
}


def get_plot_type_info(method_name: str) -> Dict[str, Any]:
    """Get plot type information from existing signature infrastructure."""
    sig = get_signature(method_name)

    args = sig.get("args", [])
    kwargs = sig.get("kwargs", {})

    # Args that also exist in kwargs with defaults are actually optional
    kwargs_with_defaults = {
        k for k, v in kwargs.items() if v.get("default") is not None or "default" in v
    }

    # Format required and optional args
    required_parts = []
    optional_parts = []

    for arg in args:
        name = arg.get("name", "")
        if name.startswith("*"):
            continue
        # Arg is optional if marked optional OR has a default in kwargs
        is_optional = arg.get("optional", False) or name in kwargs_with_defaults
        if is_optional:
            optional_parts.append(name)
        else:
            required_parts.append(name)

    required_str = ", ".join(required_parts) if required_parts else "data"
    # Only show first 2 optional vars, deduplicated
    optional_str = ", ".join(optional_parts[:2]) if optional_parts else ""

    # Build hint string showing signature
    hint_parts = []
    for arg in args[:4]:
        name = arg.get("name", "")
        if name.startswith("*"):
            continue
        is_optional = arg.get("optional", False) or name in kwargs_with_defaults
        if is_optional:
            hint_parts.append(f"[{name}]")
        else:
            hint_parts.append(name)

    if hint_parts:
        hint = f"{method_name}({', '.join(hint_parts)})"
    else:
        hint = f"{method_name}(data)"

    return {
        "name": method_name,
        "required": required_str,
        "optional": optional_str,
        "hint": hint,
    }


def get_all_plot_types() -> Dict[str, Dict[str, Any]]:
    """Get all plot types organized by category."""
    result = {}
    for cat_key, plots in CATEGORIES.items():
        label = CATEGORY_DISPLAY_NAMES.get(cat_key, cat_key)
        result[cat_key] = {
            "label": label,
            "types": [get_plot_type_info(m) for m in plots],
        }
    return result


def generate_html_options() -> str:
    """Generate HTML <optgroup> and <option> elements for plot type selector.

    Shows required and optional arguments with brackets around optional.
    e.g., "fill_between (x, y1, [y2], [where])"
    """
    html_parts = []
    first = True
    for cat_key, plots in CATEGORIES.items():
        label = CATEGORY_DISPLAY_NAMES.get(cat_key, cat_key)
        html_parts.append(f'                    <optgroup label="{label}">')
        for method in plots:
            info = get_plot_type_info(method)
            # Use hint which has correct bracket notation
            # hint format: "method(x, y, [opt1], [opt2])"
            display_text = info["hint"]
            selected = " selected" if first else ""
            first = False
            html_parts.append(
                f'                        <option value="{method}"{selected}>{display_text}</option>'
            )
        html_parts.append("                    </optgroup>")
    return "\n".join(html_parts)


def generate_js_hints() -> str:
    """Generate JavaScript PLOT_TYPE_HINTS object from signature infrastructure."""
    lines = ["const PLOT_TYPE_HINTS = {"]
    for plots in CATEGORIES.values():
        for method in plots:
            info = get_plot_type_info(method)
            req = info["required"].replace("'", "\\'")
            opt = info["optional"].replace("'", "\\'")
            hint = info["hint"].replace("'", "\\'")
            lines.append(
                f"    {method}: {{ required: '{req}', optional: '{opt}', hint: '{hint}' }},"
            )
    lines.append("};")
    return "\n".join(lines)


__all__ = [
    "CATEGORIES",
    "CATEGORY_DISPLAY_NAMES",
    "get_plot_type_info",
    "get_all_plot_types",
    "generate_html_options",
    "generate_js_hints",
]

# EOF
