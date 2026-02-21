#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_fill, plt_fill_betweenx, plt_contour, plt_pcolor,
plt_pcolormesh, plt_hist2d, plt_matshow."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register area / grid tools on *mcp*."""

    @mcp.tool
    def plt_fill(
        x: List[float],
        y: List[float],
        output_path: str,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 0.5,
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
        """Fill a closed polygon (ax.fill).

        Parameters
        ----------
        x, y : list of float  — Polygon vertex coordinates.
        output_path : str
        color, label : str, optional
        alpha : float  — Fill transparency (default 0.5).
        edgecolor : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "fill", "x": x, "y": y, "alpha": alpha}
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
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
    def plt_fill_betweenx(
        y: List[float],
        x1: List[float],
        output_path: str,
        x2: Optional[List[float]] = None,
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
        """Create a horizontal fill-between region (ax.fill_betweenx).

        Parameters
        ----------
        y : list of float  — Y-axis values (vertical axis).
        x1 : list of float  — Left boundary x values.
        output_path : str
        x2 : list of float, optional  — Right boundary x values (default 0).
        color, label : str, optional
        alpha : float
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "fill_betweenx", "x": y, "y": x1, "alpha": alpha}
        if x2 is not None:
            ps["y2"] = x2
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
    def plt_contour(
        X: List[List[float]],
        Y: List[List[float]],
        Z: List[List[float]],
        output_path: str,
        levels: int = 10,
        cmap: str = "viridis",
        colors: Optional[str] = None,
        linewidths: float = 1.0,
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
        """Create contour lines (ax.contour).

        Parameters
        ----------
        X, Y : 2D list of float  — Grid coordinates from np.meshgrid.
        Z : 2D list of float  — Z values (same shape as X and Y).
        output_path : str
        levels : int  — Number of contour levels.
        cmap : str
        colors : str, optional  — Single color for all lines (overrides cmap).
        linewidths : float
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "contour",
            "x": X,
            "y": Y,
            "z": Z,
            "levels": levels,
            "cmap": cmap,
            "linewidths": linewidths,
        }
        if colors is not None:
            ps["colors"] = colors
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
    def plt_pcolormesh(
        X: List[List[float]],
        Y: List[List[float]],
        C: List[List[float]],
        output_path: str,
        cmap: str = "viridis",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        shading: str = "auto",
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
        """Create a pseudocolor mesh plot (ax.pcolormesh).

        Parameters
        ----------
        X, Y : 2D list of float  — Grid coordinates.
        C : 2D list of float  — Color values.
        output_path : str
        cmap : str
        vmin, vmax : float, optional
        shading : str  — "auto", "flat", "gouraud".
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "pcolormesh",
            "x": X,
            "y": Y,
            "z": C,
            "cmap": cmap,
            "shading": shading,
        }
        if vmin is not None:
            ps["vmin"] = vmin
        if vmax is not None:
            ps["vmax"] = vmax
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
    def plt_hist2d(
        x: List[float],
        y: List[float],
        output_path: str,
        bins: int = 20,
        cmap: str = "Blues",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        density: bool = False,
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
        """Create a 2D histogram (ax.hist2d).

        Parameters
        ----------
        x, y : list of float  — Data points.
        output_path : str
        bins : int  — Number of bins in each dimension.
        cmap : str
        vmin, vmax : float, optional
        density : bool  — Normalize to density.
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "hist2d",
            "x": x,
            "y": y,
            "bins": bins,
            "cmap": cmap,
        }
        if vmin is not None:
            ps["vmin"] = vmin
        if vmax is not None:
            ps["vmax"] = vmax
        if density:
            ps["density"] = density
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
    def plt_matshow(
        data: List[List[float]],
        output_path: str,
        cmap: str = "viridis",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        width_mm: float = 40.0,
        height_mm: float = 28.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        legend: bool = False,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Display a 2D matrix with row/column ticks (ax.matshow).

        Parameters
        ----------
        data : 2D list of float  — Matrix to display.
        output_path : str
        cmap : str
        vmin, vmax : float, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "matshow", "data": data, "cmap": cmap}
        if vmin is not None:
            ps["vmin"] = vmin
        if vmax is not None:
            ps["vmax"] = vmax
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
            xlim=None,
            ylim=None,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )


# EOF
