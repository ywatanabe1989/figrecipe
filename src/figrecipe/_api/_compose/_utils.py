#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared utilities for figure composition."""

import os
import string
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


def mm_to_px(mm: float, dpi: int) -> int:
    """Convert millimeters to pixels."""
    return int(mm * dpi / 25.4)


def load_images(
    sources: List[str], dpi: int, facecolor: str = "white"
) -> List[Image.Image]:
    """Load images from source paths (images or recipe files).

    Parameters
    ----------
    sources : list of str
        Paths to image files or YAML recipe files.
    dpi : int
        DPI for rendering recipes.
    facecolor : str
        Background color for rendered recipes and loaded images.
        Default is 'white' for consistent composition.

    Returns
    -------
    list of Image
        Loaded images with consistent background.
    """
    import matplotlib.pyplot as plt

    images = []
    for source in sources:
        source_path = Path(source)
        if source_path.suffix.lower() == ".yaml":
            # Reproduce recipe to temp image with explicit facecolor
            import figrecipe as fr

            fig, _ = fr.reproduce(source_path)
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                # Always use explicit facecolor for consistent composition
                mpl_fig = fig.fig if hasattr(fig, "fig") else fig
                mpl_fig.savefig(tmp.name, dpi=dpi, facecolor=facecolor)
                img = Image.open(tmp.name).copy()
                # Ensure image has white background (flatten alpha)
                img = flatten_alpha(img, facecolor)
                images.append(img)
            os.unlink(tmp.name)
            # Close the underlying matplotlib figure
            plt.close(mpl_fig)
        else:
            img = Image.open(source_path)
            # Ensure loaded images also have consistent background
            img = flatten_alpha(img, facecolor)
            images.append(img)
    return images


def flatten_alpha(img: Image.Image, background_color: str = "white") -> Image.Image:
    """Flatten alpha channel by compositing onto a solid background.

    Parameters
    ----------
    img : Image
        Input image (may have alpha channel).
    background_color : str
        Background color to use. Default is 'white'.

    Returns
    -------
    Image
        RGBA image with alpha set to fully opaque (composited onto background).
    """
    if img.mode != "RGBA":
        return img.convert("RGBA")

    # Create background with same size
    if background_color.lower() == "white":
        bg_rgba = (255, 255, 255, 255)
    elif background_color.lower() == "black":
        bg_rgba = (0, 0, 0, 255)
    else:
        # Try to parse color
        try:
            from PIL import ImageColor

            rgb = ImageColor.getrgb(background_color)
            bg_rgba = (*rgb, 255)
        except ValueError:
            bg_rgba = (255, 255, 255, 255)  # Default to white

    background = Image.new("RGBA", img.size, bg_rgba)
    # Composite img onto background using alpha channel
    background.paste(img, (0, 0), mask=img)
    return background


def create_source_symlinks(sources: List[str], output_path: Path) -> Optional[Path]:
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


def add_panel_labels(
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
    font = get_font(fontweight, font_px)

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


def add_caption(
    image: Image.Image, caption: str, fontsize: int, dpi: int
) -> Image.Image:
    """Add caption below the composed image."""
    font_px = int(fontsize * dpi / 72)
    font = get_font("normal", font_px)

    # Create a temporary draw to measure text
    temp_draw = ImageDraw.Draw(image)

    # Wrap text to fit image width with margin
    margin = int(10 * dpi / 72)
    max_width = image.width - 2 * margin
    wrapped_lines = wrap_text(caption, font, max_width, temp_draw)

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


def get_font(weight: str, size_px: int) -> ImageFont.FreeTypeFont:
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


def wrap_text(
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


def resize_to_fit(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Resize image to fit within target dimensions while preserving aspect ratio.

    Parameters
    ----------
    img : Image
        Source image.
    target_w, target_h : int
        Target dimensions in pixels.

    Returns
    -------
    Image
        Resized image.
    """
    # Calculate scale factor to fit within target
    scale_w = target_w / img.width
    scale_h = target_h / img.height
    scale = min(scale_w, scale_h)

    # Calculate new dimensions
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)

    # Resize using high-quality resampling
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
