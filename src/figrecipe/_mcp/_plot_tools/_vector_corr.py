#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_quiver, plt_acorr, plt_xcorr, plt_spy."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register vector field and correlation tools on *mcp*."""

    @mcp.tool
    def plt_quiver(
        X: List[List[float]],
        Y: List[List[float]],
        U: List[List[float]],
        V: List[List[float]],
        output_path: str,
        scale: Optional[float] = None,
        color: Optional[str] = None,
        cmap: Optional[str] = None,
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
        """Create a vector field (ax.quiver).

        Parameters
        ----------
        X, Y : 2D list of float  — Arrow positions (from np.meshgrid).
        U, V : 2D list of float  — Arrow direction components.
        output_path : str
        scale : float, optional  — Arrow scale (smaller = longer arrows).
        color : str, optional  — Uniform arrow color.
        cmap : str, optional  — Colormap for magnitude-based coloring.
        alpha : float
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "quiver", "x": X, "y": Y, "u": U, "v": V}
        if scale is not None:
            ps["scale"] = scale
        if color is not None:
            ps["color"] = color
        if cmap is not None:
            ps["cmap"] = cmap
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
    def plt_acorr(
        x: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        maxlags: int = 10,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        marker: str = "o",
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
        """Plot autocorrelation (ax.acorr).

        Parameters
        ----------
        x : list of float or str — 1D time series or column name in data_file.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        maxlags : int  — Maximum lag to show.
        color, label, linestyle, marker : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "acorr",
            "x": x,
            "maxlags": maxlags,
            "linestyle": linestyle,
            "marker": marker,
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

    @mcp.tool
    def plt_xcorr(
        x: Union[List[float], str],
        y: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        maxlags: int = 10,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        marker: str = "o",
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
        """Plot cross-correlation of two signals (ax.xcorr).

        Parameters
        ----------
        x, y : list of float or str — Two 1D time series or column names.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        maxlags : int  — Maximum lag to show.
        color, label, linestyle, marker : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "xcorr",
            "x": x,
            "y": y,
            "maxlags": maxlags,
            "linestyle": linestyle,
            "marker": marker,
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

    @mcp.tool
    def plt_spy(
        data: List[List[float]],
        output_path: str,
        marker: str = ".",
        markersize: float = 3.0,
        color: Optional[str] = None,
        precision: float = 0.0,
        width_mm: float = 40.0,
        height_mm: float = 28.0,
        style: str = "SCITEX",
        dpi: int = 300,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Visualize sparsity of a 2D matrix (ax.spy).

        Parameters
        ----------
        data : 2D list of float  — Matrix (non-zero entries are plotted).
        output_path : str
        marker : str  — Marker style for non-zero entries.
        markersize : float
        color : str, optional
        precision : float  — Values with |v| <= precision treated as zero.
        width_mm, height_mm, style, dpi, title, caption : ...
        stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "spy",
            "data": data,
            "marker": marker,
            "markersize": markersize,
            "precision": precision,
        }
        if color is not None:
            ps["color"] = color
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
            legend=False,
            xlim=None,
            ylim=None,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )


# EOF
