#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP plot tools: plt_specgram, plt_psd."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._base import _create


def register(mcp) -> None:  # noqa: ANN001
    """Register spectral plot tools on *mcp*."""

    @mcp.tool
    def plt_specgram(
        x: List[float],
        output_path: str,
        Fs: float = 1.0,
        NFFT: int = 256,
        noverlap: int = 128,
        cmap: str = "viridis",
        scale: str = "dB",
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        width_mm: float = 100.0,
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
        """Create a spectrogram (ax.specgram).

        Parameters
        ----------
        x : list of float
            1D time-series signal.
        output_path : str
        Fs : float
            Sampling frequency in Hz.
        NFFT : int
            FFT window length.
        noverlap : int
            Overlap between windows.
        cmap : str
        scale : str
            "dB" or "linear".
        vmin, vmax : float, optional
            Color scale limits.
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "specgram",
            "x": x,
            "Fs": Fs,
            "NFFT": NFFT,
            "noverlap": noverlap,
            "cmap": cmap,
            "scale": scale,
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
    def plt_psd(
        x: List[float],
        output_path: str,
        Fs: float = 1.0,
        NFFT: int = 256,
        noverlap: int = 128,
        color: Optional[str] = None,
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
        """Plot power spectral density (ax.psd).

        Parameters
        ----------
        x : list of float
            1D time-series signal.
        output_path : str
        Fs : float
            Sampling frequency in Hz.
        NFFT : int
            FFT window length.
        noverlap : int
            Window overlap.
        color, label : str, optional
        width_mm, height_mm, style, dpi, xlabel, ylabel, title, caption : ...
        legend, xlim, ylim, stat_annotations, stats_results : ...

        Returns
        -------
        dict — {"image_path", "recipe_path", "success"}
        """
        ps: Dict[str, Any] = {
            "type": "psd",
            "x": x,
            "Fs": Fs,
            "NFFT": NFFT,
            "noverlap": noverlap,
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


# EOF
