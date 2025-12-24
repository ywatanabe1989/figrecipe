#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared fixtures for editor browser tests."""

import subprocess
import sys
import time
from pathlib import Path
from typing import Generator

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def check_playwright_available() -> bool:
    """Check if playwright is available."""
    import importlib.util

    return importlib.util.find_spec("playwright") is not None


requires_playwright = pytest.mark.skipif(
    not check_playwright_available(),
    reason="Playwright not installed. Install with: pip install playwright && playwright install chromium",
)


class EditorServer:
    """Context manager for running the editor server in background."""

    def __init__(self, recipe_path: Path, port: int = 5051):
        self.recipe_path = recipe_path
        self.port = port
        self.process = None
        self.url = f"http://127.0.0.1:{port}"

    def __enter__(self):
        """Start the editor server."""
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                f"""
import sys
sys.path.insert(0, 'src')
import figrecipe as fr
fr.edit('{self.recipe_path}', port={self.port}, open_browser=False)
""",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent.parent.parent,
        )

        max_wait = 10
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                import urllib.request

                urllib.request.urlopen(self.url, timeout=1)
                break
            except Exception:
                time.sleep(0.2)
        else:
            self.process.terminate()
            raise RuntimeError(f"Editor server failed to start on port {self.port}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the editor server."""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)


@pytest.fixture
def sample_recipe(tmp_path) -> Path:
    """Create a sample recipe for testing."""
    import figrecipe as fr

    rng = np.random.default_rng(42)

    fig, ax = fr.subplots()
    ax.plot([1, 2, 3], [1, 4, 9], id="line1", label="Quadratic")
    ax.scatter(rng.random(10), rng.random(10), id="scatter1", label="Random")
    ax.set_xlabel("X Label")
    ax.set_ylabel("Y Label")
    ax.set_title("Test Figure")
    ax.legend()

    recipe_path = tmp_path / "test_recipe.yaml"
    fr.save(fig, recipe_path)
    plt.close(fig.fig)

    return recipe_path


@pytest.fixture
def editor_server(sample_recipe) -> Generator[EditorServer, None, None]:
    """Start editor server for testing."""
    with EditorServer(sample_recipe, port=5051) as server:
        yield server
