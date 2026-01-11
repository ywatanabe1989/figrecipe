#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproducibility validation for figrecipe recipes."""

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import numpy as np


@dataclass
class ValidationResult:
    """Result of reproducibility validation.

    Attributes
    ----------
    valid : bool
        True if reproduction is considered valid (MSE below threshold).
    mse : float
        Mean squared error between original and reproduced images.
    psnr : float
        Peak signal-to-noise ratio (higher is better, inf if identical).
    max_diff : float
        Maximum pixel difference (0-255 scale).
    size_original : tuple
        (height, width) of original image.
    size_reproduced : tuple
        (height, width) of reproduced image.
    same_size : bool
        True if dimensions match exactly.
    file_size_diff : int
        Difference in file sizes (bytes).
    message : str
        Human-readable summary.
    """

    valid: bool
    mse: float
    psnr: float
    max_diff: float
    size_original: tuple
    size_reproduced: tuple
    same_size: bool
    file_size_diff: int
    message: str

    def __repr__(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        return (
            f"ValidationResult({status}, mse={self.mse:.2f}, "
            f"size={'match' if self.same_size else 'differ'})"
        )

    def summary(self) -> str:
        """Return detailed summary string."""
        lines = [
            f"Reproducibility Validation: {'PASSED' if self.valid else 'FAILED'}",
            f"  Dimensions: {self.size_original} vs {self.size_reproduced} "
            f"({'match' if self.same_size else 'DIFFER'})",
            f"  Pixel MSE: {self.mse:.2f}",
            f"  Max pixel diff: {self.max_diff:.1f}",
            f"  PSNR: {self.psnr:.1f} dB"
            if not np.isinf(self.psnr)
            else "  PSNR: inf (identical)",
            f"  File size diff: {self.file_size_diff:+d} bytes",
        ]
        if not self.valid:
            lines.append(f"  Note: {self.message}")
        return "\n".join(lines)


def validate_recipe(
    fig,
    recipe_path: Union[str, Path],
    mse_threshold: float = 100.0,
    dpi: int = 150,
) -> ValidationResult:
    """Validate that a recipe can faithfully reproduce the original figure.

    Parameters
    ----------
    fig : RecordingFigure
        The original figure (with matplotlib figure accessible via fig.fig).
    recipe_path : str or Path
        Path to the saved recipe file.
    mse_threshold : float
        Maximum acceptable MSE for validation to pass (default: 100).
        Lower values require closer matches.
    dpi : int
        DPI for comparison images (default: 150).

    Returns
    -------
    ValidationResult
        Detailed comparison results.
    """
    import matplotlib.pyplot as plt

    from ._reproducer import reproduce
    from ._utils._image_diff import compare_images

    recipe_path = Path(recipe_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Save original figure to temp image
        # Use the same saving approach for both to ensure consistent comparison
        original_path = tmpdir / "original.png"

        # Check if constrained_layout is being used
        use_constrained = fig.fig.get_constrained_layout()
        mm_layout = getattr(fig, "_mm_layout", None)

        if use_constrained and mm_layout is not None:
            # Use bbox_inches='tight' like we do in fr.save()
            crop_margin_left_mm = mm_layout.get("crop_margin_left_mm", 1)
            crop_margin_right_mm = mm_layout.get("crop_margin_right_mm", 1)
            crop_margin_top_mm = mm_layout.get("crop_margin_top_mm", 1)
            crop_margin_bottom_mm = mm_layout.get("crop_margin_bottom_mm", 1)
            avg_margin_mm = (
                crop_margin_left_mm
                + crop_margin_right_mm
                + crop_margin_top_mm
                + crop_margin_bottom_mm
            ) / 4
            pad_inches = avg_margin_mm / 25.4
            fig.fig.savefig(
                original_path, dpi=dpi, bbox_inches="tight", pad_inches=pad_inches
            )
        else:
            fig.fig.savefig(original_path, dpi=dpi)

        # Reproduce from recipe
        reproduced_fig, _ = reproduce(recipe_path)

        # Save reproduced figure
        reproduced_path = tmpdir / "reproduced.png"

        # Use same saving approach for reproduced figure
        use_constrained_repro = reproduced_fig.fig.get_constrained_layout()
        mm_layout_repro = getattr(reproduced_fig, "_mm_layout", None)

        if use_constrained_repro and mm_layout_repro is not None:
            crop_margin_left_mm = mm_layout_repro.get("crop_margin_left_mm", 1)
            crop_margin_right_mm = mm_layout_repro.get("crop_margin_right_mm", 1)
            crop_margin_top_mm = mm_layout_repro.get("crop_margin_top_mm", 1)
            crop_margin_bottom_mm = mm_layout_repro.get("crop_margin_bottom_mm", 1)
            avg_margin_mm = (
                crop_margin_left_mm
                + crop_margin_right_mm
                + crop_margin_top_mm
                + crop_margin_bottom_mm
            ) / 4
            pad_inches = avg_margin_mm / 25.4
            reproduced_fig.fig.savefig(
                reproduced_path, dpi=dpi, bbox_inches="tight", pad_inches=pad_inches
            )
        else:
            reproduced_fig.savefig(reproduced_path, dpi=dpi)

        # Close reproduced figure to prevent double display in notebooks
        # Use .fig to get underlying matplotlib Figure since reproduce() returns RecordingFigure
        mpl_fig = (
            reproduced_fig.fig if hasattr(reproduced_fig, "fig") else reproduced_fig
        )
        plt.close(mpl_fig)

        # Compare images
        diff = compare_images(original_path, reproduced_path)

        # Determine validity
        mse = diff["mse"]
        if np.isnan(mse):
            # Different sizes - invalid
            valid = False
            message = f"Image dimensions differ: {diff['size1']} vs {diff['size2']}"
        elif mse > mse_threshold:
            valid = False
            message = f"MSE ({mse:.2f}) exceeds threshold ({mse_threshold})"
        else:
            valid = True
            message = "Reproduction matches original within threshold"

        return ValidationResult(
            valid=valid,
            mse=mse if not np.isnan(mse) else float("inf"),
            psnr=diff["psnr"],
            max_diff=diff["max_diff"]
            if not np.isnan(diff["max_diff"])
            else float("inf"),
            size_original=diff["size1"],
            size_reproduced=diff["size2"],
            same_size=diff["same_size"],
            file_size_diff=diff["file_size2"] - diff["file_size1"],
            message=message,
        )


def validate_on_save(
    fig,
    recipe_path: Union[str, Path],
    mse_threshold: float = 100.0,
    dpi: int = 150,
    raise_on_failure: bool = False,
) -> Optional[ValidationResult]:
    """Validate recipe immediately after saving.

    Parameters
    ----------
    fig : RecordingFigure
        The original figure.
    recipe_path : str or Path
        Path where recipe was saved.
    mse_threshold : float
        Maximum acceptable MSE.
    dpi : int
        DPI for comparison.
    raise_on_failure : bool
        If True, raise ValueError when validation fails.

    Returns
    -------
    ValidationResult
        Validation results.

    Raises
    ------
    ValueError
        If raise_on_failure=True and validation fails.
    """
    result = validate_recipe(fig, recipe_path, mse_threshold, dpi)

    if raise_on_failure and not result.valid:
        raise ValueError(f"Recipe validation failed: {result.message}")

    return result
