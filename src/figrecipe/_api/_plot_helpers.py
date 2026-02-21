#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper functions for declarative plot creation."""

from typing import Any, Dict, List

import numpy as np

# stx_*/branding-alias method type groups (driven by FIGRECIPE_ALIAS env var)
from figrecipe._branding import BRAND_ALIAS as _BA  # noqa: E402

from ._data_resolver import resolve_data  # noqa: F401 (re-exported)
from ._decorations import (  # noqa: F401
    apply_decorations,
    apply_stat_annotations,
    apply_text_annotations,
)

_FR_SINGLE_ARG = {
    f"stx_{s}" for s in ("line", "ecdf", "raster", "heatmap", "image", "violin")
} | {f"{_BA}_{s}" for s in ("line", "ecdf", "raster", "heatmap", "image", "violin")}
_FR_TWO_ARG = {"stx_scatter_hist", f"{_BA}_scatter_hist"}
_FR_LINE_XX = {f"stx_{s}" for s in ("mean_std", "mean_ci", "median_iqr")} | {
    f"{_BA}_{s}" for s in ("mean_std", "mean_ci", "median_iqr")
}
_FR_SHADED = {"stx_shaded_line", f"{_BA}_shaded_line"}
_FR_FILLV = {"stx_fillv", f"{_BA}_fillv"}
_FR_CONF_MAT = {"stx_conf_mat", f"{_BA}_conf_mat"}
_FR_RECTANGLE = {"stx_rectangle", f"{_BA}_rectangle"}
del _BA

# Plot types that produce a ScalarMappable and need an auto-colorbar
_COLORBAR_TYPES = {"imshow", "matshow", "heatmap", "pcolor", "pcolormesh", "contourf"}


def apply_plots(
    ax, plots: List[Dict[str, Any]], plot_types: Dict, reserved_keys: set
) -> None:
    """Apply plot elements to an axes."""
    from ..styles._internal import resolve_colors_in_kwargs

    boxplot_reserved_keys = {"color", "colors"}

    for plot_spec in plots:
        plot_type = plot_spec.get("type", "line")

        if plot_type not in plot_types:
            raise ValueError(f"Unknown plot type: {plot_type}")

        method_name = plot_types[plot_type]
        method = getattr(ax, method_name)

        data_spec = plot_spec.get("data", {})
        data_file = plot_spec.get("data_file")

        if isinstance(data_spec, dict):
            x = resolve_data(
                plot_spec.get("x") or data_spec.get("x"), data_file=data_file
            )
            y = resolve_data(
                plot_spec.get("y") or data_spec.get("y"), data_file=data_file
            )
            z = resolve_data(
                plot_spec.get("z") or data_spec.get("z"), data_file=data_file
            )
            data = (
                resolve_data(data_spec.get("dataset"), data_file=data_file)
                if "dataset" in data_spec
                else None
            )
        else:
            x = resolve_data(plot_spec.get("x"), data_file=data_file)
            y = resolve_data(plot_spec.get("y"), data_file=data_file)
            z = resolve_data(plot_spec.get("z"), data_file=data_file)
            data = resolve_data(data_spec, data_file=data_file)

        excluded_keys = reserved_keys.copy()
        if plot_type in ("boxplot", "box"):
            excluded_keys = excluded_keys | boxplot_reserved_keys
        kwargs = {k: v for k, v in plot_spec.items() if k not in excluded_keys}
        kwargs = resolve_colors_in_kwargs(kwargs)

        _call_plot_method(method, plot_type, x, y, z, data, kwargs, plot_spec, ax)


