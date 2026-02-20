#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: streamplot, stairs, ecdf, pcolor."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register advanced / miscellaneous tools on *mcp*."""

    @mcp.tool
    def plt_streamplot(
        X: List[List[float]],
        Y: List[List[float]],
        U: List[List[float]],
        V: List[List[float]],
        output_path: str,
        density: float = 1.0,
        color: Optional[str] = None,
        cmap: Optional[str] = None,
        linewidth: Optional[float] = None,
        arrowsize: float = 1.0,
        width_mm: float = 80.0,
        height_mm: float = 70.0,
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
        """Create a streamline plot of a vector field (ax.streamplot).

        Parameters
        ----------
        X, Y : 2D list of float  — Evenly-spaced grid coordinates.
        U, V : 2D list of float  — Velocity field components.
        output_path : str
        density : float  — Stream line density (default 1.0).
        color : str, optional  — Uniform streamline color.
        cmap : str, optional  — Colormap for speed-based coloring.
        linewidth : float, optional  — Line width.
        arrowsize : float  — Arrow scale factor.
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "streamplot",
            "x": X,
            "y": Y,
            "u": U,
            "v": V,
            "density": density,
            "arrowsize": arrowsize,
        }
        if color is not None:
            ps["color"] = color
        if cmap is not None:
            ps["cmap"] = cmap
        if linewidth is not None:
            ps["linewidth"] = linewidth
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
    def plt_stairs(
        values: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        edges: Optional[List[float]] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linewidth: float = 1.5,
        fill: bool = False,
        alpha: float = 1.0,
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
        """Create a staircase (step histogram) plot (ax.stairs).

        Parameters
        ----------
        values : list of float or str — Step heights or column name in data_file.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        edges : list of float, optional  — Step edges (N+1 values).
        color, label : str, optional
        linewidth : float
        fill : bool  — Fill under the staircase.
        alpha : float
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "stairs",
            "x": values,
            "linewidth": linewidth,
            "fill": fill,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if edges is not None:
            ps["y"] = edges
        if color is not None:
            ps["color"] = color
        if label is not None:
            ps["label"] = label
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
    def plt_ecdf(
        x: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linewidth: float = 1.5,
        complementary: bool = False,
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
        """Plot empirical cumulative distribution function (ax.ecdf).

        Parameters
        ----------
        x : list of float or str — 1D data sample or column name in data_file.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color, label : str, optional
        linewidth : float
        complementary : bool  — Plot 1 - ECDF (survival function).
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "ecdf",
            "x": x,
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

    @mcp.tool
    def plt_pcolor(
        X: List[List[float]],
        Y: List[List[float]],
        C: List[List[float]],
        output_path: str,
        cmap: str = "viridis",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        shading: str = "auto",
        width_mm: float = 80.0,
        height_mm: float = 70.0,
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
        """Create a pseudocolor plot (ax.pcolor).

        Prefer plt_pcolormesh for performance; use plt_pcolor for masked arrays.

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
            "type": "pcolor",
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


# EOF
