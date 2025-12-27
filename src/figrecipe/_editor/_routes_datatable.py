#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Datatable-related Flask route handlers for the figure editor.
Handles data extraction from figures and plotting from spreadsheet data.
"""

from flask import jsonify, request

from ._helpers import render_with_overrides, to_json_serializable


def register_datatable_routes(app, editor):
    """Register datatable-related routes with the Flask app."""
    from ._hitmap import generate_hitmap, hitmap_to_base64

    @app.route("/datatable/data")
    def get_datatable_data():
        """Extract plottable data from the current figure's recorded calls.

        Returns column-oriented data suitable for spreadsheet display.
        """
        fig = editor.fig
        if not hasattr(fig, "_recorder") or fig._recorder is None:
            return jsonify({"columns": [], "rows": []})

        record = fig._recorder._figure_record

        # Collect all plot data
        columns = []
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

                def extract_data(val):
                    """Extract raw data from value, handling dict wrappers."""
                    if isinstance(val, dict) and "data" in val:
                        return val["data"]
                    if isinstance(val, (list, tuple)):
                        return list(val)
                    return None

                # Convert args to serializable format
                args = to_json_serializable(call.args)
                kwargs = to_json_serializable(call.kwargs)

                # Extract x, y data from args
                if args:
                    if len(args) >= 2:
                        x_data = extract_data(args[0])
                        y_data = extract_data(args[1])
                        if x_data is not None:
                            col_name = f"{call_id}_x"
                            all_data[col_name] = x_data
                            columns.append(
                                {
                                    "name": col_name,
                                    "type": "numeric"
                                    if all(
                                        isinstance(v, (int, float))
                                        for v in x_data
                                        if v is not None
                                    )
                                    else "string",
                                    "index": len(columns),
                                }
                            )
                        if y_data is not None:
                            col_name = f"{call_id}_y"
                            all_data[col_name] = y_data
                            columns.append(
                                {
                                    "name": col_name,
                                    "type": "numeric"
                                    if all(
                                        isinstance(v, (int, float))
                                        for v in y_data
                                        if v is not None
                                    )
                                    else "string",
                                    "index": len(columns),
                                }
                            )
                    elif len(args) == 1:
                        y_data = extract_data(args[0])
                        if y_data is not None:
                            col_name = f"{call_id}_y"
                            all_data[col_name] = y_data
                            columns.append(
                                {
                                    "name": col_name,
                                    "type": "numeric"
                                    if all(
                                        isinstance(v, (int, float))
                                        for v in y_data
                                        if v is not None
                                    )
                                    else "string",
                                    "index": len(columns),
                                }
                            )

                # Extract from kwargs
                for key in ["x", "y", "height", "width", "c", "s"]:
                    if key in kwargs:
                        val = extract_data(kwargs[key])
                        if val is not None:
                            col_name = f"{call_id}_{key}"
                            if col_name not in all_data:
                                all_data[col_name] = val
                                columns.append(
                                    {
                                        "name": col_name,
                                        "type": "numeric"
                                        if all(
                                            isinstance(v, (int, float))
                                            for v in val
                                            if v is not None
                                        )
                                        else "string",
                                        "index": len(columns),
                                    }
                                )

        if not all_data:
            return jsonify({"columns": [], "rows": []})

        # Convert to row-oriented format
        max_len = max(len(v) for v in all_data.values()) if all_data else 0
        rows = []
        col_names = [c["name"] for c in columns]
        for i in range(max_len):
            row = []
            for name in col_names:
                data = all_data.get(name, [])
                if i < len(data):
                    row.append(data[i])
                else:
                    row.append(None)
            rows.append(row)

        return jsonify({"columns": columns, "rows": rows})

    @app.route("/datatable/plot", methods=["POST"])
    def plot_from_datatable():
        """Create a plot from datatable column selections.

        Expected request body:
        {
            "data": {"col1": [1,2,3], "col2": [4,5,6]},
            "columns": ["col1", "col2"],
            "plot_type": "line",  # or "scatter", "bar", "histogram"
            "target_axis": null  # null=new figure, 0+=existing axis index
        }
        """

        data = request.get_json() or {}
        plot_data = data.get("data", {})
        columns = data.get("columns", [])
        plot_type = data.get("plot_type", "line")
        target_axis = data.get("target_axis")  # None = new figure

        if not plot_data or not columns:
            return jsonify({"error": "No data or columns provided"}), 400

        try:
            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            axes = mpl_fig.get_axes()

            # Determine target axis
            if target_axis is not None and target_axis < len(axes):
                # Plot to existing panel
                ax = axes[target_axis]
            else:
                # Add new panel to existing figure
                n_axes = len(axes)
                if n_axes == 0:
                    ax = mpl_fig.add_subplot(111)
                else:
                    # Expand figure width to accommodate new panel
                    current_width, current_height = mpl_fig.get_size_inches()
                    # Each panel gets ~60mm width, add space for new panel
                    panel_width_inches = 60 / 25.4  # 60mm in inches
                    new_width = current_width + panel_width_inches
                    mpl_fig.set_size_inches(new_width, current_height)

                    # Recalculate positions for all axes
                    n_cols = n_axes + 1
                    margin = 0.08
                    spacing = 0.05
                    panel_w = (1 - 2 * margin - (n_cols - 1) * spacing) / n_cols

                    for i, old_ax in enumerate(axes):
                        left = margin + i * (panel_w + spacing)
                        old_ax.set_position([left, 0.15, panel_w, 0.75])

                    # Add new panel
                    left = margin + n_axes * (panel_w + spacing)
                    ax = mpl_fig.add_axes([left, 0.15, panel_w, 0.75])

            # Dispatch plot using helper
            from ._datatable_plot_handlers import dispatch_plot

            try:
                dispatch_plot(ax, plot_type, plot_data, columns)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

            # Apply current style and render existing figure
            effective_style = editor.get_effective_style()
            recording_fig = editor.fig

            # Update initial axes positions after adding new panel
            editor._initial_axes_positions = editor._capture_axes_positions()

            # Render
            base64_img, bboxes, img_size = render_with_overrides(
                recording_fig,
                effective_style,
                editor.dark_mode,
            )

            # Generate hitmap
            hitmap_img, color_map = generate_hitmap(recording_fig, dpi=150)
            editor._color_map = color_map
            editor._hitmap_base64 = hitmap_to_base64(hitmap_img)
            editor._hitmap_generated = True

            return jsonify(
                {
                    "success": True,
                    "image": base64_img,
                    "bboxes": bboxes,
                    "img_size": {"width": img_size[0], "height": img_size[1]},
                }
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    @app.route("/datatable/import", methods=["POST"])
    def import_datatable():
        """Import data from uploaded file content.

        Expected request body:
        {
            "content": "csv or json content as string",
            "format": "csv" | "json" | "tsv"
        }
        """
        import csv
        import io
        import json

        data = request.get_json() or {}
        content = data.get("content", "")
        fmt = data.get("format", "csv").lower()

        try:
            if fmt == "json":
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    # Array of objects
                    if not parsed:
                        return jsonify({"columns": [], "rows": []})
                    headers = list(parsed[0].keys())
                    rows = [[obj.get(h) for h in headers] for obj in parsed]
                elif isinstance(parsed, dict):
                    # Object with column arrays
                    headers = list(parsed.keys())
                    max_len = max(
                        len(v) if isinstance(v, list) else 1 for v in parsed.values()
                    )
                    rows = []
                    for i in range(max_len):
                        row = []
                        for h in headers:
                            v = parsed[h]
                            if isinstance(v, list):
                                row.append(v[i] if i < len(v) else None)
                            else:
                                row.append(v if i == 0 else None)
                        rows.append(row)
                else:
                    return jsonify({"error": "Invalid JSON structure"}), 400
            else:
                # CSV or TSV
                delimiter = "\t" if fmt == "tsv" else ","
                reader = csv.reader(io.StringIO(content), delimiter=delimiter)
                lines = list(reader)
                if not lines:
                    return jsonify({"columns": [], "rows": []})
                headers = lines[0]
                rows = []
                for line in lines[1:]:
                    row = []
                    for i, val in enumerate(line):
                        try:
                            row.append(float(val))
                        except ValueError:
                            row.append(val)
                    rows.append(row)

            # Determine column types
            columns = []
            for i, name in enumerate(headers):
                values = [row[i] for row in rows if i < len(row) and row[i] is not None]
                is_numeric = all(isinstance(v, (int, float)) for v in values)
                columns.append(
                    {
                        "name": name,
                        "type": "numeric" if is_numeric else "string",
                        "index": i,
                    }
                )

            return jsonify({"columns": columns, "rows": rows})

        except Exception as e:
            return jsonify({"error": str(e)}), 400


__all__ = ["register_datatable_routes"]
