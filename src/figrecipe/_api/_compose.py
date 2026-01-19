#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure composition utilities for combining multiple figures."""

import math
import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


def compose_figures(
    sources: List[str],
    output_path: str,
    layout: str = "horizontal",
    gap_mm: float = 5.0,
    dpi: int = 300,
    panel_labels: bool = True,
    label_style: str = "uppercase",
    label_fontsize: int = 10,
    label_fontweight: str = "bold",
    caption: Optional[str] = None,
    caption_fontsize: int = 8,
    create_symlinks: bool = True,
) -> Dict[str, Any]:
    """Compose multiple figures into a single figure.

    Parameters
    ----------
    sources : list of str
        Paths to source images or recipe files.
    output_path : str
        Path to save the composed figure.
    layout : str
        Layout mode: 'horizontal', 'vertical', or 'grid'.
    gap_mm : float
        Gap between panels in millimeters.
    dpi : int
        DPI for output.
    panel_labels : bool
        If True, add panel labels (A, B, C, D) to each panel.
    label_style : str
        Label style: 'uppercase' (A, B, C), 'lowercase' (a, b, c), 'numeric' (1, 2, 3).
    label_fontsize : int
        Font size for panel labels.
    label_fontweight : str
        Font weight for panel labels ('bold', 'normal').
    caption : str, optional
        Figure caption to add below the composed figure.
    caption_fontsize : int
        Font size for caption.
    create_symlinks : bool
        If True (default), create symlinks to source files in a subdirectory
        for traceability and single source of truth.

    Returns
    -------
    dict
        Result with 'output_path', 'success', and 'sources_dir' (if symlinks created).
    """
    # Convert gap from mm to pixels
    gap_px = int(gap_mm * dpi / 25.4)

    # Load all images
    images = _load_images(sources, dpi)

    if not images:
        raise ValueError("No valid source images provided")

    output_path = Path(output_path)

    # Compose based on layout
    result, positions = _compose_layout(images, layout, gap_px)

    # Add panel labels if requested
    if panel_labels:
        result = _add_panel_labels(
            result, positions, label_style, label_fontsize, label_fontweight, dpi
        )

    # Add caption if provided
    if caption:
        result = _add_caption(result, caption, caption_fontsize, dpi)

    # Save result
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        result = result.convert("RGB")
    result.save(output_path, dpi=(dpi, dpi))

    result_dict = {
        "output_path": str(output_path),
        "success": True,
    }

    # Create symlinks to source files for traceability
    if create_symlinks:
        sources_dir = _create_source_symlinks(sources, output_path)
        if sources_dir:
            result_dict["sources_dir"] = str(sources_dir)

    return result_dict


def _create_source_symlinks(sources: List[str], output_path: Path) -> Optional[Path]:
    """Create symlinks to source files for traceability.

    Parameters
    ----------
    sources : list of str
        Original source file paths.
    output_path : Path
        Path to the composed output file.

    Returns
    -------
    Path or None
        Path to the sources directory containing symlinks, or None if failed.
    """
    import os

    # Create sources directory named after output file
    sources_dir = output_path.parent / f"{output_path.stem}_sources"
    try:
        sources_dir.mkdir(exist_ok=True)

        for idx, source in enumerate(sources):
            source_path = Path(source).resolve()
            if not source_path.exists():
                continue

            # Create symlink with panel label prefix (A_, B_, C_, ...)
            label = chr(ord("A") + idx)
            link_name = f"{label}_{source_path.name}"
            link_path = sources_dir / link_name

            # Remove existing symlink if present
            if link_path.is_symlink():
                link_path.unlink()

            # Create relative symlink for portability
            try:
                rel_path = os.path.relpath(source_path, sources_dir)
                link_path.symlink_to(rel_path)
            except OSError:
                # Fallback to absolute path if relative fails
                link_path.symlink_to(source_path)

        return sources_dir
    except OSError:
        return None


def _load_images(sources: List[str], dpi: int) -> List[Image.Image]:
    """Load images from source paths (images or recipe files)."""
    images = []
    for source in sources:
        source_path = Path(source)
        if source_path.suffix.lower() == ".yaml":
            # Reproduce recipe to temp image
            import os
            import tempfile

            import matplotlib.pyplot as plt

            import figrecipe as fr

            fig, _ = fr.reproduce(source_path)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                fig.savefig(tmp.name, dpi=dpi)
                images.append(Image.open(tmp.name).copy())
            os.unlink(tmp.name)
            plt.close(fig)
        else:
            images.append(Image.open(source_path))
    return images


