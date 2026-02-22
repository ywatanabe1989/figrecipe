#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_imshow, plt_contourf."""


from typing import Any, Dict, List, Optional

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register image/contour tools on *mcp*."""

    @mcp.tool
    def plt_imshow(
        data: List[List[float]],
        output_path: str,
        cmap: str = "viridis",
        aspect: str = "auto",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        interpolation: str = "nearest",
        origin: str = "upper",
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
        """Display a 2D array as an image / heatmap (ax.imshow).

        Parameters
        ----------
        data : list of list of float
            2D data matrix (rows × cols).
        output_path : str
        cmap : str
            Colormap: "viridis", "plasma", "Reds", "Blues", "RdBu",
            "coolwarm", "gray", "inferno", "magma".
        aspect : str
            "auto" or "equal".
        vmin, vmax : float, optional
            Color scale limits.
        interpolation : str
            "nearest", "bilinear", "bicubic".
        origin : str
            "upper" (row 0 = top) or "lower" (row 0 = bottom).
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "imshow",
            "data": data,
            "cmap": cmap,
            "aspect": aspect,
        }
        if vmin is not None:
            ps["vmin"] = vmin
        if vmax is not None:
            ps["vmax"] = vmax
        if interpolation != "nearest":
            ps["interpolation"] = interpolation
        if origin != "upper":
            ps["origin"] = origin
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

    @mcp.tool
    def plt_contourf(
        X: List[List[float]],
        Y: List[List[float]],
        Z: List[List[float]],
        output_path: str,
        levels: int = 10,
        cmap: str = "viridis",
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
        """Create a filled contour plot (ax.contourf).

        Parameters
        ----------
        X : 2D list of float
            X grid coordinates (from np.meshgrid).
        Y : 2D list of float
            Y grid coordinates.
        Z : 2D list of float
            Z values (same shape as X and Y).
        output_path : str
        levels : int
            Number of contour levels.
        cmap : str
        alpha : float
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "contourf",
            "x": X,
            "y": Y,
            "z": Z,
            "levels": levels,
            "cmap": cmap,
        }
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
