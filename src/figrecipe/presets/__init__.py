#!/usr/bin/env python3
# Timestamp: 2026-03-13
# File: figrecipe/presets/__init__.py

"""Journal presets for publication-quality figures.

Provides standardized figure dimensions, DPI, fonts, and line widths
for major scientific journals. Works identically in both standalone
and cloud environments.

Usage:
    >>> from figrecipe.presets import get_journals, get_journal
    >>> presets = get_journals()
    >>> nature_single = get_journal("Standard", "single")
"""

from ._journals import get_journal, get_journals, mm_to_pixels

__all__ = [
    "get_journals",
    "get_journal",
    "mm_to_pixels",
]

# EOF
