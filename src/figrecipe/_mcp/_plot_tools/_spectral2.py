#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: csd, cohere, angle_spectrum, magnitude_spectrum, phase_spectrum."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register spectral analysis tools on *mcp*."""

    @mcp.tool
    def plt_csd(
        x: Union[List[float], str],
        y: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        Fs: float = 2.0,
        NFFT: int = 256,
        color: Optional[str] = None,
        label: Optional[str] = None,
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
        """Plot cross-spectral density (ax.csd).

        Parameters
        ----------
        x, y : list of float  — Two 1D time series.
        output_path : str
        Fs : float  — Sampling frequency.
        NFFT : int  — FFT window size.
        color, label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "csd",
            "x": x,
            "y": y,
            "Fs": Fs,
            "NFFT": NFFT,
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
    def plt_cohere(
        x: Union[List[float], str],
        y: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        Fs: float = 2.0,
        NFFT: int = 256,
        color: Optional[str] = None,
        label: Optional[str] = None,
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
        """Plot coherence between two signals (ax.cohere).

        Parameters
        ----------
        x, y : list of float  — Two 1D time series.
        output_path : str
        Fs : float  — Sampling frequency.
        NFFT : int  — FFT window size.
        color, label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "cohere",
            "x": x,
            "y": y,
            "Fs": Fs,
            "NFFT": NFFT,
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
    def plt_angle_spectrum(
        x: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        Fs: float = 2.0,
        Fc: float = 0.0,
        color: Optional[str] = None,
        label: Optional[str] = None,
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
        """Plot angle spectrum (ax.angle_spectrum).

        Parameters
        ----------
        x : list of float  — 1D signal.
        output_path : str
        Fs : float  — Sampling frequency.
        Fc : float  — Center frequency.
        color, label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "angle_spectrum",
            "x": x,
            "Fs": Fs,
            "Fc": Fc,
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
    def plt_magnitude_spectrum(
        x: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        Fs: float = 2.0,
        Fc: float = 0.0,
        scale: str = "linear",
        color: Optional[str] = None,
        label: Optional[str] = None,
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
        """Plot magnitude spectrum (ax.magnitude_spectrum).

        Parameters
        ----------
        x : list of float  — 1D signal.
        output_path : str
        Fs : float  — Sampling frequency.
        Fc : float  — Center frequency.
        scale : str  — "linear", "dB".
        color, label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "magnitude_spectrum",
            "x": x,
            "Fs": Fs,
            "Fc": Fc,
            "scale": scale,
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
    def plt_phase_spectrum(
        x: Union[List[float], str],
        output_path: str,
        data_file: Optional[str] = None,
        Fs: float = 2.0,
        Fc: float = 0.0,
        color: Optional[str] = None,
        label: Optional[str] = None,
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
        """Plot phase spectrum (ax.phase_spectrum).

        Parameters
        ----------
        x : list of float  — 1D signal.
        output_path : str
        Fs : float  — Sampling frequency.
        Fc : float  — Center frequency.
        color, label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "phase_spectrum",
            "x": x,
            "Fs": Fs,
            "Fc": Fc,
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


# EOF
