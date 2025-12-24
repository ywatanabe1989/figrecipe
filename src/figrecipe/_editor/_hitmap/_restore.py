#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Property restoration for hitmap generation."""

from typing import Any, Dict, List

from matplotlib.collections import (
    LineCollection,
    PathCollection,
    PolyCollection,
)


def restore_axes_properties(
    axes_list: List,
    original_props: Dict[str, Any],
    include_text: bool = True,
) -> None:
    """Restore original properties to axes elements.

    Parameters
    ----------
    axes_list : list
        List of axes to restore.
    original_props : dict
        Dictionary of original properties keyed by element key.
    include_text : bool
        Whether text elements were modified.
    """
    for ax_idx, ax in enumerate(axes_list):
        # Restore lines
        for i, line in enumerate(ax.get_lines()):
            key = f"ax{ax_idx}_line{i}"
            if key in original_props:
                props = original_props[key]
                line.set_color(props["color"])
                line.set_markerfacecolor(props["markerfacecolor"])
                line.set_markeredgecolor(props["markeredgecolor"])

        # Restore collections
        for i, coll in enumerate(ax.collections):
            if isinstance(coll, PathCollection):
                key = f"ax{ax_idx}_scatter{i}"
                if key in original_props:
                    props = original_props[key]
                    coll.set_facecolors(props["facecolors"])
                    coll.set_edgecolors(props["edgecolors"])
            elif isinstance(coll, PolyCollection):
                key = f"ax{ax_idx}_fill{i}"
                if key in original_props:
                    props = original_props[key]
                    coll.set_facecolors(props["facecolors"])
                    coll.set_edgecolors(props["edgecolors"])
            elif isinstance(coll, LineCollection):
                key = f"ax{ax_idx}_linecoll{i}"
                if key in original_props:
                    props = original_props[key]
                    if len(props["colors"]) > 0:
                        coll.set_color(props["colors"])

        # Restore patches
        for i, patch in enumerate(ax.patches):
            key = f"ax{ax_idx}_bar{i}"
            if key in original_props:
                props = original_props[key]
                patch.set_facecolor(props["facecolor"])
                patch.set_edgecolor(props["edgecolor"])

        # Restore text
        if include_text:
            key = f"ax{ax_idx}_title"
            if key in original_props:
                ax.title.set_color(original_props[key]["color"])

            key = f"ax{ax_idx}_xlabel"
            if key in original_props:
                ax.xaxis.label.set_color(original_props[key]["color"])

            key = f"ax{ax_idx}_ylabel"
            if key in original_props:
                ax.yaxis.label.set_color(original_props[key]["color"])

        # Restore legend
        key = f"ax{ax_idx}_legend"
        if key in original_props:
            legend = ax.get_legend()
            if legend:
                frame = legend.get_frame()
                props = original_props[key]
                frame.set_facecolor(props["facecolor"])
                frame.set_edgecolor(props["edgecolor"])

        # Restore spines
        for spine in ax.spines.values():
            spine.set_color("black")

        # Restore tick colors
        ax.tick_params(colors="black")


def restore_figure_text(
    mpl_fig,
    original_props: Dict[str, Any],
    include_text: bool = True,
) -> None:
    """Restore figure-level text properties.

    Parameters
    ----------
    mpl_fig : Figure
        The matplotlib figure.
    original_props : dict
        Dictionary of original properties.
    include_text : bool
        Whether text elements were modified.
    """
    if not include_text:
        return

    key = "fig_suptitle"
    if key in original_props and hasattr(mpl_fig, "_suptitle") and mpl_fig._suptitle:
        mpl_fig._suptitle.set_color(original_props[key]["color"])

    key = "fig_supxlabel"
    if key in original_props and hasattr(mpl_fig, "_supxlabel") and mpl_fig._supxlabel:
        mpl_fig._supxlabel.set_color(original_props[key]["color"])

    key = "fig_supylabel"
    if key in original_props and hasattr(mpl_fig, "_supylabel") and mpl_fig._supylabel:
        mpl_fig._supylabel.set_color(original_props[key]["color"])


def restore_backgrounds(fig, axes_list: List) -> None:
    """Restore background colors.

    Parameters
    ----------
    fig : Figure
        The figure.
    axes_list : list
        List of axes.
    """
    fig.patch.set_facecolor("white")
    for ax in axes_list:
        ax.set_facecolor("white")


__all__ = [
    "restore_axes_properties",
    "restore_figure_text",
    "restore_backgrounds",
]

# EOF
