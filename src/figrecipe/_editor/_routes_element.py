#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Element-related Flask route handlers for the figure editor.
Handles calls, download, and shutdown routes.
"""

from flask import jsonify, request, send_file

from ._helpers import render_with_overrides, to_json_serializable


def register_element_routes(app, editor):
    """Register element-related routes with the Flask app."""
    from ._hitmap import generate_hitmap, hitmap_to_base64
    from ._renderer import render_download

    @app.route("/calls")
    def get_calls():
        """Get all recorded calls with their signatures."""
        from .._signatures import get_signature

        calls_data = {}
        if hasattr(editor.fig, "record"):
            for ax_key, ax_record in editor.fig.record.axes.items():
                for call in ax_record.calls:
                    call_id = call.id
                    func_name = call.function
                    sig = get_signature(func_name)

                    calls_data[call_id] = {
                        "function": func_name,
                        "ax_key": ax_key,
                        "args": to_json_serializable(call.args),
                        "kwargs": to_json_serializable(call.kwargs),
                        "signature": {
                            "args": sig.get("args", []),
                            "kwargs": {
                                k: v
                                for k, v in sig.get("kwargs", {}).items()
                                if k != "**kwargs"
                            },
                        },
                    }

        return jsonify(calls_data)

    @app.route("/call/<call_id>")
    def get_call(call_id):
        """Get recorded call data by call_id."""
        from .._signatures import get_signature

        if hasattr(editor.fig, "record"):
            for ax_key, ax_record in editor.fig.record.axes.items():
                for call in ax_record.calls:
                    if call.id == call_id:
                        sig = get_signature(call.function)
                        return jsonify(
                            {
                                "call_id": call_id,
                                "function": call.function,
                                "ax_key": ax_key,
                                "args": call.args,
                                "kwargs": call.kwargs,
                                "signature": {
                                    "args": sig.get("args", []),
                                    "kwargs": {
                                        k: v
                                        for k, v in sig.get("kwargs", {}).items()
                                        if k != "**kwargs"
                                    },
                                },
                            }
                        )

        return jsonify({"error": f"Call {call_id} not found"}), 404

    @app.route("/update_call", methods=["POST"])
    def update_call():
        """Update a call's kwargs and re-render.

        Uses IDENTICAL pipeline as all other routes:
        1. Store override via set_call_override()
        2. Call render_with_overrides(editor.fig) - same as initial render

        The actual property application happens in apply_overrides() via
        apply_call_overrides() - SINGLE SOURCE OF TRUTH.
        """
        data = request.get_json() or {}
        call_id = data.get("call_id")
        param = data.get("param")
        value = data.get("value")

        if not call_id or not param:
            return jsonify({"error": "Missing call_id or param"}), 400

        # Find the call and store override
        updated = False
        if hasattr(editor.fig, "record"):
            for ax_key, ax_record in editor.fig.record.axes.items():
                for call in ax_record.calls:
                    if call.id == call_id:
                        # Store override - will be applied via apply_overrides()
                        editor.style_overrides.set_call_override(call_id, param, value)

                        # Also update record kwargs for persistence
                        if value is None or value == "" or value == "null":
                            call.kwargs.pop(param, None)
                        else:
                            call.kwargs[param] = value

                        updated = True
                        break
                if updated:
                    break

        if not updated:
            return jsonify({"error": f"Call {call_id} not found"}), 404

        # Auto-save recipe if we have a recipe path
        if editor.recipe_path and hasattr(editor.fig, "save_recipe"):
            try:
                editor.fig.save_recipe(editor.recipe_path)
            except Exception as save_err:
                print(f"[Auto-save] Warning: Could not save recipe: {save_err}")

        try:
            # IDENTICAL to all other routes - single source of truth
            base64_img, bboxes, img_size = render_with_overrides(
                editor.fig,
                editor.get_effective_style(),
                editor.dark_mode,
            )

            # Regenerate hitmap
            hitmap_img, color_map = generate_hitmap(editor.fig, dpi=150)
            editor._color_map = color_map
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Re-render failed: {str(e)}"}), 500

        # Get updated call data to sync frontend
        updated_call_data = None
        if hasattr(editor.fig, "record"):
            for ax_key, ax_record in editor.fig.record.axes.items():
                for call in ax_record.calls:
                    if call.id == call_id:
                        updated_call_data = {
                            "kwargs": to_json_serializable(call.kwargs),
                        }
                        break
                if updated_call_data:
                    break

        return jsonify(
            {
                "success": True,
                "image": base64_img,
                "bboxes": bboxes,
                "img_size": {"width": img_size[0], "height": img_size[1]},
                "call_id": call_id,
                "param": param,
                "value": value,
                "has_call_overrides": editor.style_overrides.has_call_overrides(),
                "updated_call": updated_call_data,
            }
        )

    @app.route("/download/csv")
    def download_csv():
        """Download plotted data as CSV."""
        import csv
        import io

        # Get the recorder from the figure
        fig = editor.fig
        if not hasattr(fig, "_recorder") or fig._recorder is None:
            return jsonify({"error": "No recorded data available"}), 400

        record = fig._recorder._figure_record

        # Collect all plot data
        all_data = {}
        decoration_funcs = {
            "set_xlabel",
            "set_ylabel",
            "set_title",
            "set_xlim",
            "set_ylim",
            "legend",
            "grid",
            "axhline",
            "axvline",
            "text",
            "annotate",
        }

        for ax_key, ax_record in record.axes.items():
            for call in ax_record.calls:
                if call.function in decoration_funcs:
                    continue

                call_id = call.id or f"{ax_key}_{call.function}_{id(call)}"
                call_data = {}

                def extract_data(val):
                    """Extract raw data from value, handling dict wrappers."""
                    if isinstance(val, dict) and "data" in val:
                        return val["data"]
                    if isinstance(val, list):
                        return val
                    return None

                # Convert args to serializable format
                args = to_json_serializable(call.args)

                # Extract x, y data from args
                if args:
                    if len(args) >= 2:
                        x_data = extract_data(args[0])
                        y_data = extract_data(args[1])
                        if x_data:
                            call_data["x"] = x_data
                        if y_data:
                            call_data["y"] = y_data
                    elif len(args) == 1:
                        data = extract_data(args[0])
                        if data:
                            call_data["y"] = data
                            call_data["x"] = list(range(len(call_data["y"])))

                # Extract from kwargs
                kwargs = to_json_serializable(call.kwargs)
                for key in ["x", "y", "height", "width", "c", "s"]:
                    if key in kwargs:
                        val = extract_data(kwargs[key])
                        if val:
                            call_data[key] = val

                if call_data:
                    all_data[call_id] = call_data

        if not all_data:
            return jsonify({"error": "No plot data found"}), 400

        # Create CSV content
        output = io.StringIO()

        # Find max length for padding
        max_len = max(max(len(v) for v in data.values()) for data in all_data.values())

        # Write header
        headers = []
        for call_id, data in all_data.items():
            for key in sorted(data.keys()):
                headers.append(f"{call_id}_{key}")

        writer = csv.writer(output)
        writer.writerow(headers)

        # Write data rows
        for i in range(max_len):
            row = []
            for call_id, data in all_data.items():
                for key in sorted(data.keys()):
                    values = data[key]
                    if i < len(values):
                        row.append(values[i])
                    else:
                        row.append("")
            writer.writerow(row)

        # Return CSV file
        csv_content = output.getvalue().encode("utf-8")
        filename = "figure_data.csv"
        if editor.recipe_path:
            filename = f"{editor.recipe_path.stem}_data.csv"

        return send_file(
            io.BytesIO(csv_content),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename,
        )

    @app.route("/download/<fmt>")
    def download(fmt: str):
        """Download figure in specified format."""
        import io

        fmt = fmt.lower()
        if fmt not in ("png", "svg", "pdf"):
            return jsonify({"error": f"Unsupported format: {fmt}"}), 400

        effective_style = editor.get_effective_style()
        content = render_download(
            editor.fig,
            fmt=fmt,
            dpi=300,
            overrides=effective_style if effective_style else None,
            dark_mode=False,
        )

        mimetype = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
        }[fmt]

        filename = f"figure.{fmt}"
        if editor.recipe_path:
            filename = f"{editor.recipe_path.stem}.{fmt}"

        return send_file(
            io.BytesIO(content),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename,
        )

    @app.route("/shutdown", methods=["POST"])
    def shutdown():
        """Shutdown the server."""
        func = request.environ.get("werkzeug.server.shutdown")
        if func:
            func()
        return jsonify({"success": True})


__all__ = ["register_element_routes"]
