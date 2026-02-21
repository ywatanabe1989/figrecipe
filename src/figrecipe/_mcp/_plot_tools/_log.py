#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_loglog, plt_semilogx, plt_semilogy."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register log-scale line tools on *mcp*."""

    @mcp.tool
    def plt_loglog(
        x: Union[List[float], str],
        y: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        linewidth: float = 1.5,
        marker: Optional[str] = None,
        alpha: float = 1.0,
        width_mm: float = 40.0,
        height_mm: float = 60.0,
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
        """Line plot with both axes on log scale (ax.loglog).

        Parameters
        ----------
        x, y : list of float or str — Data (positive) or column names.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color, label, linestyle, linewidth, marker, alpha : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "loglog",
            "x": x,
            "y": y,
            "linestyle": linestyle,
            "linewidth": linewidth,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        if marker is not None:
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

    @mcp.tool
    def plt_semilogx(
        x: Union[List[float], str],
        y: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        linewidth: float = 1.5,
        marker: Optional[str] = None,
        alpha: float = 1.0,
        width_mm: float = 40.0,
        height_mm: float = 60.0,
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
        """Line plot with x-axis on log scale (ax.semilogx).

        Parameters
        ----------
        x, y : list of float or str — x must be positive; or column names.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color, label, linestyle, linewidth, marker, alpha : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "semilogx",
            "x": x,
            "y": y,
            "linestyle": linestyle,
            "linewidth": linewidth,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        if marker is not None:
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

    @mcp.tool
    def plt_semilogy(
        x: Union[List[float], str],
        y: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        linewidth: float = 1.5,
        marker: Optional[str] = None,
        alpha: float = 1.0,
        width_mm: float = 40.0,
        height_mm: float = 60.0,
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
        """Line plot with y-axis on log scale (ax.semilogy).

        Parameters
        ----------
        x, y : list of float or str — y must be positive; or column names.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color, label, linestyle, linewidth, marker, alpha : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "semilogy",
            "x": x,
            "y": y,
            "linestyle": linestyle,
            "linewidth": linewidth,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
        if marker is not None:
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
