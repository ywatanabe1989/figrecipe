#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_pie, plt_hist, plt_fill_between."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register pie/hist/fill tools on *mcp*."""

    @mcp.tool
    def plt_pie(
        x: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        autopct: Optional[str] = None,
        startangle: float = 90.0,
        counterclock: bool = False,
        explode: Optional[List[float]] = None,
        shadow: bool = False,
        width_mm: float = 40.0,
        height_mm: float = 28.0,
        style: str = "SCITEX",
        dpi: int = 300,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        legend: bool = False,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a pie chart (ax.pie).

        Parameters
        ----------
        x : list of float
            Slice sizes (normalized to 100 %).
        output_path : str
        labels : list of str, optional
        colors : list of str, optional
        autopct : str, optional
            Percentage format, e.g. "%.1f%%". None = no percentage labels.
        startangle : float
            Start angle in degrees (90 = top).
        counterclock : bool
            If False (default), slices drawn clockwise.
        explode : list of float, optional
            Offset per slice (0 = no offset).
        shadow : bool
        width_mm, height_mm : float
            Square canvas recommended (default 80×80).
        style, dpi, title, caption, legend, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "pie", "x": x}
        if data_file is not None:
            ps["data_file"] = data_file
        if labels is not None:
            ps["labels"] = labels
        if colors is not None:
            ps["colors"] = colors
        if autopct is not None:
            ps["autopct"] = autopct
        ps["startangle"] = startangle
        ps["counterclock"] = counterclock
        if explode is not None:
            ps["explode"] = explode
        if shadow:
            ps["shadow"] = shadow
        return _create(
            ps,
            output_path,
            width_mm=width_mm,
            height_mm=height_mm,
            style=style,
            dpi=dpi,
            xlabel=None,
            ylabel=None,
            title=title,
            caption=caption,
            legend=legend,
            xlim=None,
            ylim=None,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )

    @mcp.tool
    def plt_hist(
        x: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        bins: Union[int, str] = "auto",
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 0.7,
        density: bool = False,
        histtype: str = "bar",
        edgecolor: Optional[str] = None,
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
        """Create a histogram (ax.hist).

        Parameters
        ----------
        x : list of float
            Data values.
        output_path : str
        bins : int or str
            Number of bins or "auto", "fd", "scott", "sqrt".
        color, label : str, optional
        alpha : float
        density : bool
            Normalize to probability density.
        histtype : str
            "bar", "barstacked", "step", "stepfilled".
        edgecolor : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "hist", "x": x, "alpha": alpha}
        if data_file is not None:
            ps["data_file"] = data_file
        if not (isinstance(bins, str) and bins == "auto"):
            ps["bins"] = bins
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        if density:
            ps["density"] = density
        if histtype != "bar":
            ps["histtype"] = histtype
        if edgecolor is not None:
            ps["edgecolor"] = edgecolor
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
    def plt_fill_between(
        x: Union[List[float], str],
        y1: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        y2: Optional[List[float]] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 0.3,
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
        """Create a filled region plot (ax.fill_between).

        Parameters
        ----------
        x : list of float
        y1 : list of float
            Upper boundary.
        output_path : str
        y2 : list of float, optional
            Lower boundary (defaults to 0).
        color, label : str, optional
        alpha : float
            Fill transparency (default 0.3).
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "fill_between", "x": x, "y": y1, "alpha": alpha}
        if data_file is not None:
            ps["data_file"] = data_file
        if y2 is not None:
            ps["y2"] = y2
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
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
