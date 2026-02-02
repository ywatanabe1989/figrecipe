#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract spec, style, and data from FigureRecord."""

from datetime import datetime
from typing import Any, Dict

import numpy as np
import pandas as pd


def extract_spec_from_record(record) -> Dict[str, Any]:
    """Extract semantic specification from FigureRecord.

    Parameters
    ----------
    record : FigureRecord
        The figure record.

    Returns
    -------
    dict
        Specification dictionary (WHAT to plot).
    """
    spec = {
        "version": "1.0",
        "id": record.id,
        "created": datetime.now().isoformat(),
        "figure": {
            "width_inches": record.figsize[0] if record.figsize else None,
            "height_inches": record.figsize[1] if record.figsize else None,
            "dpi": record.dpi,
        },
        "axes": {},
    }

    # Add mm_layout if present
    if hasattr(record, "mm_layout") and record.mm_layout:
        spec["figure"]["mm_layout"] = record.mm_layout

    # Extract axes specifications
    for ax_key, ax_record in record.axes.items():
        ax_spec = {
            "position": ax_record.position,
            "bbox": ax_record.bbox,
            "traces": [],
        }

        # Extract trace specifications (calls)
        for call in ax_record.calls:
            trace_spec = {
                "id": call.id,
                "function": call.function,
                "data_columns": _extract_data_column_refs(call),
            }

            # Include non-data kwargs (visual properties go to style)
            kwargs = {}
            if isinstance(call.kwargs, dict):
                for name, value in call.kwargs.items():
                    if name not in ("id",):
                        kwargs[name] = value
            else:
                for kwarg in call.kwargs:
                    if kwarg.name not in ("id",):
                        kwargs[kwarg.name] = kwarg.value
            if kwargs:
                trace_spec["kwargs"] = kwargs

            ax_spec["traces"].append(trace_spec)

        # Extract decorations
        decorations = []
        for dec in ax_record.decorations:
            dec_spec = {
                "id": dec.id,
                "function": dec.function,
            }
            if isinstance(dec.kwargs, dict):
                kwargs = {k: v for k, v in dec.kwargs.items() if k != "id"}
            else:
                kwargs = {kw.name: kw.value for kw in dec.kwargs if kw.name != "id"}
            if kwargs:
                dec_spec["kwargs"] = kwargs

            # Include args (e.g., text content, positions)
            args = []
            for arg in dec.args:
                # Args can be dicts or objects
                if isinstance(arg, dict):
                    data = arg.get("data")
                    name = arg.get("name", "data")
                else:
                    data = getattr(arg, "data", None)
                    name = getattr(arg, "name", "data")

                if isinstance(data, (list, np.ndarray)):
                    args.append({"name": name, "type": "data"})
                else:
                    args.append({"name": name, "value": data})
            if args:
                dec_spec["args"] = args

            decorations.append(dec_spec)

        if decorations:
            ax_spec["decorations"] = decorations

        spec["axes"][ax_key] = ax_spec

    return spec


def _extract_data_column_refs(call) -> Dict[str, str]:
    """Extract column references for data in a call.

    Parameters
    ----------
    call : CallRecord
        The call record.

    Returns
    -------
    dict
        Mapping of argument name to CSV column name.
    """
    refs = {}
    for arg in call.args:
        # Args can be dicts or objects
        if isinstance(arg, dict):
            has_array = "_array" in arg
            data = arg.get("data")
            name = arg.get("name", "data")
        else:
            has_array = hasattr(arg, "_array")
            data = getattr(arg, "data", None)
            name = getattr(arg, "name", "data")

        if has_array or isinstance(data, (list, np.ndarray)):
            col_name = f"{call.id}_{name}"
            refs[name] = col_name
    return refs


def extract_style_from_record(record) -> Dict[str, Any]:
    """Extract style settings from FigureRecord.

    Parameters
    ----------
    record : FigureRecord
        The figure record.

    Returns
    -------
    dict
        Style dictionary (HOW it looks).
    """
    style = {
        "version": "1.0",
        "global": {},
        "axes": {},
    }

    # Try to get loaded style
    try:
        from ..styles._style_loader import _STYLE_CACHE

        if _STYLE_CACHE is not None:
            style["global"]["preset"] = getattr(_STYLE_CACHE, "_preset_name", None)
    except Exception:
        pass

    # Extract per-axes styles
    for ax_key, ax_record in record.axes.items():
        ax_style = {"traces": {}}

        for call in ax_record.calls:
            trace_style = {}

            # Extract visual properties from kwargs
            visual_props = [
                "color",
                "linewidth",
                "linestyle",
                "marker",
                "markersize",
                "alpha",
                "edgecolor",
                "facecolor",
                "fontsize",
                "fontweight",
            ]
            if isinstance(call.kwargs, dict):
                for name, value in call.kwargs.items():
                    if name in visual_props:
                        trace_style[name] = value
            else:
                for kwarg in call.kwargs:
                    if kwarg.name in visual_props:
                        trace_style[kwarg.name] = kwarg.value

            if trace_style:
                ax_style["traces"][call.id] = trace_style

        if ax_style["traces"]:
            style["axes"][ax_key] = ax_style

    return style


def extract_data_from_record(record) -> pd.DataFrame:
    """Extract all data arrays from FigureRecord as DataFrame.

    Parameters
    ----------
    record : FigureRecord
        The figure record.

    Returns
    -------
    pd.DataFrame
        DataFrame with all data columns.
    """
    columns = {}
    max_len = 0

    for ax_key, ax_record in record.axes.items():
        for call in ax_record.calls:
            for arg in call.args:
                arr = None
                name = None

                # Args can be dicts or objects
                if isinstance(arg, dict):
                    name = arg.get("name", "data")
                    if "_array" in arg:
                        arr = arg["_array"]
                    elif isinstance(arg.get("data"), np.ndarray):
                        arr = arg["data"]
                    elif isinstance(arg.get("data"), list):
                        arr = np.array(arg["data"])
                else:
                    name = getattr(arg, "name", "data")
                    if hasattr(arg, "_array"):
                        arr = arg._array
                    elif isinstance(getattr(arg, "data", None), np.ndarray):
                        arr = arg.data
                    elif isinstance(getattr(arg, "data", None), list):
                        arr = np.array(arg.data)

                if arr is not None:
                    col_name = f"{call.id}_{name}"
                    columns[col_name] = arr
                    max_len = max(max_len, len(arr))

    # Pad shorter arrays with NaN
    if columns:
        for col_name, arr in columns.items():
            if len(arr) < max_len:
                padded = np.full(max_len, np.nan)
                padded[: len(arr)] = arr
                columns[col_name] = padded

        return pd.DataFrame(columns)

    return pd.DataFrame()
