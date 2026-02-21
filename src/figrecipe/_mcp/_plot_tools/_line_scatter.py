#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_line, plt_scatter, plt_errorbar."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register line/scatter tools on *mcp*."""

    @mcp.tool
    def plt_line(
        output_path: str,
        x: Union[List[float], str],
        y: Union[List[float], str],
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        linewidth: float = 1.5,
        alpha: float = 1.0,
        marker: Optional[str] = None,
        yerr: Optional[List[float]] = None,
        width_mm: float = 40.0,
        height_mm: float = 28.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        legend: bool = False,
        xlim: Optional[List[float]] = None,
        ylim: Optional[List[float]] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a line plot (ax.plot).

        Parameters
        ----------
        output_path : str
            Path to save the figure (e.g. "plot.png", "plot.svg").
        x : list of float or str
            X data (inline list) or column name in data_file.
        y : list of float or str
            Y data (inline list) or column name in data_file.
        data_file : str, optional
            Path to a CSV file. When provided, x and y are treated as column
            names to look up in that file.
        color : str, optional  — Named/hex color.
        label : str, optional  — Legend label.
        linestyle : str  — "-", "--", "-.", ":".
        linewidth : float  — Line width in points.
        alpha : float  — Transparency 0–1.
        marker : str, optional  — "o", "s", "^", "D", "x", "+", None.
        yerr : list of float, optional  — Symmetric y error bars.
        width_mm, height_mm, style, dpi : Figure dimensions and quality.
        xlabel, ylabel, title, caption : Axes decorations.
        legend, xlim, ylim : Additional decorations.
        stat_annotations : list of dict, optional
            Significance brackets. Each: {x1, x2, p_value|text, y?, style?}.
        stats_results : list of dict, optional
            Direct output from scitex.stats tests.

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "line", "x": x, "y": y}
        if data_file is not None:
            ps["data_file"] = data_file
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        ps["linestyle"] = linestyle
        ps["linewidth"] = linewidth
        if alpha != 1.0:
            ps["alpha"] = alpha
        if marker is not None:
            ps["marker"] = marker
        if yerr is not None:
            ps["yerr"] = yerr
        return _create(
            ps,
            output_path,
            width_mm=width_mm,
            height_mm=height_mm,
            style=style,
            dpi=dpi,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            caption=caption,
            legend=legend,
            xlim=xlim,
            ylim=ylim,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )

    @mcp.tool
    def plt_scatter(
        output_path: str,
        x: Union[List[float], str],
        y: Union[List[float], str],
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        marker: str = "o",
        s: Optional[float] = None,
        alpha: float = 1.0,
        edgecolors: Optional[str] = None,
        width_mm: float = 40.0,
        height_mm: float = 28.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        legend: bool = False,
        xlim: Optional[List[float]] = None,
        ylim: Optional[List[float]] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a scatter plot (ax.scatter).

        Parameters
        ----------
        output_path : str
        x : list of float or str — X data or column name in data_file.
        y : list of float or str — Y data or column name in data_file.
        data_file : str, optional — CSV file path for column lookup.
        color : str, optional  — Marker color.
        label : str, optional  — Legend label.
        marker : str  — "o", "s", "^", "D", "x", "+", "v", "<", ">".
        s : float, optional  — Marker size in points².
        alpha : float  — Transparency 0–1.
        edgecolors : str, optional  — Marker edge color ("none" to hide).
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "scatter", "x": x, "y": y}
        if data_file is not None:
            ps["data_file"] = data_file
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        ps["marker"] = marker
        if s is not None:
            ps["s"] = s
        if alpha != 1.0:
            ps["alpha"] = alpha
        if edgecolors is not None:
            ps["edgecolors"] = edgecolors
        return _create(
            ps,
            output_path,
            width_mm=width_mm,
            height_mm=height_mm,
            style=style,
            dpi=dpi,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            caption=caption,
            legend=legend,
            xlim=xlim,
            ylim=ylim,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )

    @mcp.tool
    def plt_errorbar(
        output_path: str,
        x: Union[List[float], str],
        y: Union[List[float], str],
        data_file: Optional[str] = None,
        yerr: Optional[List[float]] = None,
        xerr: Optional[List[float]] = None,
        capsize: float = 4.0,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        marker: str = "o",
        alpha: float = 1.0,
        width_mm: float = 40.0,
        height_mm: float = 28.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        legend: bool = False,
        xlim: Optional[List[float]] = None,
        ylim: Optional[List[float]] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create an error-bar plot (ax.errorbar).

        Parameters
        ----------
        output_path : str
        x : list of float or str — X data or column name in data_file.
        y : list of float or str — Y data or column name in data_file.
        data_file : str, optional — CSV file path for column lookup.
        yerr : list of float, optional  — Symmetric y error bars.
        xerr : list of float, optional  — Symmetric x error bars.
        capsize : float  — Error cap size in points.
        color : str, optional.
        label : str, optional.
        linestyle : str  — "-", "--", "-.", ":", "" (no line).
        marker : str  — "o", "s", "^", etc. Use "none" for no markers.
        alpha : float  — Transparency 0–1.
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "errorbar", "x": x, "y": y}
        if data_file is not None:
            ps["data_file"] = data_file
        if yerr is not None:
            ps["yerr"] = yerr
        if xerr is not None:
            ps["xerr"] = xerr
        ps["capsize"] = capsize
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        ps["linestyle"] = linestyle
        ps["marker"] = marker
        if alpha != 1.0:
            ps["alpha"] = alpha
        return _create(
            ps,
            output_path,
            width_mm=width_mm,
            height_mm=height_mm,
            style=style,
            dpi=dpi,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            caption=caption,
            legend=legend,
            xlim=xlim,
            ylim=ylim,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )


# EOF
