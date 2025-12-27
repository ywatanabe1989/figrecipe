#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run all demo recordings and create combined video.

Usage:
    python run_all.py                    # Run all demos
    python run_all.py --demo 01          # Run specific demo
    python run_all.py --no-headless      # Run with visible browser
    python run_all.py --combine-only     # Only combine existing videos
"""

import argparse
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import demos - use importlib for dynamic loading
import importlib.util

from figrecipe._dev.browser import concatenate_videos, convert_to_gif


def load_demo_class(demo_file: str, class_name: str):
    """Dynamically load a demo class from file."""
    demo_path = Path(__file__).parent / demo_file
    spec = importlib.util.spec_from_file_location("demo_module", demo_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


# Register all demos: (filename, class_name)
DEMO_REGISTRY = {
    "01": ("01_enable_dark_mode.py", "DarkModeDemo"),
    "02": ("02_change_color.py", "ChangeColorDemo"),
    "03": ("03_datatable_import.py", "DatatableDemo"),
    "04": ("04_image_drop.py", "ImageDropDemo"),
    "05": ("05_panel_drag.py", "PanelDragDemo"),
    "06": ("06_file_browser.py", "FileBrowserDemo"),
}

OUTPUT_DIR = Path(__file__).parent / "outputs"


def get_demo_class(demo_id: str):
    """Get demo class by ID using lazy loading."""
    if demo_id not in DEMO_REGISTRY:
        raise ValueError(
            f"Unknown demo: {demo_id}. Available: {list(DEMO_REGISTRY.keys())}"
        )
    filename, class_name = DEMO_REGISTRY[demo_id]
    return load_demo_class(filename, class_name)


def run_demo(demo_id: str, url: str, headless: bool) -> Path:
    """Run a single demo.

    Parameters
    ----------
    demo_id : str
        Demo ID (e.g., "01").
    url : str
        Editor URL.
    headless : bool
        Run in headless mode.

    Returns
    -------
    Path
        Path to output MP4 file.
    """
    demo_class = get_demo_class(demo_id)
    demo = demo_class(url=url, headless=headless, output_dir=OUTPUT_DIR)

    print(f"\n{'=' * 50}")
    print(f"Recording: {demo.title}")
    print(f"{'=' * 50}")

    mp4_path, gif_path = demo.execute()
    return mp4_path


def combine_videos(output_name: str = "combined") -> tuple:
    """Combine all recorded videos.

    Parameters
    ----------
    output_name : str
        Base name for combined output.

    Returns
    -------
    tuple
        (mp4_path, gif_path)
    """
    # Find all MP4 files in order
    mp4_files = sorted(OUTPUT_DIR.glob("*.mp4"))
    mp4_files = [f for f in mp4_files if not f.name.startswith("combined")]

    if not mp4_files:
        print("No video files found to combine")
        return None, None

    print(f"\nCombining {len(mp4_files)} videos...")
    for f in mp4_files:
        print(f"  - {f.name}")

    combined_mp4 = OUTPUT_DIR / f"{output_name}.mp4"
    combined_gif = OUTPUT_DIR / f"{output_name}.gif"

    try:
        concatenate_videos(mp4_files, combined_mp4)
        print(f"Combined MP4: {combined_mp4}")
    except Exception as e:
        print(f"Failed to combine videos: {e}")
        return None, None

    try:
        convert_to_gif(combined_mp4, combined_gif)
        print(f"Combined GIF: {combined_gif}")
    except Exception as e:
        print(f"Failed to convert to GIF: {e}")
        combined_gif = None

    return combined_mp4, combined_gif


def main():
    parser = argparse.ArgumentParser(description="Run demo recordings")
    parser.add_argument(
        "--demo",
        type=str,
        help="Run specific demo by ID (e.g., 01, 02)",
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:5050",
        help="Editor URL",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run in headless mode (default)",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Run with visible browser",
    )
    parser.add_argument(
        "--combine-only",
        action="store_true",
        help="Only combine existing videos",
    )
    parser.add_argument(
        "--no-combine",
        action="store_true",
        help="Skip video combination",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.combine_only:
        combine_videos()
        return

    if args.demo:
        # Run specific demo
        run_demo(args.demo, args.url, args.headless)
    else:
        # Run all demos
        for demo_id in sorted(DEMO_REGISTRY.keys()):
            try:
                run_demo(demo_id, args.url, args.headless)
            except Exception as e:
                print(f"Demo {demo_id} failed: {e}")
                continue

    # Combine videos
    if not args.no_combine and not args.demo:
        combine_videos()

    print("\nDone!")


if __name__ == "__main__":
    main()

# EOF
