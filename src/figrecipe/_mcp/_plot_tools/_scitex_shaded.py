#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP fr_* tools: shaded line family (fr_line, fr_shaded_line, fr_mean_*)."""


from typing import Any, Dict, List, Optional, Union

from figrecipe._branding import BRAND_ALIAS as _BA

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register shaded-line fr_* tools on *mcp*."""

    @mcp.tool(f"{_BA}_line")
    def _impl_line(
        values: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        xx: Optional[Union[List[float], str]] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        linewidth: float = 1.5,
        alpha: float = 1.0,
        linestyle: str = "-",
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
        """Plot a 1D array as a line (ax.stx_line).

        Parameters
        ----------
        values : list of float or str — 1D data or column name in data_file.
        xx : list of float, optional — x-axis values.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color, label, linewidth, alpha, linestyle : ...
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_line",
            "x": values,
            "linewidth": linewidth,
            "linestyle": linestyle,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if xx is not None:
            ps["y"] = xx
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

    @mcp.tool(f"{_BA}_shaded_line")
    def _impl_shaded_line(
        xs: Union[List[float], str],
        y_lower: Union[List[float], str],
        y_middle: Union[List[float], str],
        y_upper: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 0.3,
        linewidth: float = 1.5,
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
        """Plot line(s) with shaded uncertainty regions (ax.stx_shaded_line).

        Parameters
        ----------
        xs : list of float or str — x-axis values.
        y_lower : list of float or str — Lower bound.
        y_middle : list of float or str — Center line.
        y_upper : list of float or str — Upper bound.
        output_path : str
        data_file : str, optional — CSV file for column lookup.
        color, label, alpha, linewidth : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_shaded_line",
            "x": xs,
            "y_lower": y_lower,
            "y_middle": y_middle,
            "y_upper": y_upper,
            "linewidth": linewidth,
            "alpha": alpha,
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

    @mcp.tool(f"{_BA}_mean_std")
    def _impl_mean_std(
        values_2d: Union[List[List[float]], str],
        output_path: str,
        data_file: Optional[str] = None,
        xx: Optional[Union[List[float], str]] = None,
        sd: float = 1.0,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 0.3,
        linewidth: float = 1.5,
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
        """Plot mean ± sd with shaded region (ax.stx_mean_std).

        Parameters
        ----------
        values_2d : 2D list — Rows=observations, cols=timepoints.
        xx : list of float, optional — x-axis values.
        sd : float — Number of standard deviations (default 1).
        output_path : str
        data_file : str, optional — CSV column lookup.
        color, label, alpha, linewidth : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_mean_std",
            "x": values_2d,
            "sd": sd,
            "linewidth": linewidth,
            "alpha": alpha,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if xx is not None:
            ps["y"] = xx
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

    @mcp.tool(f"{_BA}_mean_ci")
    def _impl_mean_ci(
        values_2d: Union[List[List[float]], str],
        output_path: str,
        data_file: Optional[str] = None,
        xx: Optional[Union[List[float], str]] = None,
        perc: float = 95.0,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 0.3,
        linewidth: float = 1.5,
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
        """Plot mean with CI shading (ax.stx_mean_ci).

        Parameters
        ----------
        values_2d : 2D list — Rows=observations, cols=timepoints.
        xx : list of float, optional — x-axis values.
        perc : float — CI percentile (default 95).
        output_path : str
        data_file : str, optional — CSV column lookup.
        color, label, alpha, linewidth : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_mean_ci",
            "x": values_2d,
            "perc": perc,
            "linewidth": linewidth,
            "alpha": alpha,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if xx is not None:
            ps["y"] = xx
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

    @mcp.tool(f"{_BA}_median_iqr")
    def _impl_median_iqr(
        values_2d: Union[List[List[float]], str],
        output_path: str,
        data_file: Optional[str] = None,
        xx: Optional[Union[List[float], str]] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        alpha: float = 0.3,
        linewidth: float = 1.5,
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
        """Plot median with IQR shading (ax.stx_median_iqr).

        Parameters
        ----------
        values_2d : 2D list — Rows=observations, cols=timepoints.
        xx : list of float, optional — x-axis values.
        output_path : str
        data_file : str, optional — CSV column lookup.
        color, label, alpha, linewidth : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": f"{_BA}_median_iqr",
            "x": values_2d,
            "linewidth": linewidth,
            "alpha": alpha,
        }
        if data_file is not None:
            ps["data_file"] = data_file
        if xx is not None:
            ps["y"] = xx
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


# EOF
