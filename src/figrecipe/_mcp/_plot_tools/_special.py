#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_step, plt_stem, plt_hexbin, plt_eventplot, plt_stackplot."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register special-purpose plot tools on *mcp*."""

    @mcp.tool
    def plt_step(
        x: List[float],
        y: List[float],
        output_path: str,
        where: str = "mid",
        color: Optional[str] = None,
        label: Optional[str] = None,
        linestyle: str = "-",
        linewidth: float = 1.5,
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
        """Create a step plot (ax.step).

        Parameters
        ----------
        x, y : list of float
        output_path : str
        where : str
            Step position: "pre", "mid", "post".
        color, label, linestyle, linewidth, alpha : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "step",
            "x": x,
            "y": y,
            "where": where,
            "linestyle": linestyle,
            "linewidth": linewidth,
        }
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
    def plt_stem(
        y: List[float],
        output_path: str,
        x: Optional[List[float]] = None,
        linefmt: str = "C0-",
        markerfmt: str = "C0o",
        basefmt: str = "C3-",
        label: Optional[str] = None,
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
        """Create a stem plot (ax.stem).

        Parameters
        ----------
        y : list of float
            Heights of stems.
        output_path : str
        x : list of float, optional
            X positions (defaults to 0, 1, 2, …).
        linefmt : str
            Stem line format, e.g. "C0-", "b--".
        markerfmt : str
            Marker format at stem tips, e.g. "C0o", "rs".
        basefmt : str
            Baseline format, e.g. "C3-", "k-".
        label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "stem",
            "y": y,
            "linefmt": linefmt,
            "markerfmt": markerfmt,
            "basefmt": basefmt,
        }
        if x is not None:
            ps["x"] = x
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
    def plt_hexbin(
        x: List[float],
        y: List[float],
        output_path: str,
        gridsize: int = 20,
        cmap: str = "Blues",
        bins: Optional[Union[int, str]] = None,
        mincnt: int = 1,
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
        """Create a 2D hexagonal binning plot (ax.hexbin).

        Parameters
        ----------
        x, y : list of float
        output_path : str
        gridsize : int
            Number of hexagons in x direction.
        cmap : str
            "Blues", "viridis", "YlOrRd", etc.
        bins : int or "log", optional
            If "log", use log scale for counts.
        mincnt : int
            Minimum count to display a hexagon.
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "hexbin",
            "x": x,
            "y": y,
            "gridsize": gridsize,
            "cmap": cmap,
            "mincnt": mincnt,
        }
        if bins is not None:
            ps["bins"] = bins
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
    def plt_eventplot(
        positions: List[List[float]],
        output_path: str,
        orientation: str = "horizontal",
        lineoffsets: float = 1.0,
        linelengths: float = 0.8,
        linewidths: float = 1.0,
        colors: Optional[List[str]] = None,
        label: Optional[str] = None,
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
        """Create a spike raster / event plot (ax.eventplot).

        Parameters
        ----------
        positions : list of list of float
            Event positions per channel/row.
            E.g. [[0.1, 0.5, 0.9], [0.2, 0.7]] for 2 channels.
        output_path : str
        orientation : str
            "horizontal" or "vertical".
        lineoffsets : float
            Vertical spacing between channels.
        linelengths : float
            Length of each event tick.
        linewidths : float
        colors : list of str, optional
            Color per channel.
        label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "eventplot",
            "x": positions,
            "orientation": orientation,
            "lineoffsets": lineoffsets,
            "linelengths": linelengths,
            "linewidths": linewidths,
        }
        if colors is not None:
            ps["colors"] = colors
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
    def plt_stackplot(
        x: List[float],
        y_stacks: List[List[float]],
        output_path: str,
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        alpha: float = 1.0,
        baseline: str = "zero",
        width_mm: float = 80.0,
        height_mm: float = 60.0,
        style: str = "SCITEX",
        dpi: int = 300,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        legend: bool = True,
        xlim: Optional[List[float]] = None,
        ylim: Optional[List[float]] = None,
        stat_annotations: Optional[List[Dict[str, Any]]] = None,
        stats_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a stacked area chart (ax.stackplot).

        Parameters
        ----------
        x : list of float
            Shared X values.
        y_stacks : list of list of float
            One sublist per stack layer (same length as x).
        output_path : str
        labels : list of str, optional
            Layer labels for legend.
        colors : list of str, optional
        alpha : float
        baseline : str
            "zero", "sym", "wiggle", "weighted_wiggle".
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {"type": "stackplot", "x": x, "y": y_stacks}
        if labels is not None:
            ps["labels"] = labels
        if colors is not None:
            ps["colors"] = colors
        if alpha != 1.0:
            ps["alpha"] = alpha
        if baseline != "zero":
            ps["baseline"] = baseline
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
