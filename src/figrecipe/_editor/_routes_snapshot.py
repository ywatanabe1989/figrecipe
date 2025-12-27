#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Routes for panel snapshot generation (isolated rendering)."""

import base64
import io


def register_snapshot_routes(app, editor):
    """Register snapshot-related routes.

    Parameters
    ----------
    app : Flask
        Flask application instance.
    editor : FigureEditor
        Editor instance with figure state.
    """

    @app.route("/get_panel_snapshot/<int:ax_index>")
    def get_panel_snapshot(ax_index):
        """Render a single panel in isolation and return as base64 PNG.

        This hides all other axes to produce a clean snapshot without
        overlap artifacts from neighboring panels.

        Parameters
        ----------
        ax_index : int
            Index of the axis/panel to render.

        Returns
        -------
        dict
            JSON with success status and base64-encoded PNG image.
        """
        try:
            # Get matplotlib figure from RecordingFigure wrapper
            mpl_fig = editor.fig.fig if hasattr(editor.fig, "fig") else editor.fig
            axes = mpl_fig.get_axes()

            if ax_index < 0 or ax_index >= len(axes):
                return {"success": False, "error": f"Invalid ax_index: {ax_index}"}

            # Store original visibility states
            original_visibility = [ax.get_visible() for ax in axes]

            try:
                # Hide all axes except the target
                for i, ax in enumerate(axes):
                    ax.set_visible(i == ax_index)

                # Render to buffer with transparent background
                buf = io.BytesIO()
                mpl_fig.savefig(
                    buf,
                    format="png",
                    transparent=True,
                    bbox_inches="tight",
                    pad_inches=0.1,
                    facecolor="none",
                    edgecolor="none",
                )
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode("utf-8")

                return {
                    "success": True,
                    "image": image_base64,
                    "ax_index": ax_index,
                }

            finally:
                # Restore original visibility
                for i, ax in enumerate(axes):
                    ax.set_visible(original_visibility[i])

        except Exception as e:
            # Return JSON error instead of 500 to avoid console errors
            return {"success": False, "error": str(e)}


__all__ = ["register_snapshot_routes"]

# EOF
