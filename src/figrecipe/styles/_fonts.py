#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Font utilities for figrecipe.

Provides font availability checking and listing for publication-quality figures.
"""

__all__ = [
    "list_available_fonts",
    "check_font",
]

import warnings
from typing import List


def list_available_fonts() -> List[str]:
    """List all available font families.

    Returns
    -------
    list of str
        Sorted list of available font family names.

    Examples
    --------
    >>> fonts = ps.list_available_fonts()
    >>> print(fonts[:5])
    ['Arial', 'Courier New', 'DejaVu Sans', ...]
    """
    import matplotlib.font_manager as fm

    fonts = set()
    for font in fm.fontManager.ttflist:
        fonts.add(font.name)
    return sorted(fonts)


def check_font(font_family: str, fallback: str = "DejaVu Sans") -> str:
    """Check if font is available, with fallback and helpful error message.

    Parameters
    ----------
    font_family : str
        Requested font family name.
    fallback : str
        Fallback font if requested font is not available.

    Returns
    -------
    str
        The font to use (original if available, fallback otherwise).

    Examples
    --------
    >>> font = check_font("Arial")  # Returns "Arial" if available
    >>> font = check_font("NonExistentFont")  # Returns fallback with warning
    """

    available = list_available_fonts()

    if font_family in available:
        return font_family

    # Font not found - show helpful message
    similar = [f for f in available if font_family.lower() in f.lower()]

    msg = f"Font '{font_family}' not found.\n"
    if similar:
        msg += f"  Similar fonts available: {similar[:5]}\n"
    msg += f"  Using fallback: '{fallback}'\n"
    msg += "  To see all available fonts: ps.list_available_fonts()\n"
    msg += "  To install Arial on Linux: sudo apt install ttf-mscorefonts-installer"

    warnings.warn(msg, UserWarning)

    return fallback if fallback in available else "DejaVu Sans"
