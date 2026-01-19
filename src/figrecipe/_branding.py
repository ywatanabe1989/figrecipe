#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Branding configuration for white-label integration.

This module provides configurable branding for figrecipe, allowing parent
packages (e.g., scitex.plt) to rebrand documentation and tool descriptions.

Environment Variables
---------------------
FIGRECIPE_BRAND : str
    Package name shown in docs (default: "figrecipe")
FIGRECIPE_ALIAS : str
    Import alias shown in examples (default: "fr")

Usage
-----
Parent package sets env vars before importing:

    # scitex/plt/__init__.py
    import os
    os.environ["FIGRECIPE_BRAND"] = "scitex.plt"
    os.environ["FIGRECIPE_ALIAS"] = "plt"
    from figrecipe import *

Then docstrings will show:
    >>> import scitex.plt as plt
    >>> plt.subplots()

Instead of:
    >>> import figrecipe as fr
    >>> fr.subplots()
"""

import os
import re
from typing import Optional

# Read branding from environment
BRAND_NAME = os.environ.get("FIGRECIPE_BRAND", "figrecipe")
BRAND_ALIAS = os.environ.get("FIGRECIPE_ALIAS", "fr")

# Original values (for reference/restoration)
_ORIGINAL_NAME = "figrecipe"
_ORIGINAL_ALIAS = "fr"


def rebrand_text(text: Optional[str]) -> Optional[str]:
    """Apply branding to a text string (e.g., docstring).

    Parameters
    ----------
    text : str or None
        Text to rebrand.

    Returns
    -------
    str or None
        Rebranded text, or None if input was None.

    Examples
    --------
    >>> os.environ["FIGRECIPE_BRAND"] = "mypackage"
    >>> os.environ["FIGRECIPE_ALIAS"] = "mp"
    >>> rebrand_text("import figrecipe as fr")
    'import mypackage as mp'
    """
    if text is None:
        return None

    if BRAND_NAME == _ORIGINAL_NAME and BRAND_ALIAS == _ORIGINAL_ALIAS:
        return text

    result = text

    # Replace "import figrecipe as fr" with "import BRAND as ALIAS"
    result = re.sub(
        rf"import\s+{_ORIGINAL_NAME}\s+as\s+{_ORIGINAL_ALIAS}",
        f"import {BRAND_NAME} as {BRAND_ALIAS}",
        result,
    )

    # Replace "from figrecipe" with "from BRAND"
    result = re.sub(
        rf"from\s+{_ORIGINAL_NAME}(\s+import|\s*\.)",
        lambda m: f"from {BRAND_NAME}{m.group(1)}",
        result,
    )

    # Replace standalone "figrecipe" (but not in URLs or paths)
    # Only replace when preceded by space, newline, or start and followed by word boundary
    result = re.sub(
        rf"(?<![/.\w]){_ORIGINAL_NAME}(?=\s|$|[,.](?!\w))",
        BRAND_NAME,
        result,
    )

    # Replace " fr." with " ALIAS." (variable usage in examples)
    result = re.sub(
        rf"(\s){_ORIGINAL_ALIAS}\.",
        lambda m: f"{m.group(1)}{BRAND_ALIAS}.",
        result,
    )

    # Replace ">>> fr." with ">>> ALIAS." (doctest examples)
    result = re.sub(
        rf"(>>>\s+){_ORIGINAL_ALIAS}\.",
        lambda m: f"{m.group(1)}{BRAND_ALIAS}.",
        result,
    )

    return result


def rebrand_docstring(obj):
    """Apply branding to an object's docstring in-place.

    Parameters
    ----------
    obj : object
        Object with __doc__ attribute (function, class, module).

    Returns
    -------
    object
        The same object with rebranded docstring.
    """
    if hasattr(obj, "__doc__") and obj.__doc__:
        try:
            obj.__doc__ = rebrand_text(obj.__doc__)
        except AttributeError:
            # Some built-in objects have read-only __doc__
            pass
    return obj


def get_branded_import_example() -> str:
    """Get the branded import statement for documentation.

    Returns
    -------
    str
        Import statement like "import figrecipe as fr" or "from scitex import plt".
    """
    if BRAND_NAME == _ORIGINAL_NAME:
        return f"import {BRAND_NAME} as {BRAND_ALIAS}"

    # For rebranded packages, check if it's a submodule
    if "." in BRAND_NAME:
        parts = BRAND_NAME.rsplit(".", 1)
        return f"from {parts[0]} import {parts[1]} as {BRAND_ALIAS}"
    else:
        return f"import {BRAND_NAME} as {BRAND_ALIAS}"


def get_mcp_server_name() -> str:
    """Get the MCP server name based on branding.

    Returns
    -------
    str
        Server name for MCP registration.
    """
    return BRAND_NAME.replace(".", "-")


def get_mcp_instructions() -> str:
    """Get branded MCP server instructions.

    Returns
    -------
    str
        Instructions text with branding applied.
    """
    base_instructions = f"""
    {BRAND_NAME} MCP server for creating reproducible matplotlib figures.

    Key tools:
    - plot: Create figures from declarative YAML/JSON specs
    - reproduce: Recreate figures from saved recipes
    - compose: Combine multiple figures into one
    - info: Get information about recipe files
    - validate: Check if recipes reproduce correctly
    - crop: Auto-crop whitespace from figure images
    """
    return base_instructions


# EOF
