#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo runner for all plotters."""

from pathlib import Path

from ._plotters import PLOTTERS


def _compare_images(img1_path, img2_path, tolerance=0):
    """Compare two images pixel by pixel.

    Parameters
    ----------
    img1_path : Path
        Path to first image.
    img2_path : Path
        Path to second image.
    tolerance : int
        Maximum allowed pixel difference (0 for exact match).

    Returns
    -------
    tuple
        (is_match, max_diff, mean_diff, diff_pixels)
    """
    import numpy as np
    from PIL import Image

    img1 = np.array(Image.open(img1_path))
    img2 = np.array(Image.open(img2_path))

    if img1.shape != img2.shape:
        return False, float("inf"), float("inf"), -1

    diff = np.abs(img1.astype(float) - img2.astype(float))
    max_diff = diff.max()
    mean_diff = diff.mean()
    diff_pixels = (diff > tolerance).sum()

    is_match = max_diff <= tolerance
    return is_match, max_diff, mean_diff, diff_pixels


def run_all_demos(
    fr,
    output_dir=None,
    show=False,
    verbose=True,
    reproduce=False,
    pixel_perfect=False,
    tolerance=0,
):
    """Run all demo plotters and save outputs using fr.save().

    Parameters
    ----------
    fr : module
        figrecipe module (e.g., `import figrecipe as fr`).
    output_dir : Path or str, optional
        Directory to save output images. If None, uses /tmp/figrecipe_demos.
    show : bool
        Whether to show figures interactively.
    verbose : bool
        Whether to print progress.
    reproduce : bool
        Whether to also generate reproduced plots from YAML recipes.
    pixel_perfect : bool
        If True, compare each plot with its reproduction immediately and
        STOP on first non-matching plot. Implies reproduce=True.
    tolerance : int
        Maximum allowed pixel difference for pixel_perfect mode (0 for exact).

    Returns
    -------
    dict
        Results for each demo: {name: {'success': bool, 'error': str or None, 'path': str}}
    """
    import matplotlib.pyplot as _plt
    import numpy as np

    rng = np.random.default_rng(42)
    results = {}

    if output_dir is None:
        output_dir = Path("/tmp/figrecipe_demos")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # pixel_perfect implies reproduce
    if pixel_perfect:
        reproduce = True

    total = len(PLOTTERS)

    # Sequential mode: plot -> reproduce -> verify -> next
    if pixel_perfect:
        if verbose:
            print("=" * 60)
            print("PIXEL-PERFECT VERIFICATION MODE")
            print(f"Tolerance: {tolerance} (0 = exact match)")
            print("=" * 60)

        for i, (name, func) in enumerate(sorted(PLOTTERS.items()), 1):
            if verbose:
                print(f"\n[{i}/{total}] Testing: {name}")
                print("-" * 40)

            # Step 1: Generate original plot
            try:
                fig, ax = func(fr, rng)
                out_path = output_dir / f"plot_{name}.png"
                yaml_path = output_dir / f"plot_{name}.yaml"
                fr.save(fig, out_path, validate=False, verbose=False)
                _plt.close("all")
                if verbose:
                    print(f"  [1/3] Original saved: {out_path.name}")
            except Exception as e:
                results[name] = {"success": False, "error": str(e), "path": None}
                print(f"  FAILED to generate: {e}")
                raise RuntimeError(f"Failed to generate {name}: {e}")

            # Step 2: Reproduce from YAML
            reproduced_path = output_dir / f"plot_{name}_reproduced.png"
            try:
                fig2, ax2 = fr.reproduce(str(yaml_path))
                fr.save(fig2, reproduced_path, validate=False, verbose=False)
                _plt.close("all")
                if verbose:
                    print(f"  [2/3] Reproduced saved: {reproduced_path.name}")
            except Exception as e:
                results[name] = {
                    "success": False,
                    "error": f"Reproduce failed: {e}",
                    "path": str(out_path),
                }
                print(f"  FAILED to reproduce: {e}")
                raise RuntimeError(f"Failed to reproduce {name}: {e}")

            # Step 3: Compare pixel by pixel
            is_match, max_diff, mean_diff, diff_pixels = _compare_images(
                out_path, reproduced_path, tolerance
            )

            if is_match:
                results[name] = {"success": True, "error": None, "path": str(out_path)}
                if verbose:
                    print("  [3/3] PIXEL-PERFECT MATCH ✓")
                    print(f"        Max diff: {max_diff}, Mean diff: {mean_diff:.4f}")
            else:
                results[name] = {
                    "success": False,
                    "error": f"Pixel mismatch: max={max_diff}, mean={mean_diff:.4f}, diff_pixels={diff_pixels}",
                    "path": str(out_path),
                }
                print("  [3/3] PIXEL MISMATCH ✗")
                print(f"        Max diff: {max_diff}")
                print(f"        Mean diff: {mean_diff:.4f}")
                print(f"        Pixels differing: {diff_pixels}")
                print("\n" + "=" * 60)
                print(f"STOPPED AT: {name}")
                print(f"Original:   {out_path}")
                print(f"Reproduced: {reproduced_path}")
                print("=" * 60)
                assert False, (
                    f"Pixel-perfect reproduction FAILED for '{name}': "
                    f"max_diff={max_diff}, mean_diff={mean_diff:.4f}, "
                    f"original={out_path}, reproduced={reproduced_path}"
                )

        if verbose:
            print("\n" + "=" * 60)
            print(f"ALL {total} PLOTS PIXEL-PERFECT ✓")
            print("=" * 60)

        return results

    # Original batch mode
    for i, (name, func) in enumerate(sorted(PLOTTERS.items()), 1):
        try:
            fig, ax = func(fr, rng)
            out_path = output_dir / f"plot_{name}.png"
            # Use fr.save() for proper mm layout and auto-cropping
            fr.save(fig, out_path, validate=False, verbose=False)
            if show:
                _plt.show()
            else:
                _plt.close("all")
            results[name] = {"success": True, "error": None, "path": str(out_path)}
            if verbose:
                print(f"[{i}/{total}] {name}: OK")
        except Exception as e:
            results[name] = {"success": False, "error": str(e), "path": None}
            if verbose:
                print(f"[{i}/{total}] {name}: FAILED - {e}")
            _plt.close("all")

    # Generate reproduced plots if requested
    if reproduce:
        if verbose:
            print("\nGenerating reproduced plots...")
        reproduced_count = 0
        failed_reproductions = []
        for name, result in results.items():
            if result["success"]:
                yaml_path = output_dir / f"plot_{name}.yaml"
                reproduced_path = output_dir / f"plot_{name}_reproduced.png"
                if yaml_path.exists():
                    try:
                        # fr.reproduce returns (fig, ax), use fr.save for proper styling
                        fig, ax = fr.reproduce(str(yaml_path))
                        fr.save(fig, reproduced_path, validate=False, verbose=False)
                        reproduced_count += 1
                        if verbose:
                            print(f"  Reproduced: {name}")
                    except Exception as e:
                        failed_reproductions.append((name, str(e)))
                        if verbose:
                            print(f"  FAILED to reproduce {name}: {e}")
                    _plt.close("all")
        if verbose:
            print(f"Reproduced {reproduced_count} plots")
        if failed_reproductions:
            raise RuntimeError(
                f"Failed to reproduce {len(failed_reproductions)} plots: "
                + ", ".join(f"{n}: {e}" for n, e in failed_reproductions)
            )

    # Summary
    success = sum(1 for r in results.values() if r["success"])
    if verbose:
        print(f"\nSummary: {success}/{total} demos succeeded")
        print(f"Output directory: {output_dir}")

    return results


# EOF