def _call_plot_method(method, plot_type, x, y, z, data, kwargs, plot_spec, ax=None):
    """Call the appropriate plot method based on plot type."""
    if plot_type in (
        "hist",
        "pie",
        "eventplot",
        "acorr",
        "ecdf",
        "angle_spectrum",
        "magnitude_spectrum",
        "phase_spectrum",
    ):
        if x is not None:
            method(x, **kwargs)
        elif data is not None:
            method(data, **kwargs)
    elif plot_type in ("boxplot", "box", "violinplot", "violin"):
        _apply_boxplot(method, plot_type, x, data, kwargs, plot_spec, ax)
    elif plot_type in ("imshow", "matshow", "heatmap", "spy"):
        # 2D data — check data, then z, then x (user often passes matrix as x)
        plot_data = data if data is not None else (z if z is not None else x)
        if plot_data is not None:
            result = method(plot_data, **kwargs)
            if plot_type != "spy" and ax is not None:
                _maybe_add_colorbar(result, ax, plot_spec)
    elif plot_type in ("pcolor", "pcolormesh"):
        if x is not None and y is not None and z is not None:
            result = method(x, y, z, **kwargs)
        elif z is not None:
            result = method(z, **kwargs)
        elif data is not None:
            result = method(data, **kwargs)
        else:
            result = None
        if result is not None and ax is not None:
            _maybe_add_colorbar(result, ax, plot_spec)
    elif plot_type == "contourf":
        if x is not None and y is not None and z is not None:
            result = method(x, y, z, **kwargs)
        elif z is not None:
            result = method(z, **kwargs)
        else:
            result = None
        if result is not None and ax is not None:
            _maybe_add_colorbar(result, ax, plot_spec)
    elif plot_type == "contour":
        if x is not None and y is not None and z is not None:
            method(x, y, z, **kwargs)
        elif z is not None:
            method(z, **kwargs)
        elif data is not None:
            method(data, **kwargs)
    elif plot_type == "hexbin":
        if x is not None and y is not None:
            result = method(x, y, **kwargs)
            if ax is not None:
                _maybe_add_colorbar(result, ax, plot_spec)
    elif plot_type == "hist2d":
        if x is not None and y is not None:
            _counts, _xe, _ye, result = method(x, y, **kwargs)
            if ax is not None:
                _maybe_add_colorbar(result, ax, plot_spec)
    elif plot_type in ("xcorr", "csd", "cohere"):
        if x is not None and y is not None:
            method(x, y, **kwargs)
    elif plot_type == "stairs":
        if x is not None and y is not None:
            method(x, y, **kwargs)
        elif x is not None:
            method(x, **kwargs)
    elif plot_type == "stackplot":
        if x is not None and y is not None:
            y_arr = np.asarray(y)
            if y_arr.ndim == 1:
                method(x, y_arr, **kwargs)
            else:
                method(x, *y_arr, **kwargs)
    elif plot_type == "fill_betweenx":
        y2 = plot_spec.get("y2")
        ykw = {k: v for k, v in kwargs.items() if k != "y2"}
        if x is not None and y is not None and y2 is not None:
            method(x, y, y2, **ykw)
        elif x is not None and y is not None:
            method(x, y, **ykw)
    elif plot_type in ("quiver", "streamplot"):
        u = plot_spec.get("u")
        v = plot_spec.get("v")
        ukw = {k: v2 for k, v2 in kwargs.items() if k not in ("u", "v")}
        if x is not None and y is not None and u is not None and v is not None:
            method(x, y, u, v, **ukw)
    elif plot_type in ("bar", "barh"):
        _apply_bar(method, plot_type, x, y, kwargs, plot_spec)
    elif plot_type in _FR_SINGLE_ARG:
        if x is not None:
            method(x, **kwargs)
    elif plot_type in _FR_TWO_ARG:
        if x is not None and y is not None:
            method(x, y, **kwargs)
    elif plot_type in _FR_LINE_XX:
        if x is not None:
            if y is not None:
                method(x, xx=y, **kwargs)
            else:
                method(x, **kwargs)
    elif plot_type in _FR_SHADED:
        y_lower = plot_spec.get("y_lower")
        y_middle = plot_spec.get("y_middle")
        y_upper = plot_spec.get("y_upper")
        if x is not None:
            method(x, y_lower, y_middle, y_upper, **kwargs)
    elif plot_type in _FR_FILLV:
        fillv_kw = {k: v for k, v in kwargs.items() if k in ("color", "alpha")}
        if x is not None and y is not None:
            method(x, y, **fillv_kw)
    elif plot_type in _FR_CONF_MAT:
        if x is not None:
            method(x, **kwargs)
    elif plot_type in _FR_RECTANGLE:
        if x is not None and y is not None:
            method(x, y, **kwargs)
    else:
        if x is not None and y is not None:
            method(x, y, **kwargs)
        elif y is not None:
            method(y, **kwargs)
        elif x is not None:
            method(x, **kwargs)


def _maybe_add_colorbar(mappable, ax, plot_spec):
    """Add a styled colorbar if the plot produced a ScalarMappable."""
    if plot_spec.get("colorbar") is False:
        return
    try:
        from .._utils._colorbar import add_colorbar

        mpl_ax = ax._ax if hasattr(ax, "_ax") else ax
        fig = mpl_ax.get_figure()
        add_colorbar(fig, mappable, ax=mpl_ax)
    except Exception:
        pass  # Non-fatal: colorbar is a nicety


