#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convenience functions for the caption system."""

__all__ = [
    "add_figure_caption",
    "add_panel_captions",
    "export_captions",
    "cross_ref",
    "create_figure_list",
    "quick_caption",
    "save_caption_multiple_formats",
]

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ._caption import caption_manager
from ._formats import (
    format_caption_for_md,
    format_caption_for_tex,
    format_caption_for_txt,
)


def add_figure_caption(fig: Any, caption: str, **kwargs) -> str:
    """Add a figure caption.

    See ScientificCaption.add_figure_caption for full documentation.

    Parameters
    ----------
    fig : matplotlib.figure.Figure or RecordingFigure
        The figure to add caption to.
    caption : str
        The caption text.
    **kwargs
        Additional arguments passed to ScientificCaption.add_figure_caption.

    Returns
    -------
    str
        The formatted caption text.
    """
    return caption_manager.add_figure_caption(fig, caption, **kwargs)


def add_panel_captions(
    fig: Any, axes: Any, panel_captions: Union[List[str], Dict[str, str]], **kwargs
) -> Dict[str, str]:
    """Add panel captions (A, B, C, etc.) to subplot panels.

    See ScientificCaption.add_panel_captions for full documentation.

    Parameters
    ----------
    fig : matplotlib.figure.Figure or RecordingFigure
        The figure containing panels.
    axes : Axes, list, or ndarray
        Axes objects for each panel.
    panel_captions : list or dict
        Caption text for each panel.
    **kwargs
        Additional arguments passed to ScientificCaption.add_panel_captions.

    Returns
    -------
    dict
        Dictionary mapping panel labels to full caption text.
    """
    return caption_manager.add_panel_captions(fig, axes, panel_captions, **kwargs)


def export_captions(file_path: str = "figure_captions.txt"):
    """Export all registered captions to a file.

    Parameters
    ----------
    file_path : str, optional
        Output file path. Default: "figure_captions.txt".
    """
    return caption_manager.export_all_captions(file_path)


def cross_ref(figure_label: str) -> str:
    """Get a cross-reference string for a figure.

    Parameters
    ----------
    figure_label : str
        The figure label to reference (e.g., "Figure 1").

    Returns
    -------
    str
        Cross-reference string.
    """
    return caption_manager.get_cross_reference(figure_label)


def create_figure_list(output_file: str = "figure_list.txt", fmt: str = "txt"):
    """Create a comprehensive list of all figures and their captions.

    Parameters
    ----------
    output_file : str, optional
        Output filename. Default: "figure_list.txt".
    fmt : str, optional
        Output format: "txt", "tex", "md". Default: "txt".
    """
    return caption_manager.create_figure_list(output_file, fmt)


def quick_caption(fig: Any, caption: str, save_path: Optional[str] = None, **kwargs):
    """Quick way to add caption and save to multiple formats.

    Parameters
    ----------
    fig : matplotlib.figure.Figure or RecordingFigure
        Figure to caption.
    caption : str
        Caption text.
    save_path : str, optional
        Base path for saving (uses figure number if None).
    **kwargs
        Additional arguments for caption formatting.

    Returns
    -------
    str
        The formatted caption text.
    """
    if save_path is None:
        save_path = f"figure_{caption_manager.figure_counter + 1}"

    # Save in all formats
    save_caption_multiple_formats(caption, save_path, **kwargs)

    # Add visual caption to figure
    return add_figure_caption(fig, caption, **kwargs)


def save_caption_multiple_formats(
    caption: str,
    base_filename: str,
    figure_label: Optional[str] = None,
    style: str = "scientific",
    save_txt: bool = True,
    save_tex: bool = True,
    save_md: bool = True,
    wrap_width: int = 80,
):
    """Save caption in multiple formats (TXT, TeX, Markdown).

    Parameters
    ----------
    caption : str
        The caption text.
    base_filename : str
        Base filename without extension.
    figure_label : str, optional
        Figure label (auto-generated if None).
    style : str, optional
        Caption style. Default: "scientific".
    save_txt : bool, optional
        Save as plain text. Default: True.
    save_tex : bool, optional
        Save as LaTeX. Default: True.
    save_md : bool, optional
        Save as Markdown. Default: True.
    wrap_width : int, optional
        Text wrapping width. Default: 80.
    """
    if figure_label is None:
        caption_manager.figure_counter += 1
        figure_label = f"Figure {caption_manager.figure_counter}"

    # Create formatted versions
    txt_caption = format_caption_for_txt(caption, figure_label, style, wrap_width)
    tex_caption = format_caption_for_tex(caption, figure_label, style, wrap_width)
    md_caption = format_caption_for_md(caption, figure_label, style, wrap_width)

    # Save files
    if save_txt:
        txt_file = f"{base_filename}_caption.txt"
        Path(txt_file).write_text(txt_caption, encoding="utf-8")

    if save_tex:
        tex_file = f"{base_filename}_caption.tex"
        Path(tex_file).write_text(tex_caption, encoding="utf-8")

    if save_md:
        md_file = f"{base_filename}_caption.md"
        Path(md_file).write_text(md_caption, encoding="utf-8")


# EOF
