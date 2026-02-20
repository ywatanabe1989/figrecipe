#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_boxplot, plt_violinplot."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register box/violin tools on *mcp*."""

    @mcp.tool
    def plt_boxplot(
        data: List[List[float]],
        output_path: str,
        labels: Optional[List[str]] = None,
        notch: bool = False,
        vert: bool = True,
        showfliers: bool = True,
        color: Optional[str] = None,
        width_mm: float = 80.0,
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
        """Create a box plot (ax.boxplot).

        Parameters
        ----------
        data : list of list of float
            One sublist per group (groups can have different lengths).
        output_path : str
        labels : list of str, optional
            Group labels on x-axis.
        notch : bool
            Draw notched box plots.
        vert : bool
            Vertical boxes (default True).
        showfliers : bool
            Show outlier points.
        color : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "boxplot", "x": data}
        if labels is not None:
            ps["labels"] = labels
        if notch:
            ps["notch"] = notch
        if not vert:
            ps["vert"] = vert
        if not showfliers:
            ps["showfliers"] = showfliers
        if color is not None:
            ps["color"] = color
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
    def plt_violinplot(
        dataset: List[List[float]],
        output_path: str,
        labels: Optional[List[str]] = None,
        showmeans: bool = False,
        showmedians: bool = True,
        showextrema: bool = True,
        vert: bool = True,
        color: Optional[str] = None,
        width_mm: float = 80.0,
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
        """Create a violin plot (ax.violinplot).

        Parameters
        ----------
        dataset : list of list of float
            One sublist per group.
        output_path : str
        labels : list of str, optional
            Group labels (applied as x-tick labels).
        showmeans : bool
            Draw mean line.
        showmedians : bool
            Draw median line (default True).
        showextrema : bool
            Draw extrema lines (default True).
        vert : bool
            Vertical violins (default True).
        color : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "violinplot", "x": dataset}
        if labels is not None:
            ps["labels"] = labels
        ps["showmeans"] = showmeans
        ps["showmedians"] = showmedians
        ps["showextrema"] = showextrema
        if not vert:
            ps["vert"] = vert
        if color is not None:
            ps["color"] = color
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
