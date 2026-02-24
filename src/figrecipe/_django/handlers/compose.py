#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compose handlers: compose canvas figures into a single output.

Uses PIL image composition to paste rendered preview images at their
exact canvas positions. This guarantees pixel-perfect output matching
the canvas layout, including theme, dark mode, and all decorations.
"""

import base64
import io
import json
import logging
from pathlib import Path

from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


def _parse_figures(request):
    """Parse placed figures from request body.

    Returns (figures, dark_mode, working_dir).
    Each figure: {path, x, y, width, height, image (base64)}.
    """
    data = json.loads(request.body) if request.body else {}
    figures = data.get("figures", [])
    dark_mode = data.get("dark_mode", False)
    working_dir = data.get("working_dir", "")

    if not figures:
        raise ValueError("No figures on canvas")

    for fig in figures:
        logger.info(
            "[Compose] Figure '%s': x=%d, y=%d, w=%d, h=%d, has_image=%s",
            fig.get("path", "?"),
            fig.get("x", 0),
            fig.get("y", 0),
            fig.get("width", 0),
            fig.get("height", 0),
            bool(fig.get("image")),
        )

    return figures, dark_mode, working_dir


def _compose_pil(figures, dark_mode):
    """Compose figures into a single PIL Image by pasting at canvas positions.

    Each figure has {x, y, width, height, image} where image is base64 PNG.
    """
    from PIL import Image

    # Compute canvas bounds from figure positions + sizes
    max_x = 0
    max_y = 0
    for fig in figures:
        right = int(fig["x"]) + int(fig["width"])
        bottom = int(fig["y"]) + int(fig["height"])
        max_x = max(max_x, right)
        max_y = max(max_y, bottom)

    canvas_w = max_x + 4  # small margin
    canvas_h = max_y + 4

    logger.info("[Compose] Canvas: %d x %d px", canvas_w, canvas_h)

    # Create canvas with appropriate background
    bg = (30, 30, 30, 255) if dark_mode else (255, 255, 255, 255)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg)

    # Paste each figure at its position
    for fig in figures:
        img_b64 = fig.get("image", "")
        if not img_b64:
            logger.warning(
                "[Compose] Figure '%s' has no image data, skipping", fig.get("path")
            )
            continue

        img_data = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_data)).convert("RGBA")

        # Resize to match the exact canvas dimensions
        target_w = int(fig["width"])
        target_h = int(fig["height"])
        if img.size != (target_w, target_h):
            img = img.resize((target_w, target_h), Image.LANCZOS)

        x = int(fig["x"])
        y = int(fig["y"])
        canvas.paste(img, (x, y), img)  # use alpha mask

        # Draw panel letter (A, B, C...) at top-left of figure
        panel_letter = fig.get("panel_letter")
        if panel_letter:
            from PIL import ImageDraw, ImageFont

            draw = ImageDraw.Draw(canvas)
            font_size = 18
            try:
                font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

            # Measure text for badge background
            bbox = draw.textbbox((0, 0), panel_letter, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            pad_x, pad_y = 6, 3
            bx = x + 8
            by = y + 6

            # Semi-transparent dark badge
            badge = Image.new("RGBA", (tw + pad_x * 2, th + pad_y * 2), (0, 0, 0, 165))
            canvas.paste(badge, (bx, by), badge)

            # White bold letter
            draw.text(
                (bx + pad_x - bbox[0], by + pad_y - bbox[1]),
                panel_letter,
                fill=(255, 255, 255, 255),
                font=font,
            )

    return canvas


def handle_compose_save(request, editor):
    """Compose canvas figures and save as PNG."""
    figures, dark_mode, working_dir = _parse_figures(request)
    canvas = _compose_pil(figures, dark_mode)

    # Determine output path
    data = json.loads(request.body) if request.body else {}
    filename = data.get("filename", "composed")

    if working_dir:
        out_dir = Path(working_dir)
    elif editor and editor.recipe_path:
        out_dir = editor.recipe_path.parent
    else:
        out_dir = Path(".")

    out_path = out_dir / f"{filename}.png"

    # Save as PNG
    canvas_rgb = canvas.convert("RGB")
    canvas_rgb.save(str(out_path), "PNG", dpi=(300, 300))
    logger.info("[Compose] Saved to %s (%dx%d)", out_path, canvas.width, canvas.height)

    return JsonResponse(
        {
            "success": True,
            "path": str(out_path),
        }
    )


def handle_compose_export(request, editor, fmt):
    """Compose canvas figures and return as downloadable blob."""
    fmt = fmt.lower()
    if fmt not in ("png", "svg", "pdf"):
        return JsonResponse({"error": f"Unsupported format: {fmt}"}, status=400)

    figures, dark_mode, working_dir = _parse_figures(request)
    canvas = _compose_pil(figures, dark_mode)

    data = json.loads(request.body) if request.body else {}
    filename = data.get("filename", "composed")

    buf = io.BytesIO()
    if fmt == "png":
        canvas.convert("RGB").save(buf, "PNG", dpi=(300, 300))
        mimetype = "image/png"
    elif fmt == "pdf":
        canvas.convert("RGB").save(buf, "PDF", resolution=300)
        mimetype = "application/pdf"
    elif fmt == "svg":
        # SVG from raster: embed as base64 image in SVG wrapper
        png_buf = io.BytesIO()
        canvas.convert("RGB").save(png_buf, "PNG", dpi=(300, 300))
        png_b64 = base64.b64encode(png_buf.getvalue()).decode()
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{canvas.width}" height="{canvas.height}">'
            f'<image href="data:image/png;base64,{png_b64}" '
            f'width="{canvas.width}" height="{canvas.height}"/>'
            f"</svg>"
        )
        buf.write(svg.encode())
        mimetype = "image/svg+xml"
    buf.seek(0)

    response = HttpResponse(buf.read(), content_type=mimetype)
    response["Content-Disposition"] = f'attachment; filename="{filename}.{fmt}"'
    return response
