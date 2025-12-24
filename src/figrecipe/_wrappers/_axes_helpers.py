#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper functions for RecordingAxes."""

from typing import Any, Dict, Optional


def args_have_fmt_color(args: tuple) -> bool:
    """Check if args contain a matplotlib fmt string with color specifier."""
    color_codes = set("bgrcmykw")
    for arg in args:
        if isinstance(arg, str) and len(arg) >= 1 and len(arg) <= 4:
            if arg[0] in color_codes:
                return True
    return False


def extract_color_from_result(method_name: str, result) -> Optional[str]:
    """Extract actual color used from plot result."""
    try:
        if method_name == "plot":
            if result and hasattr(result[0], "get_color"):
                return result[0].get_color()
        elif method_name == "scatter":
            if hasattr(result, "get_facecolor"):
                fc = result.get_facecolor()
                if len(fc) > 0:
                    import matplotlib.colors as mcolors

                    return mcolors.to_hex(fc[0])
        elif method_name in ("bar", "barh"):
            if hasattr(result, "patches") and result.patches:
                fc = result.patches[0].get_facecolor()
                import matplotlib.colors as mcolors

                return mcolors.to_hex(fc)
        elif method_name == "step":
            if result and hasattr(result[0], "get_color"):
                return result[0].get_color()
        elif method_name == "fill_between":
            if hasattr(result, "get_facecolor"):
                fc = result.get_facecolor()
                if len(fc) > 0:
                    import matplotlib.colors as mcolors

                    return mcolors.to_hex(fc[0])
    except Exception:
        pass
    return None


def process_result_refs_in_args(
    args: tuple,
    method_name: str,
    result_refs: Dict[int, str],
    referencing_methods: set,
) -> tuple:
    """Process args to replace matplotlib objects with references."""
    if method_name not in referencing_methods:
        return args

    import builtins

    processed = []
    for arg in args:
        obj_id = builtins.id(arg)
        if obj_id in result_refs:
            processed.append({"__ref__": result_refs[obj_id]})
        else:
            processed.append(arg)
    return tuple(processed)


def record_call_with_color_capture(
    recorder,
    position: tuple,
    method_name: str,
    args: tuple,
    kwargs: dict,
    result,
    call_id: Optional[str],
    result_refs: Dict[int, str],
    referencing_methods: set,
    referenceable_methods: set,
) -> Any:
    """Record a call with color capture and result reference handling."""
    recorded_kwargs = kwargs.copy()

    # Capture colors for methods using color cycle
    if method_name in ("plot", "scatter", "bar", "barh", "step", "fill_between"):
        has_fmt_color = args_have_fmt_color(args)
        if (
            "color" not in recorded_kwargs
            and "c" not in recorded_kwargs
            and not has_fmt_color
        ):
            actual_color = extract_color_from_result(method_name, result)
            if actual_color is not None:
                recorded_kwargs["color"] = actual_color

        if method_name == "fill_between" and "edgecolor" not in recorded_kwargs:
            if hasattr(result, "get_edgecolor"):
                ec = result.get_edgecolor()
                if len(ec) == 0:
                    recorded_kwargs["edgecolor"] = "none"

    # Process args for result references
    processed_args = process_result_refs_in_args(
        args, method_name, result_refs, referencing_methods
    )

    call_record = recorder.record_call(
        ax_position=position,
        method_name=method_name,
        args=processed_args,
        kwargs=recorded_kwargs,
        call_id=call_id,
    )

    # Store result reference if applicable
    if method_name in referenceable_methods:
        import builtins

        result_refs[builtins.id(result)] = call_record.id

    return call_record


__all__ = [
    "args_have_fmt_color",
    "extract_color_from_result",
    "process_result_refs_in_args",
    "record_call_with_color_capture",
]

# EOF