def _apply_bar(method, plot_type, x, y, kwargs, plot_spec):
    """Apply bar/barh with per-bar color cycling when no color is given."""
    from ..styles._color_resolver import get_color_map

    colors_spec = plot_spec.get("colors")
    color_spec = plot_spec.get("color") or kwargs.get("color")

    if colors_spec is not None:
        # Explicit list of colors — pass as color kwarg (matplotlib accepts list)
        kw = {k: v for k, v in kwargs.items() if k != "color"}
        if x is not None and y is not None:
            method(x, y, color=colors_spec, **kw)
        elif x is not None:
            method(x, color=colors_spec, **kw)
    elif color_spec is None:
        # No color given — auto-cycle SCITEX palette
        color_map = get_color_map()
        if color_map:
            _cycle_names = [
                "blue",
                "orange",
                "green",
                "red",
                "purple",
                "brown",
                "pink",
                "gray",
                "yellow",
                "navy",
            ]
            cycle = [color_map[n] for n in _cycle_names if n in color_map]
            if cycle and x is not None and y is not None:
                n_bars = len(y) if hasattr(y, "__len__") else 1
                bar_colors = [cycle[i % len(cycle)] for i in range(n_bars)]
                kw = {k: v for k, v in kwargs.items() if k != "color"}
                method(x, y, color=bar_colors, **kw)
                return
        # Fallback: plain call
        if x is not None and y is not None:
            method(x, y, **kwargs)
        elif x is not None:
            method(x, **kwargs)
    else:
        if x is not None and y is not None:
            method(x, y, **kwargs)
        elif x is not None:
            method(x, **kwargs)


def _apply_boxplot(method, plot_type, x, data, kwargs, plot_spec, ax=None):
    """Apply boxplot or violinplot with color handling."""
    box_colors = plot_spec.get("color") or plot_spec.get("colors")

    if plot_type in ("boxplot", "box"):
        kwargs.setdefault("patch_artist", True)

    plot_data = data if data is not None else x
    # matplotlib boxplot treats columns of a 2D array as groups — convert to
    # a list of 1D arrays so each *row* (user-provided group) becomes one box.
    if (
        plot_type in ("boxplot", "box")
        and isinstance(plot_data, np.ndarray)
        and plot_data.ndim == 2
    ):
        plot_data = list(plot_data)

    if plot_data is not None:
        result = method(plot_data, **kwargs)

        if plot_type in ("boxplot", "box"):
            from ..styles._color_resolver import get_color_map, resolve_color

            boxes = result.get("boxes", [])
            if box_colors is not None:
                if isinstance(box_colors, str):
                    resolved = resolve_color(box_colors)
                    for box in boxes:
                        box.set_facecolor(resolved)
                elif isinstance(box_colors, (list, tuple)):
                    resolved_colors = [
                        resolve_color(c) if isinstance(c, str) else c
                        for c in box_colors
                    ]
                    if len(resolved_colors) != len(boxes):
                        raise ValueError(
                            f"Number of colors ({len(resolved_colors)}) must match "
                            f"number of boxes ({len(boxes)}). "
                            f"Provide exactly one color per group."
                        )
                    for box, color in zip(boxes, resolved_colors):
                        box.set_facecolor(color)
            elif boxes:
                # No colors specified — cycle through SCITEX palette
                color_map = get_color_map()
                if color_map:
                    _cycle_names = [
                        "blue",
                        "orange",
                        "green",
                        "red",
                        "purple",
                        "brown",
                        "pink",
                        "gray",
                        "yellow",
                        "navy",
                    ]
                    cycle = [color_map[n] for n in _cycle_names if n in color_map]
                    if cycle:
                        for i, box in enumerate(boxes):
                            box.set_facecolor(cycle[i % len(cycle)])

            if ax is not None:
                from ..styles._plot_styles import apply_boxplot_style
                from ..styles._style_loader import get_current_style_dict

                mpl_ax = ax._ax if hasattr(ax, "_ax") else ax
                style_dict = get_current_style_dict()
                apply_boxplot_style(mpl_ax, style_dict)


def clear_csv_cache() -> None:
    """Clear the CSV file cache (delegates to _data_resolver)."""
    from ._data_resolver import clear_csv_cache as _clear

    _clear()


# EOF
