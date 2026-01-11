#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Save function helpers for the public API."""

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

# Image extensions supported for saving
IMAGE_EXTENSIONS = {
    ".png",
    ".pdf",
    ".svg",
    ".jpg",
    ".jpeg",
    ".eps",
    ".tiff",
    ".tif",
}
YAML_EXTENSIONS = {".yaml", ".yml"}
BUNDLE_RECIPE_NAME = "recipe.yaml"


def resolve_save_paths(
    path: Path,
    image_format: Optional[str] = None,
) -> Tuple[Path, Path, str]:
    """Resolve image and YAML paths from the provided path.

    Parameters
    ----------
    path : Path
        User-provided output path.
    image_format : str, optional
        Explicit image format when path is YAML.

    Returns
    -------
    tuple
        (image_path, yaml_path, img_format)
    """
    suffix_lower = path.suffix.lower()

    if suffix_lower in IMAGE_EXTENSIONS:
        # User provided image path
        image_path = path
        yaml_path = path.with_suffix(".yaml")
        img_format = suffix_lower[1:]  # Remove leading dot
    elif suffix_lower in YAML_EXTENSIONS:
        # User provided YAML path
        yaml_path = path
        img_format = _get_default_image_format(image_format)
        image_path = path.with_suffix(f".{img_format}")
    else:
        # Unknown extension - treat as base name, add both extensions
        yaml_path = path.with_suffix(".yaml")
        img_format = _get_default_image_format(image_format)
        image_path = path.with_suffix(f".{img_format}")

    return image_path, yaml_path, img_format


def _get_default_image_format(explicit_format: Optional[str] = None) -> str:
    """Get default image format from style or fallback to png."""
    if explicit_format is not None:
        return explicit_format.lower().lstrip(".")

    # Check global style for preferred format
    from ..styles._style_loader import _STYLE_CACHE

    if _STYLE_CACHE is not None:
        try:
            return _STYLE_CACHE.output.format.lower()
        except (KeyError, AttributeError):
            pass
    return "png"


def get_save_dpi(explicit_dpi: Optional[int] = None) -> int:
    """Get DPI for saving, using style default if not specified."""
    if explicit_dpi is not None:
        return explicit_dpi

    from ..styles._style_loader import _STYLE_CACHE

    if _STYLE_CACHE is not None:
        try:
            return _STYLE_CACHE.output.dpi
        except (KeyError, AttributeError):
            pass
    return 300


def _capture_axes_bboxes(fig, crop_offset: Optional[dict] = None) -> None:
    """Capture bounding boxes of all axes for alignment/snap functionality.

    Stores bbox as [left, bottom, width, height] in figure coordinates (0-1).
    If crop_offset is provided, adjusts bbox to post-crop coordinate system.

    Parameters
    ----------
    fig : RecordingFigure
        The figure with record to update.
    crop_offset : dict, optional
        Crop information from crop() with return_offset=True.
        Contains: left, upper, right, lower, original_width, original_height,
        new_width, new_height (all in pixels).
    """
    for ax in fig.fig.get_axes():
        # Get axes position in figure coordinates (0-1 range)
        bbox = ax.get_position()
        bbox_list = [bbox.x0, bbox.y0, bbox.width, bbox.height]

        # Adjust for crop offset if provided
        if crop_offset is not None:
            # Convert from figure coords to pixel coords, then to cropped coords
            orig_w = crop_offset["original_width"]
            orig_h = crop_offset["original_height"]
            new_w = crop_offset["new_width"]
            new_h = crop_offset["new_height"]
            crop_left = crop_offset["left"]
            crop_upper = crop_offset["upper"]

            # Original pixel positions (matplotlib y=0 is bottom, image y=0 is top)
            x0_px = bbox.x0 * orig_w
            y0_px = (1 - bbox.y0 - bbox.height) * orig_h  # Convert to image coords
            w_px = bbox.width * orig_w
            h_px = bbox.height * orig_h

            # Adjust for crop (translate origin)
            x0_cropped = x0_px - crop_left
            y0_cropped = y0_px - crop_upper

            # Convert back to figure coordinates (0-1 range in cropped image)
            new_x0 = x0_cropped / new_w
            new_y0 = 1 - (y0_cropped + h_px) / new_h  # Back to matplotlib coords
            new_w_frac = w_px / new_w
            new_h_frac = h_px / new_h

            bbox_list = [new_x0, new_y0, new_w_frac, new_h_frac]

        # Find corresponding AxesRecord
        # Try to match by checking if this ax corresponds to a known position
        for key, ax_record in fig.record.axes.items():
            # Parse key like "ax_0_0" to get row, col
            parts = key.split("_")
            if len(parts) >= 3:
                row, col = int(parts[1]), int(parts[2])
                # Check if positions match (comparing grid indices)
                if ax_record.position == (row, col):
                    ax_record.bbox = bbox_list
                    break


