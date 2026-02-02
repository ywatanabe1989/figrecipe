#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""imshow: image display demo."""

import warnings
from pathlib import Path


def _load_scitex_icon():
    """Load scitex icon image if available.

    Returns
    -------
    numpy.ndarray or None
        Image array if icon found, None otherwise.
    """
    # Path from demo file: image_matrix -> demo_plotters -> _dev -> figrecipe -> src -> project_root
    icon_path = Path(__file__).parents[5] / "docs" / "scitex-icon-navy-inverted.png"

    if not icon_path.exists():
        # Try alternative path relative to package root (for installed package)
        import figrecipe

        pkg_root = Path(figrecipe.__file__).parent.parent.parent
        icon_path = pkg_root / "docs" / "scitex-icon-navy-inverted.png"

    if icon_path.exists():
        try:
            import matplotlib.image as mpimg

            return mpimg.imread(str(icon_path))
        except Exception as e:
            warnings.warn(
                f"Failed to load scitex icon: {e}. Falling back to synthetic data.",
                stacklevel=2,
            )
            return None
    return None


def plot_imshow(plt, rng, ax=None):
    """Image display demo.

    Demonstrates: ax.imshow()

    Uses the scitex icon if available, otherwise falls back to synthetic data.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Try to load scitex icon, fall back to synthetic data
    data = _load_scitex_icon()
    is_synthetic = data is None
    if is_synthetic:
        warnings.warn(
            "Scitex icon not found. Using synthetic data for imshow demo.",
            stacklevel=2,
        )
        data = rng.uniform(0, 1, (20, 20))

    im = ax.imshow(data, id="imshow")
    ax.axis("off")
    ax.set_title("imshow")
    # Add colorbar for 2D data (not RGB images)
    if is_synthetic or (data.ndim == 2):
        from figrecipe._utils._colorbar import add_colorbar

        add_colorbar(fig, im, ax=ax)
    return fig, ax


# EOF
