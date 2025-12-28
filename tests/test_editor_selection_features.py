#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for selection features in the figure editor.

This module tests:
- Annotation drag (draggable panel labels, text annotations)
- Multi-selection with Ctrl+Click
- Region selection (marquee/rectangle selection)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestAnnotationDragScript:
    """Test that annotation drag JavaScript module is properly defined."""

    def test_annotation_drag_script_exists(self):
        """Test that SCRIPTS_ANNOTATION_DRAG is defined and exported."""
        from figrecipe._editor._templates._scripts import SCRIPTS_ANNOTATION_DRAG

        assert SCRIPTS_ANNOTATION_DRAG is not None
        assert len(SCRIPTS_ANNOTATION_DRAG) > 0

    def test_annotation_snap_config_defined(self):
        """Test that ANNOTATION_SNAP is defined with expected properties."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "ANNOTATION_SNAP" in SCRIPTS_ANNOTATION_DRAG
        assert "threshold" in SCRIPTS_ANNOTATION_DRAG
        assert "magneticZone" in SCRIPTS_ANNOTATION_DRAG
        assert "snapToEdges" in SCRIPTS_ANNOTATION_DRAG

    def test_init_annotation_drag_function(self):
        """Test that initAnnotationDrag function is defined."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "function initAnnotationDrag(" in SCRIPTS_ANNOTATION_DRAG

    def test_is_annotation_element_function(self):
        """Test that isAnnotationElement function is defined."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "function isAnnotationElement(" in SCRIPTS_ANNOTATION_DRAG

    def test_annotation_drag_handlers(self):
        """Test that annotation drag handlers are defined."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "function startAnnotationDrag(" in SCRIPTS_ANNOTATION_DRAG
        assert "function handleAnnotationDragMove(" in SCRIPTS_ANNOTATION_DRAG
        assert "function handleAnnotationDragEnd(" in SCRIPTS_ANNOTATION_DRAG

    def test_annotation_snapping_function(self):
        """Test that applyAnnotationSnap function is defined."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "function applyAnnotationSnap(" in SCRIPTS_ANNOTATION_DRAG

    def test_annotation_positions_tracking(self):
        """Test that annotation positions are tracked."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "annotationPositions" in SCRIPTS_ANNOTATION_DRAG
        assert "function initAnnotationPositions(" in SCRIPTS_ANNOTATION_DRAG

    def test_apply_annotation_position_function(self):
        """Test that applyAnnotationPosition function is defined."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "async function applyAnnotationPosition(" in SCRIPTS_ANNOTATION_DRAG
        assert "/update_annotation_position" in SCRIPTS_ANNOTATION_DRAG

    def test_annotation_drag_overlay(self):
        """Test that annotation drag overlay is created."""
        from figrecipe._editor._templates._scripts._annotation_drag import (
            SCRIPTS_ANNOTATION_DRAG,
        )

        assert "annotation-drag-overlay" in SCRIPTS_ANNOTATION_DRAG
        assert "annotation-drag-label" in SCRIPTS_ANNOTATION_DRAG


class TestMultiSelectScript:
    """Test that multi-selection JavaScript module is properly defined."""

    def test_multi_select_script_exists(self):
        """Test that SCRIPTS_MULTI_SELECT is defined and exported."""
        from figrecipe._editor._templates._scripts import SCRIPTS_MULTI_SELECT

        assert SCRIPTS_MULTI_SELECT is not None
        assert len(SCRIPTS_MULTI_SELECT) > 0

    def test_selected_elements_array(self):
        """Test that selectedElements array is defined."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "let selectedElements = []" in SCRIPTS_MULTI_SELECT

    def test_multi_select_mode_detection(self):
        """Test that isMultiSelectMode function is defined."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "function isMultiSelectMode(" in SCRIPTS_MULTI_SELECT
        assert "ctrlKey" in SCRIPTS_MULTI_SELECT
        assert "metaKey" in SCRIPTS_MULTI_SELECT

    def test_selection_management_functions(self):
        """Test that selection management functions are defined."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "function isElementSelected(" in SCRIPTS_MULTI_SELECT
        assert "function addToSelection(" in SCRIPTS_MULTI_SELECT
        assert "function removeFromSelection(" in SCRIPTS_MULTI_SELECT
        assert "function toggleInSelection(" in SCRIPTS_MULTI_SELECT

    def test_clear_multi_selection(self):
        """Test that clearMultiSelection function is defined."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "function clearMultiSelection(" in SCRIPTS_MULTI_SELECT

    def test_draw_multi_selection(self):
        """Test that drawMultiSelection function is defined."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "function drawMultiSelection(" in SCRIPTS_MULTI_SELECT

    def test_select_all_of_type(self):
        """Test that selectAllOfType function is defined."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "function selectAllOfType(" in SCRIPTS_MULTI_SELECT

    def test_get_selected_panel_indices(self):
        """Test that getSelectedPanelIndices function is defined."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "function getSelectedPanelIndices(" in SCRIPTS_MULTI_SELECT

    def test_multi_select_keyboard_shortcuts(self):
        """Test that Ctrl+A shortcut is handled."""
        from figrecipe._editor._templates._scripts._multi_select import (
            SCRIPTS_MULTI_SELECT,
        )

        assert "handleMultiSelectKeyboard" in SCRIPTS_MULTI_SELECT
        assert "ctrlKey" in SCRIPTS_MULTI_SELECT


class TestRegionSelectScript:
    """Test that region selection JavaScript module is properly defined."""

    def test_region_select_script_exists(self):
        """Test that SCRIPTS_REGION_SELECT is defined and exported."""
        from figrecipe._editor._templates._scripts import SCRIPTS_REGION_SELECT

        assert SCRIPTS_REGION_SELECT is not None
        assert len(SCRIPTS_REGION_SELECT) > 0

    def test_region_selection_state(self):
        """Test that region selection state variables are defined."""
        from figrecipe._editor._templates._scripts._region_select import (
            SCRIPTS_REGION_SELECT,
        )

        assert "let isRegionSelecting = false" in SCRIPTS_REGION_SELECT
        assert "regionSelectStart" in SCRIPTS_REGION_SELECT
        assert "regionSelectRect" in SCRIPTS_REGION_SELECT

    def test_init_region_select(self):
        """Test that initRegionSelect function is defined."""
        from figrecipe._editor._templates._scripts._region_select import (
            SCRIPTS_REGION_SELECT,
        )

        assert "function initRegionSelect(" in SCRIPTS_REGION_SELECT

    def test_region_select_handlers(self):
        """Test that region selection handlers are defined."""
        from figrecipe._editor._templates._scripts._region_select import (
            SCRIPTS_REGION_SELECT,
        )

        assert "function handleRegionSelectStart(" in SCRIPTS_REGION_SELECT
        assert "function handleRegionSelectMove(" in SCRIPTS_REGION_SELECT
        assert "function handleRegionSelectEnd(" in SCRIPTS_REGION_SELECT

    def test_select_elements_in_region(self):
        """Test that selectElementsInRegion function is defined."""
        from figrecipe._editor._templates._scripts._region_select import (
            SCRIPTS_REGION_SELECT,
        )

        assert "function selectElementsInRegion(" in SCRIPTS_REGION_SELECT

    def test_rects_intersect_function(self):
        """Test that rectsIntersect helper is defined."""
        from figrecipe._editor._templates._scripts._region_select import (
            SCRIPTS_REGION_SELECT,
        )

        assert "function rectsIntersect(" in SCRIPTS_REGION_SELECT

    def test_region_select_overlay(self):
        """Test that region selection overlay is created."""
        from figrecipe._editor._templates._scripts._region_select import (
            SCRIPTS_REGION_SELECT,
        )

        assert "region-select-overlay" in SCRIPTS_REGION_SELECT
        assert "border: 2px dashed" in SCRIPTS_REGION_SELECT

    def test_ctrl_drag_adds_to_selection(self):
        """Test that Ctrl+drag adds to existing selection."""
        from figrecipe._editor._templates._scripts._region_select import (
            SCRIPTS_REGION_SELECT,
        )

        assert "isMultiSelectMode" in SCRIPTS_REGION_SELECT
        assert "addToExisting" in SCRIPTS_REGION_SELECT


class TestAnnotationRoutesAPI:
    """Test annotation-related Flask routes."""

    def test_routes_module_exists(self):
        """Test that _routes_annotation module exists."""
        from figrecipe._editor._routes_annotation import register_annotation_routes

        assert register_annotation_routes is not None

    def test_annotation_position_api_routes(self):
        """Test that annotation positions API is documented in routes."""
        from figrecipe._editor._routes_annotation import register_annotation_routes

        # Check that the function is callable
        assert callable(register_annotation_routes)


class TestScriptsIntegration:
    """Test that all new scripts are properly integrated."""

    def test_all_new_scripts_in_combined(self):
        """Test that new scripts are in the combined SCRIPTS constant."""
        from figrecipe._editor._templates._scripts import SCRIPTS

        # Check multi-select functions
        assert "selectedElements" in SCRIPTS
        assert "isMultiSelectMode" in SCRIPTS

        # Check region select functions
        assert "isRegionSelecting" in SCRIPTS
        assert "handleRegionSelectStart" in SCRIPTS

        # Check annotation drag functions
        assert "initAnnotationDrag" in SCRIPTS
        assert "startAnnotationDrag" in SCRIPTS

    def test_new_scripts_in_get_all_scripts(self):
        """Test that new scripts are in get_all_scripts dictionary."""
        from figrecipe._editor._templates._scripts import get_all_scripts

        scripts = get_all_scripts()
        assert "multi_select" in scripts
        assert "annotation_drag" in scripts
        assert "region_select" in scripts

    def test_new_scripts_in_all_exports(self):
        """Test that new scripts are exported in __all__."""
        from figrecipe._editor._templates._scripts import __all__

        assert "SCRIPTS_MULTI_SELECT" in __all__
        assert "SCRIPTS_ANNOTATION_DRAG" in __all__
        assert "SCRIPTS_REGION_SELECT" in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
