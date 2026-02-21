#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP fr_* tools: statistical/scientific plots (conf_mat, ecdf, raster, scatter_hist)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create
from figrecipe._branding import BRAND_ALIAS as _BA


def register(mcp) -> None:  # noqa: ANN001
    """Register scientific fr_* tools on *mcp*."""

    @mcp.tool(f"{_BA}_conf_mat")
    def _impl_conf_mat(
        conf_mat: List[List[float]],
        output_path: str,
        x_labels: Optional[List[str]] = None,
        y_labels: Optional[List[str]] = None,
        cmap: str = "Blues",
        fmt: str = ".2f",
        width_mm: float = 40.0,
        height_mm: float = 80.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Plot a confusion matrix (ax.stx_conf_mat).

        Parameters
        ----------
        conf_mat : 2D list of float — Confusion matrix values.
        x_labels : list of str, optional — Column (predicted) labels.
        y_labels : list of str, optional — Row (true) labels.
        cmap : str — Colormap (default "Blues").
        fmt : str — Number format string (default ".2f").
        output_path : str
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_conf_mat",
            "x": conf_mat,
            "cmap": cmap,
            "fmt": fmt,
        }
        if x_labels is not None:
            ps["x_labels"] = x_labels
        if y_labels is not None:
            ps["y_labels"] = y_labels
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
            legend=False,
            xlim=None,
            ylim=None,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )

    @mcp.tool(f"{_BA}_ecdf")
    def _impl_ecdf(
        values: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linewidth: float = 1.5,
        complementary: bool = False,
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
        """Plot empirical CDF (ax.stx_ecdf).

        Parameters
        ----------
        values : list of float or str — 1D data or column name in data_file.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color, label, linewidth : ...
        complementary : bool — Plot 1 - ECDF (survival function).
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_ecdf",
            "x": values,
            "linewidth": linewidth,
            "complementary": complementary,
        }
        if data_file is not None:
            ps["data_file"] = data_file
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

    @mcp.tool(f"{_BA}_raster")
    def _impl_raster(
        spike_times: List[List[float]],
        output_path: str,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linelengths: float = 1.0,
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
        """Plot a raster/event plot (ax.stx_raster).

        Parameters
        ----------
        spike_times : list of list of float — Each inner list = one trial/unit.
        output_path : str
        color, label, linelengths : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_raster",
            "x": spike_times,
            "linelengths": linelengths,
        }
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

    @mcp.tool(f"{_BA}_scatter_hist")
    def _impl_scatter_hist(
        x: Union[List[float], str],
        y: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        alpha: float = 0.7,
        bins: int = 20,
        width_mm: float = 40.0,
        height_mm: float = 80.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Scatter plot with marginal histograms (ax.stx_scatter_hist).

        Parameters
        ----------
        x, y : list of float or str — 1D data or column names in data_file.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color : str, optional
        alpha : float
        bins : int — Histogram bins.
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_scatter_hist",
            "x": x,
            "y": y,
            "bins": bins,
            "alpha": alpha,
        }
        if data_file is not None:
            ps["data_file"] = data_file
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
            legend=False,
            xlim=None,
            ylim=None,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )


# EOF
