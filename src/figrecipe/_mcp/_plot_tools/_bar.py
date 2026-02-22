#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_bar, plt_barh."""


from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register bar tools on *mcp*."""

    @mcp.tool
    def plt_bar(
        output_path: str,
        x: Union[List[Union[str, float]], str],
        height: Union[List[float], str],
        data_file: Optional[str] = None,
        yerr: Optional[List[float]] = None,
        capsize: float = 4.0,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 1.0,
        width: float = 0.8,
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
        """Create a bar chart (ax.bar).

        Parameters
        ----------
        output_path : str
            Save path.
        x : list of str/float or str
            Bar positions/labels or column name in data_file.
        height : list of float or str
            Bar heights or column name in data_file.
        data_file : str, optional — CSV file path for column lookup.
        yerr : list of float, optional
            Error bar values.
        capsize : float
            Error cap size in points.
        color : str, optional
        label : str, optional
        alpha : float
        width : float
            Bar width as fraction of spacing (default 0.8).
        edgecolor : str, optional
        width_mm, height_mm : float
            Figure size in mm.
        style : str
            "SCITEX" or "MATPLOTLIB".
        dpi : int
        xlabel, ylabel, title, caption : str, optional
        legend : bool
        xlim, ylim : [min, max], optional
        stat_annotations : list of dict, optional
            [{x1, x2, p_value|text, y?, style?}, ...]
        stats_results : list of dict, optional
            scitex.stats result dicts (auto-converted to stat_annotations).

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "bar", "x": x, "y": height}
        if data_file is not None:
            ps["data_file"] = data_file
        if yerr is not None:
            ps["yerr"] = yerr
            ps["capsize"] = capsize
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        if alpha != 1.0:
            ps["alpha"] = alpha
        ps["width"] = width
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
    def plt_barh(
        output_path: str,
        y: Union[List[Union[str, float]], str],
        width: Union[List[float], str],
        data_file: Optional[str] = None,
        xerr: Optional[List[float]] = None,
        capsize: float = 4.0,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 1.0,
        height: float = 0.8,
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
        """Create a horizontal bar chart (ax.barh).

        Parameters
        ----------
        output_path : str
        y : list of str/float or str — Positions/labels or column name.
        width : list of float or str — Bar widths or column name in data_file.
        data_file : str, optional — CSV file path for column lookup.
        xerr : list of float, optional
        capsize : float
        color, label : str, optional
        alpha : float
        height : float
            Bar height as fraction of spacing (default 0.8).
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "barh", "y": y, "x": width}
        if data_file is not None:
            ps["data_file"] = data_file
        if xerr is not None:
            ps["xerr"] = xerr
            ps["capsize"] = capsize
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        if alpha != 1.0:
            ps["alpha"] = alpha
        ps["height"] = height
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
