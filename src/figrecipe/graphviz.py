#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pure Graphviz rendering — delegate to graphviz dot engine."""

from pathlib import Path

from ._diagram._render import _check_graphviz, _render_with_graphviz


class Graphviz:
    """Render Graphviz DOT code to image files.

    Parameters
    ----------
    code : str
        Raw Graphviz DOT code.

    Examples
    --------
    >>> g = Graphviz('digraph { A -> B }')
    >>> g.render("output.png")
    """

    def __init__(self, code: str):
        self.code = code.strip()

    def render(self, output, format="png"):
        """Render to image file.

        Parameters
        ----------
        output : str or Path
            Output file path.
        format : str
            Output format: 'png', 'svg', 'pdf'.

        Returns
        -------
        Path
            Path to rendered file.
        """
        output_path = Path(output)
        format = format.lower()

        if not _check_graphviz():
            raise RuntimeError(
                "graphviz (dot) not found. Install with: apt install graphviz"
            )

        return _render_with_graphviz(self.code, output_path, format)

    @staticmethod
    def is_available():
        """Check if graphviz (dot) is installed."""
        return _check_graphviz()

    def __repr__(self):
        return f"Graphviz({len(self.code)} chars)"