def get_save_transparency() -> bool:
    """Get transparency setting from style."""
    from ..styles._style_loader import _STYLE_CACHE

    if _STYLE_CACHE is not None:
        try:
            return _STYLE_CACHE.output.transparent
        except (KeyError, AttributeError):
            pass
    return False


def _resolve_background_color(background):
    """Resolve background color to matplotlib-compatible format.

    Parameters
    ----------
    background : str, tuple, or None
        Background specification:
        - "transparent" or "none": returns None (transparent)
        - RGB tuple like (255, 255, 255) or (1.0, 1.0, 1.0)
        - RGBA tuple like (255, 255, 255, 255)
        - Color name like "white" (resolved from style if available)
        - Hex color like "#ffffff"

    Returns
    -------
    tuple or None
        Matplotlib-compatible color tuple (0-1 range), or None for transparent.
    """
    if background is None:
        return None

    # Check for transparent
    if isinstance(background, str):
        if background.lower() in ("transparent", "none"):
            return None

    # If tuple, normalize to 0-1 range
    if isinstance(background, (tuple, list)):
        bg = list(background)
        # Check if values are in 0-255 range (RGB/RGBA integers)
        if any(v > 1 for v in bg[:3]):
            bg = [v / 255.0 for v in bg]
        # Ensure alpha=1.0 if not specified
        if len(bg) == 3:
            bg.append(1.0)
        return tuple(bg)

    # If string color name, try to resolve from style first
    if isinstance(background, str):
        from ..styles._style_loader import _STYLE_CACHE

        if _STYLE_CACHE is not None:
            try:
                # Look up in style's colors.rgb
                colors_rgb = getattr(_STYLE_CACHE, "colors", None)
                if colors_rgb:
                    rgb_list = getattr(colors_rgb, "rgb", None)
                    if rgb_list:
                        for item in rgb_list:
                            if isinstance(item, dict) and background.lower() in item:
                                rgb = item[background.lower()]
                                if isinstance(rgb, (list, tuple)):
                                    # Normalize to 0-1 range
                                    if any(v > 1 for v in rgb[:3]):
                                        rgb = [v / 255.0 for v in rgb]
                                    if len(rgb) == 3:
                                        rgb = list(rgb) + [1.0]
                                    return tuple(rgb)
            except (AttributeError, TypeError):
                pass

        # Fall back to matplotlib color parsing
        import matplotlib.colors as mcolors

        try:
            rgba = mcolors.to_rgba(background)
            return rgba
        except ValueError:
            pass

    # Default: return as-is (let matplotlib handle it)
    return background


def _is_bundle_path(path: Path) -> bool:
    """Check if path represents a bundle (directory or ZIP)."""
    suffix = path.suffix.lower()
    # ZIP file
    if suffix == ".zip":
        return True
    # Existing directory
    if path.is_dir():
        return True
    # Path ending with / (explicit directory)
    if str(path).endswith("/"):
        return True
    # No extension and doesn't look like a file
    if not suffix and not path.exists():
        return True
    return False


def _save_as_bundle(
    fig,
    path: Path,
    include_data: bool,
    data_format: str,
    csv_format: str,
    dpi: int,
    background,
    image_format: str,
    verbose: bool,
) -> Tuple[Path, Path]:
    """Save figure as a bundle (directory or ZIP).

    Parameters
    ----------
    background : tuple or None
        Resolved background color as RGB/RGBA tuple, or None for transparent.
    """
    suffix = path.suffix.lower()
    is_zip = suffix == ".zip"

    # Create temporary directory for bundle contents
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Determine image format
        img_format = image_format or _get_default_image_format()
        image_name = f"figure.{img_format}"

        # Save image (no bbox_inches to preserve mm layout)
        image_path = tmpdir / image_name
        if background is None:  # transparent
            fig.fig.savefig(image_path, dpi=dpi, transparent=True)
        else:
            fig.fig.set_facecolor(background)
            fig.fig.savefig(image_path, dpi=dpi, facecolor=background)

        # Save recipe
        yaml_path = tmpdir / BUNDLE_RECIPE_NAME
        fig.save_recipe(
            yaml_path,
            include_data=include_data,
            data_format=data_format,
            csv_format=csv_format,
        )

        if is_zip:
            # Create ZIP bundle
            zip_path = path.with_suffix(".zip")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(yaml_path, BUNDLE_RECIPE_NAME)
                zf.write(image_path, image_name)
            if verbose:
                print(f"Saved: {zip_path} (ZIP bundle)")
            return zip_path, zip_path
        else:
            # Create directory bundle
            bundle_dir = Path(str(path).rstrip("/"))
            bundle_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(yaml_path, bundle_dir / BUNDLE_RECIPE_NAME)
            shutil.copy2(image_path, bundle_dir / image_name)
            if verbose:
                print(f"Saved: {bundle_dir}/ (directory bundle)")
            return bundle_dir, bundle_dir / BUNDLE_RECIPE_NAME


def save_figure(
    fig,
    path,
    include_data: bool = True,
    data_format: str = "csv",
    csv_format: str = "separate",
    validate: bool = True,
    validate_mse_threshold: float = 100.0,
    validate_error_level: str = "error",
    verbose: bool = True,
    dpi: Optional[int] = None,
    image_format: Optional[str] = None,
    crop_margin_mm: Optional[float] = None,
    background: Optional[str] = None,
):
    """Core save implementation.

    Supports multiple output formats:
    - Image file (.png, .pdf, etc.): Saves image + .yaml recipe
    - YAML file (.yaml): Saves recipe + image
    - Directory (path/ or no extension): Saves as bundle directory
    - ZIP file (.zip): Saves as ZIP bundle

    Parameters
    ----------
    csv_format : str
        CSV file structure: 'separate' (default) or 'single'.
        - 'separate': One CSV file per variable
        - 'single': Single CSV with all columns (scitex/SigmaPlot-compatible)
    crop_margin_mm : float, optional
        If specified, auto-crop saved image to all ink/content plus this margin.
        Crops to visible content (axes, labels, titles) + margin on all sides.
    """
    from .._wrappers import RecordingFigure

    path = Path(path)

    if not isinstance(fig, RecordingFigure):
        raise TypeError(
            "Expected RecordingFigure. Use fr.subplots() to create "
            "a recording-enabled figure."
        )

    # Get DPI from style if not specified
    dpi = get_save_dpi(dpi)

    # Resolve background: explicit param > fig.set_background() > style default
    if background is None:
        if hasattr(fig, "_explicit_background") and fig._explicit_background:
            background = fig._explicit_background
        elif get_save_transparency():
            background = "transparent"
        else:
            background = "white"

    # Apply style and finalize tick configuration for all axes
    # Get style for finalization (use globally loaded style, flattened)
    from ..styles._kwargs_converter import to_subplots_kwargs
    from ..styles._style_applier import (
        apply_style_mm,
        finalize_special_plots,
        finalize_ticks,
    )

    style_dict = to_subplots_kwargs()

    for ax in fig.fig.get_axes():
        apply_style_mm(ax, style_dict)
        finalize_ticks(ax)
        finalize_special_plots(ax, style_dict)

    # Resolve background color (supports name, RGB tuple, RGBA tuple, hex)
    resolved_bg = _resolve_background_color(background)

    # Check if saving as bundle
    if _is_bundle_path(path):
        bundle_path, yaml_path = _save_as_bundle(
            fig,
            path,
            include_data,
            data_format,
            csv_format,
            dpi,
            resolved_bg,
            image_format or _get_default_image_format(),
            verbose,
        )
        # No validation for bundles (yet)
        return bundle_path, yaml_path, None

    # Resolve paths for standard save
    image_path, yaml_path, _ = resolve_save_paths(path, image_format)

    # Save the image (no bbox_inches to preserve mm layout)
    if resolved_bg is None:  # transparent
        fig.fig.savefig(image_path, dpi=dpi, transparent=True)
    else:
        # Set background color with alpha=1.0 for opaque output
        fig.fig.set_facecolor(resolved_bg)
        fig.fig.patch.set_alpha(1.0)
        for ax in fig.fig.get_axes():
            ax.set_facecolor(resolved_bg)
            ax.patch.set_alpha(1.0)
        fig.fig.savefig(image_path, dpi=dpi, facecolor=resolved_bg)

    # Auto-crop using stored crop margins from mm_layout (or explicit parameter)
    # Only crop raster image formats (not PDF, SVG, EPS)
    croppable_formats = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
    is_croppable = image_path.suffix.lower() in croppable_formats

    crop_offset = None
    if is_croppable:
        if crop_margin_mm is not None:
            # Explicit uniform crop margin
            from .._utils._crop import crop

            _, crop_offset = crop(
                image_path,
                margin_mm=crop_margin_mm,
                output_path=image_path,
                return_offset=True,
            )
        elif hasattr(fig, "_mm_layout") and fig._mm_layout is not None:
            # Use per-side crop margins from mm_layout
            mm_layout = fig._mm_layout
            if "crop_margin_left_mm" in mm_layout:
                from .._utils._crop import crop

                _, crop_offset = crop(
                    image_path,
                    margin_left_mm=mm_layout.get("crop_margin_left_mm", 1),
                    margin_right_mm=mm_layout.get("crop_margin_right_mm", 1),
                    margin_top_mm=mm_layout.get("crop_margin_top_mm", 1),
                    margin_bottom_mm=mm_layout.get("crop_margin_bottom_mm", 1),
                    output_path=image_path,
                    return_offset=True,
                )

    # Capture axes bounding boxes (adjusted for crop if cropping occurred)
    _capture_axes_bboxes(fig, crop_offset)

    # Store crop info in record for future reference
    if crop_offset is not None:
        fig.record.crop_info = crop_offset

    # Save the recipe
    saved_yaml = fig.save_recipe(
        yaml_path,
        include_data=include_data,
        data_format=data_format,
        csv_format=csv_format,
    )

    # Validate if requested
    if validate:
        from .._validator import validate_on_save

        result = validate_on_save(fig, saved_yaml, mse_threshold=validate_mse_threshold)
        status = "PASSED" if result.valid else "FAILED"
        if verbose:
            print(
                f"Saved: {image_path} + {yaml_path} (Reproducible Validation: {status})"
            )
        if not result.valid:
            msg = f"Reproducibility validation failed (MSE={result.mse:.1f}): {result.message}"
            if validate_error_level == "error":
                raise ValueError(msg)
            elif validate_error_level == "warning":
                import warnings

                warnings.warn(msg, UserWarning)
            # "debug" level: silent, just return the result
        return image_path, yaml_path, result

    if verbose:
        print(f"Saved: {image_path} + {yaml_path}")
    return image_path, yaml_path, None


__all__ = [
    "IMAGE_EXTENSIONS",
    "YAML_EXTENSIONS",
    "resolve_save_paths",
    "get_save_dpi",
    "get_save_transparency",
    "save_figure",
]

# EOF
