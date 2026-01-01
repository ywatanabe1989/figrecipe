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


def get_save_transparency() -> bool:
    """Get transparency setting from style."""
    from ..styles._style_loader import _STYLE_CACHE

    if _STYLE_CACHE is not None:
        try:
            return _STYLE_CACHE.output.transparent
        except (KeyError, AttributeError):
            pass
    return False


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
    transparent: bool,
    image_format: str,
    verbose: bool,
) -> Tuple[Path, Path]:
    """Save figure as a bundle (directory or ZIP)."""
    suffix = path.suffix.lower()
    is_zip = suffix == ".zip"

    # Create temporary directory for bundle contents
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Determine image format
        img_format = image_format or _get_default_image_format()
        image_name = f"figure.{img_format}"

        # Save image
        image_path = tmpdir / image_name
        fig.fig.savefig(
            image_path, dpi=dpi, bbox_inches="tight", transparent=transparent
        )

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
    """
    from .._wrappers import RecordingFigure

    path = Path(path)

    if not isinstance(fig, RecordingFigure):
        raise TypeError(
            "Expected RecordingFigure. Use fr.subplots() to create "
            "a recording-enabled figure."
        )

    # Get DPI and transparency from style if not specified
    dpi = get_save_dpi(dpi)
    transparent = get_save_transparency()

    # Finalize tick configuration and special plot types for all axes
    from ..styles._style_applier import finalize_special_plots, finalize_ticks

    # Get style for special plot finalization
    style_dict = {}
    if hasattr(fig, "style") and fig.style:
        from ..styles import get_style

        style_dict = get_style(fig.style)

    for ax in fig.fig.get_axes():
        finalize_ticks(ax)
        finalize_special_plots(ax, style_dict)

    # Check if saving as bundle
    if _is_bundle_path(path):
        bundle_path, yaml_path = _save_as_bundle(
            fig,
            path,
            include_data,
            data_format,
            csv_format,
            dpi,
            transparent,
            image_format or _get_default_image_format(),
            verbose,
        )
        # No validation for bundles (yet)
        return bundle_path, yaml_path, None

    # Resolve paths for standard save
    image_path, yaml_path, _ = resolve_save_paths(path, image_format)

    # Save the image
    fig.fig.savefig(image_path, dpi=dpi, bbox_inches="tight", transparent=transparent)

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
