#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP fr_* tools: visualization helpers (heatmap, fillv, rectangle, image, violin)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create
from figrecipe._branding import BRAND_ALIAS as _BA


def register(mcp) -> None:  # noqa: ANN001
    """Register visualization fr_* tools on *mcp*."""

    @mcp.tool(f"{_BA}_heatmap")
    def _impl_heatmap(
        values_2d: List[List[float]],
        output_path: str,
        cmap: str = "viridis",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        annot: bool = True,
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
        """Heatmap with smart annotation colors (ax.stx_heatmap).

        Parameters
        ----------
        values_2d : 2D list of float — Matrix data.
        cmap : str — Colormap.
        vmin, vmax : float, optional — Color scale limits.
        annot : bool — Annotate cells with values.
        fmt : str — Format string for annotations.
        output_path : str
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_heatmap",
            "x": values_2d,
            "cmap": cmap,
            "annot": annot,
            "fmt": fmt,
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
            legend=False,
            xlim=None,
            ylim=None,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )

    @mcp.tool(f"{_BA}_fillv")
    def _impl_fillv(
        starts: Union[List[float], str],
        ends: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: str = "red",
        alpha: float = 0.2,
        width_mm: float = 40.0,
        height_mm: float = 60.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Fill vertical spans between start/end x-values (ax.stx_fillv).

        Parameters
        ----------
        starts : list of float or str — Left edges of spans or column name.
        ends : list of float or str — Right edges of spans or column name.
        color : str — Fill color (default "red").
        alpha : float — Transparency (default 0.2).
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_fillv",
            "x": starts,
            "y": ends,
            "color": color,
            "alpha": alpha,
        }
        if data_file is not None:
            ps["data_file"] = data_file
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

    @mcp.tool(f"{_BA}_rectangle")
    def _impl_rectangle(
        xx: Union[List[float], float],
        yy: Union[List[float], float],
        ww: Union[List[float], float],
        hh: Union[List[float], float],
        output_path: str,
        color: Optional[str] = None,
        alpha: float = 0.5,
        fill: bool = True,
        width_mm: float = 40.0,
        height_mm: float = 60.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Add rectangle patches to a plot (ax.stx_rectangle).

        Parameters
        ----------
        xx : float or list — Left edge x position(s).
        yy : float or list — Bottom edge y position(s).
        ww : float or list — Width(s).
        hh : float or list — Height(s).
        color : str, optional
        alpha : float
        fill : bool — Fill rectangle (default True).
        output_path : str
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_rectangle",
            "x": xx,
            "y": yy,
            "ww": ww,
            "hh": hh,
            "fill": fill,
            "alpha": alpha,
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

    @mcp.tool(f"{_BA}_image")
    def _impl_image(
        arr_2d: List[List[float]],
        output_path: str,
        cmap: str = "gray",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
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
        """Display 2D array as image with correct orientation (ax.stx_image).

        Parameters
        ----------
        arr_2d : 2D list of float — Image data.
        cmap : str — Colormap (default "gray").
        vmin, vmax : float, optional — Color scale limits.
        output_path : str
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_image",
            "x": arr_2d,
            "cmap": cmap,
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
            legend=False,
            xlim=None,
            ylim=None,
            stat_annotations=stat_annotations,
            stats_results=stats_results,
        )

    @mcp.tool(f"{_BA}_violin")
    def _impl_violin(
        values_list: List[List[float]],
        output_path: str,
        color: Optional[str] = None,
        alpha: float = 0.7,
        positions: Optional[List[float]] = None,
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
        """Plot violins from a list of arrays (ax.stx_violin).

        Parameters
        ----------
        values_list : list of list of float — Each inner list = one group/condition.
        color : str, optional
        alpha : float
        positions : list of float, optional — Violin x-positions.
        output_path : str
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_violin",
            "x": values_list,
            "alpha": alpha,
        }
        if color is not None:
            ps["color"] = color
        if positions is not None:
            ps["positions"] = positions
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