def _compose_layout(
    images: List[Image.Image], layout: str, gap_px: int
) -> Tuple[Image.Image, List[Tuple[int, int, int, int]]]:
    """Compose images into layout and return result with positions."""
    positions = []  # List of (x, y, width, height) for each image

    if layout == "horizontal":
        total_width = sum(img.width for img in images) + gap_px * (len(images) - 1)
        max_height = max(img.height for img in images)
        result = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 255))
        x_offset = 0
        for img in images:
            result.paste(img, (x_offset, 0))
            positions.append((x_offset, 0, img.width, img.height))
            x_offset += img.width + gap_px

    elif layout == "vertical":
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images) + gap_px * (len(images) - 1)
        result = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 255))
        y_offset = 0
        for img in images:
            result.paste(img, (0, y_offset))
            positions.append((0, y_offset, img.width, img.height))
            y_offset += img.height + gap_px

    elif layout == "grid":
        ncols = math.ceil(math.sqrt(len(images)))
        nrows = math.ceil(len(images) / ncols)
        max_w = max(img.width for img in images)
        max_h = max(img.height for img in images)
        total_width = ncols * max_w + (ncols - 1) * gap_px
        total_height = nrows * max_h + (nrows - 1) * gap_px
        result = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 255))
        for idx, img in enumerate(images):
            row = idx // ncols
            col = idx % ncols
            x = col * (max_w + gap_px)
            y = row * (max_h + gap_px)
            result.paste(img, (x, y))
            positions.append((x, y, img.width, img.height))
    else:
        raise ValueError(
            f"Unknown layout: {layout}. Use 'horizontal', 'vertical', or 'grid'"
        )

    return result, positions


def _add_panel_labels(
    image: Image.Image,
    positions: List[Tuple[int, int, int, int]],
    label_style: str,
    fontsize: int,
    fontweight: str,
    dpi: int,
) -> Image.Image:
    """Add panel labels (A, B, C, D) to composed image."""
    draw = ImageDraw.Draw(image)

    # Generate labels based on style
    if label_style == "lowercase":
        labels = list(string.ascii_lowercase)
    elif label_style == "numeric":
        labels = [str(i + 1) for i in range(len(positions))]
    else:  # uppercase (default)
        labels = list(string.ascii_uppercase)

    # Calculate font size in pixels (approximate)
    font_px = int(fontsize * dpi / 72)

    # Try to load a bold font
    font = _get_font(fontweight, font_px)

    # Add labels to each panel
    for idx, (x, y, w, h) in enumerate(positions):
        if idx >= len(labels):
            break
        label = labels[idx]

        # Position: upper-left corner with small offset
        offset_px = int(3 * dpi / 72)  # 3pt offset
        text_x = x + offset_px
        text_y = y + offset_px

        # Draw white background for visibility
        bbox = draw.textbbox((text_x, text_y), label, font=font)
        padding = 2
        draw.rectangle(
            [
                bbox[0] - padding,
                bbox[1] - padding,
                bbox[2] + padding,
                bbox[3] + padding,
            ],
            fill=(255, 255, 255, 230),
        )

        # Draw label
        draw.text((text_x, text_y), label, fill=(0, 0, 0), font=font)

    return image


def _add_caption(
    image: Image.Image, caption: str, fontsize: int, dpi: int
) -> Image.Image:
    """Add caption below the composed image."""
    font_px = int(fontsize * dpi / 72)
    font = _get_font("normal", font_px)

    # Create a temporary draw to measure text
    temp_draw = ImageDraw.Draw(image)

    # Wrap text to fit image width with margin
    margin = int(10 * dpi / 72)
    max_width = image.width - 2 * margin
    wrapped_lines = _wrap_text(caption, font, max_width, temp_draw)

    # Calculate caption height
    line_height = font_px + 4
    caption_height = len(wrapped_lines) * line_height + 2 * margin

    # Create new image with space for caption
    new_height = image.height + caption_height
    new_image = Image.new("RGBA", (image.width, new_height), (255, 255, 255, 255))
    new_image.paste(image, (0, 0))

    # Draw caption
    draw = ImageDraw.Draw(new_image)
    y = image.height + margin
    for line in wrapped_lines:
        # Center the text
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (image.width - text_width) // 2
        draw.text((x, y), line, fill=(0, 0, 0), font=font)
        y += line_height

    return new_image


def _get_font(weight: str, size_px: int) -> ImageFont.FreeTypeFont:
    """Get a font with specified weight and size."""
    # Try common system fonts
    font_paths = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]

    # Prefer bold fonts if weight is bold
    if weight == "bold":
        font_paths = [p for p in font_paths if "Bold" in p or "bd" in p] + font_paths

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size_px)
        except (IOError, OSError):
            continue

    # Fallback to default
    return ImageFont.load_default()


def _wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw
) -> List[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines
