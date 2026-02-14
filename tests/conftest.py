"""Root conftest for figrecipe tests."""

import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def _close_figures():
    """Close all matplotlib figures after each test to prevent memory leaks."""
    yield
    plt.close("all")
