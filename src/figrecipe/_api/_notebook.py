#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notebook utilities for figrecipe.

Provides SVG rendering for Jupyter notebooks.
"""

__all__ = [
    "enable_svg",
]

# Notebook display format flag (set once per session)
_notebook_format_set = False


def _enable_notebook_svg():
    """Enable SVG format for Jupyter notebook display.

    This provides crisp vector graphics at any zoom level.
    Called automatically when load_style() or subplots() is used.
    """
    global _notebook_format_set
    if _notebook_format_set:
        return

    try:
        # Method 1: matplotlib_inline (IPython 7.0+, JupyterLab)
        from matplotlib_inline.backend_inline import set_matplotlib_formats

        set_matplotlib_formats("svg")
        _notebook_format_set = True
    except (ImportError, Exception):
        try:
            # Method 2: IPython config (older IPython)
            from IPython import get_ipython

            ipython = get_ipython()
            if ipython is not None and hasattr(ipython, "kernel"):
                # Only run in actual Jupyter kernel, not IPython console
                ipython.run_line_magic(
                    "config", "InlineBackend.figure_formats = ['svg']"
                )
                _notebook_format_set = True
        except Exception:
            pass  # Not in Jupyter environment or method not available


def enable_svg():
    """Manually enable SVG format for Jupyter notebook display.

    Call this if figures appear pixelated in notebooks.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fr.enable_svg()  # Enable SVG rendering
    >>> fig, ax = fr.subplots()  # Now renders as crisp SVG
    """
    global _notebook_format_set
    _notebook_format_set = False  # Force re-application
    _enable_notebook_svg()
