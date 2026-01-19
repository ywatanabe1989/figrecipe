#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collection processing for hitmap generation.

This package handles the processing of matplotlib collections for hitmap
generation, including scatter plots, fills, lines, quivers, and meshes.
"""

from typing import Any, Dict

from matplotlib.collections import LineCollection, PathCollection, PolyCollection

from ._linecoll import process_linecoll
from ._mesh import process_contour, process_quadmesh
from ._polycoll import determine_fill_type, process_polycoll
from ._quiver import process_barbs, process_quiver
from ._scatter import process_scatter


def process_collections(
    ax,
    ax_idx: int,
    element_id: int,
    original_props: Dict[str, Any],
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process collections (scatter, fills, etc.) on an axes.

    Parameters
    ----------
    ax : Axes
        The matplotlib axes to process.
    ax_idx : int
        Index of the axes.
    element_id : int
        Starting element ID.
    original_props : dict
        Dict to store original properties for restoration.
    color_map : dict
        Dict to store element color mappings.
    ax_info : dict
        Plot type information for this axes.

    Returns
    -------
    int
        Updated element ID.
    """
    from matplotlib.collections import QuadMesh
    from matplotlib.contour import QuadContourSet
    from matplotlib.quiver import Barbs, Quiver
    from matplotlib.tri import TriContourSet

    ax_plot_types = ax_info.get("types", set())
    ax_call_ids = ax_info.get("call_ids", {})
    has_violin = "violinplot" in ax_plot_types
    has_record = len(ax_plot_types) > 0

    # Check for specific fill types
    has_fill_between = "fill_between" in ax_plot_types
    has_fill_betweenx = "fill_betweenx" in ax_plot_types
    has_stackplot = "stackplot" in ax_plot_types
    has_stairs = "stairs" in ax_plot_types
    has_errorbar = "errorbar" in ax_plot_types
    has_stem = "stem" in ax_plot_types
    has_eventplot = "eventplot" in ax_plot_types
    has_hexbin = "hexbin" in ax_plot_types
    has_pcolor = "pcolor" in ax_plot_types
    has_tripcolor = "tripcolor" in ax_plot_types

    # Any fill-type present means we should process PolyCollections
    has_any_fill = (
        has_fill_between
        or has_fill_betweenx
        or has_stackplot
        or has_stairs
        or has_hexbin
        or has_pcolor
        or has_tripcolor
    )

    # Extract call IDs
    violin_ids = list(ax_call_ids.get("violinplot", []))
    scatter_ids = list(ax_call_ids.get("scatter", []))
    quiver_ids = list(ax_call_ids.get("quiver", []))
    barbs_ids = list(ax_call_ids.get("barbs", []))
    fill_between_ids = list(ax_call_ids.get("fill_between", []))
    fill_betweenx_ids = list(ax_call_ids.get("fill_betweenx", []))
    stackplot_ids = list(ax_call_ids.get("stackplot", []))
    stairs_ids = list(ax_call_ids.get("stairs", []))
    hexbin_ids = list(ax_call_ids.get("hexbin", []))
    pcolor_ids = list(ax_call_ids.get("pcolor", []))
    tripcolor_ids = list(ax_call_ids.get("tripcolor", []))
    errorbar_ids = list(ax_call_ids.get("errorbar", []))
    stem_ids = list(ax_call_ids.get("stem", []))
    eventplot_ids = list(ax_call_ids.get("eventplot", []))
    pcolormesh_ids = list(ax_call_ids.get("pcolormesh", []))
    contour_ids = list(ax_call_ids.get("contour", []))
    contourf_ids = list(ax_call_ids.get("contourf", []))
    tricontour_ids = list(ax_call_ids.get("tricontour", []))
    tricontourf_ids = list(ax_call_ids.get("tricontourf", []))

    violin_call_id = violin_ids[0] if violin_ids else None
    pcolormesh_call_id = pcolormesh_ids[0] if pcolormesh_ids else None
    contour_call_id = contour_ids[0] if contour_ids else None
    contourf_call_id = contourf_ids[0] if contourf_ids else None
    tricontour_call_id = tricontour_ids[0] if tricontour_ids else None
    tricontourf_call_id = tricontourf_ids[0] if tricontourf_ids else None
    scatter_coll_idx = 0

    # Separate indices for each fill type
    fill_between_idx = 0
    fill_betweenx_idx = 0
    stackplot_idx = 0
    stairs_idx = 0
    violin_idx = 0
    linecoll_idx = 0

    for i, coll in enumerate(ax.collections):
        if isinstance(coll, Quiver):
            element_id = process_quiver(
                coll, i, ax_idx, element_id, original_props, color_map, quiver_ids
            )
        elif isinstance(coll, Barbs):
            element_id = process_barbs(
                coll, i, ax_idx, element_id, original_props, color_map, barbs_ids
            )
        elif isinstance(coll, PathCollection):
            element_id, scatter_coll_idx = process_scatter(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                scatter_ids,
                scatter_coll_idx,
            )
        elif isinstance(coll, PolyCollection):
            # Determine which fill type this belongs to based on detected types
            fill_info = determine_fill_type(
                has_fill_between,
                has_fill_betweenx,
                has_stackplot,
                has_stairs,
                has_violin,
                has_hexbin,
                has_pcolor,
                has_tripcolor,
                fill_between_ids,
                fill_betweenx_ids,
                stackplot_ids,
                stairs_ids,
                hexbin_ids,
                pcolor_ids,
                tripcolor_ids,
                fill_between_idx,
                fill_betweenx_idx,
                stackplot_idx,
                stairs_idx,
            )
            (
                element_id,
                fill_between_idx,
                fill_betweenx_idx,
                stackplot_idx,
                stairs_idx,
                violin_idx,
            ) = process_polycoll(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                has_violin,
                violin_call_id,
                has_record,
                has_any_fill,
                ax,
                fill_info,
                fill_between_idx,
                fill_betweenx_idx,
                stackplot_idx,
                stairs_idx,
                violin_idx,
            )
        elif isinstance(coll, LineCollection):
            element_id, linecoll_idx = process_linecoll(
                coll,
                i,
                ax_idx,
                element_id,
                original_props,
                color_map,
                has_violin,
                violin_call_id,
                has_errorbar,
                errorbar_ids,
                has_stem,
                stem_ids,
                has_eventplot,
                eventplot_ids,
                linecoll_idx,
            )
        elif isinstance(coll, QuadMesh):
            element_id = process_quadmesh(
                coll, i, ax_idx, element_id, color_map, pcolormesh_call_id
            )
        elif isinstance(coll, QuadContourSet):
            element_id = process_contour(
                coll,
                i,
                ax_idx,
                element_id,
                color_map,
                contour_call_id,
                contourf_call_id,
            )
        elif isinstance(coll, TriContourSet):
            element_id = process_contour(
                coll,
                i,
                ax_idx,
                element_id,
                color_map,
                tricontour_call_id,
                tricontourf_call_id,
            )

    return element_id


__all__ = ["process_collections"]

# EOF
