#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for undo/redo functionality in the figure editor."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestUndoRedoScript:
    """Test that undo/redo JavaScript module is properly defined."""

    def test_undo_redo_script_exists(self):
        """Test that SCRIPTS_UNDO_REDO is defined and exported."""
        from figrecipe._editor._templates._scripts import SCRIPTS_UNDO_REDO

        assert SCRIPTS_UNDO_REDO is not None
        assert len(SCRIPTS_UNDO_REDO) > 0

    def test_undo_function_defined(self):
        """Test that undo() function is defined in the script."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function undo()" in SCRIPTS_UNDO_REDO

    def test_redo_function_defined(self):
        """Test that redo() function is defined in the script."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function redo()" in SCRIPTS_UNDO_REDO

    def test_history_stack_defined(self):
        """Test that historyStack is defined."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "historyStack" in SCRIPTS_UNDO_REDO
        assert "redoStack" in SCRIPTS_UNDO_REDO

    def test_push_to_history_defined(self):
        """Test that pushToHistory function is defined."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function pushToHistory()" in SCRIPTS_UNDO_REDO

    def test_capture_state_defined(self):
        """Test that captureState function is defined."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function captureState()" in SCRIPTS_UNDO_REDO

    def test_apply_state_defined(self):
        """Test that applyState function is defined."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function applyState(state)" in SCRIPTS_UNDO_REDO

    def test_max_history_limit(self):
        """Test that MAX_HISTORY limit is set."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "MAX_HISTORY" in SCRIPTS_UNDO_REDO
        assert "50" in SCRIPTS_UNDO_REDO  # Default limit

    def test_clear_history_function(self):
        """Test that clearHistory function is defined for file switching."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function clearHistory()" in SCRIPTS_UNDO_REDO

    def test_update_buttons_function(self):
        """Test that updateUndoRedoButtons function is defined."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function updateUndoRedoButtons()" in SCRIPTS_UNDO_REDO


class TestUndoRedoKeyboardShortcuts:
    """Test keyboard shortcut definitions for undo/redo."""

    def test_ctrl_z_undo_shortcut(self):
        """Test that Ctrl+Z triggers undo."""
        from figrecipe._editor._templates._scripts._core import SCRIPTS_CORE

        assert "Ctrl+Z: Undo" in SCRIPTS_CORE
        assert "event.ctrlKey && !event.shiftKey && event.key === 'z'" in SCRIPTS_CORE
        assert "undo()" in SCRIPTS_CORE

    def test_ctrl_shift_z_redo_shortcut(self):
        """Test that Ctrl+Shift+Z triggers redo."""
        from figrecipe._editor._templates._scripts._core import SCRIPTS_CORE

        assert "Ctrl+Shift+Z or Ctrl+Y: Redo" in SCRIPTS_CORE
        assert "event.ctrlKey && event.shiftKey && event.key === 'Z'" in SCRIPTS_CORE
        assert "redo()" in SCRIPTS_CORE

    def test_ctrl_y_redo_shortcut(self):
        """Test that Ctrl+Y also triggers redo (Windows convention)."""
        from figrecipe._editor._templates._scripts._core import SCRIPTS_CORE

        assert "event.ctrlKey && event.key === 'y'" in SCRIPTS_CORE


class TestUndoRedoUI:
    """Test UI elements for undo/redo."""

    def test_undo_button_in_html(self):
        """Test that Undo button is in HTML template."""
        from figrecipe._editor._templates._html import HTML_TEMPLATE

        assert 'id="btn-undo"' in HTML_TEMPLATE
        assert "Undo" in HTML_TEMPLATE

    def test_redo_button_in_html(self):
        """Test that Redo button is in HTML template."""
        from figrecipe._editor._templates._html import HTML_TEMPLATE

        assert 'id="btn-redo"' in HTML_TEMPLATE
        assert "Redo" in HTML_TEMPLATE

    def test_buttons_disabled_by_default(self):
        """Test that buttons start disabled."""
        from figrecipe._editor._templates._html import HTML_TEMPLATE

        assert 'id="btn-undo"' in HTML_TEMPLATE
        # Check that disabled attribute is present on undo button
        assert (
            'btn-undo" class="btn-small" title="Undo (Ctrl+Z)" disabled'
            in HTML_TEMPLATE
        )

    def test_shortcuts_modal_has_undo_redo(self):
        """Test that shortcuts modal includes undo/redo shortcuts."""
        from figrecipe._editor._templates._html import HTML_TEMPLATE

        assert "<kbd>Ctrl</kbd>+<kbd>Z</kbd>" in HTML_TEMPLATE
        assert "<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Z</kbd>" in HTML_TEMPLATE
        assert "Undo</span>" in HTML_TEMPLATE
        assert "Redo</span>" in HTML_TEMPLATE


class TestUndoRedoIntegration:
    """Test undo/redo integration with other modules."""

    def test_undo_redo_in_combined_scripts(self):
        """Test that undo/redo is included in combined SCRIPTS."""
        from figrecipe._editor._templates._scripts import SCRIPTS

        assert "historyStack" in SCRIPTS
        assert "function undo()" in SCRIPTS
        assert "function redo()" in SCRIPTS

    def test_undo_redo_in_get_all_scripts(self):
        """Test that undo_redo is in get_all_scripts."""
        from figrecipe._editor._templates._scripts import get_all_scripts

        scripts = get_all_scripts()
        assert "undo_redo" in scripts

    def test_button_click_handlers(self):
        """Test that button click handlers are set up."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "undoBtn.addEventListener('click', undo)" in SCRIPTS_UNDO_REDO
        assert "redoBtn.addEventListener('click', redo)" in SCRIPTS_UNDO_REDO


class TestUndoRedoStateManagement:
    """Test state management in undo/redo."""

    def test_prevents_recursive_recording(self):
        """Test that isUndoRedoInProgress flag prevents recursive recording."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "isUndoRedoInProgress" in SCRIPTS_UNDO_REDO
        assert "if (isUndoRedoInProgress) return" in SCRIPTS_UNDO_REDO

    def test_clears_redo_on_new_action(self):
        """Test that redo stack is cleared when new action is performed."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "redoStack.length = 0" in SCRIPTS_UNDO_REDO

    def test_trims_history_when_too_long(self):
        """Test that history is trimmed when exceeding MAX_HISTORY."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "historyStack.length > MAX_HISTORY" in SCRIPTS_UNDO_REDO
        assert "historyStack.shift()" in SCRIPTS_UNDO_REDO

    def test_shows_toast_on_undo_redo(self):
        """Test that toast messages are shown for undo/redo."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "showToast('Undo'" in SCRIPTS_UNDO_REDO
        assert "showToast('Redo'" in SCRIPTS_UNDO_REDO
        assert "showToast('Nothing to undo'" in SCRIPTS_UNDO_REDO
        assert "showToast('Nothing to redo'" in SCRIPTS_UNDO_REDO


class TestUndoRedoPanelPositions:
    """Test panel position undo/redo."""

    def test_capture_state_includes_panel_positions(self):
        """Test that captureState includes panelPositions."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "panelPositions" in SCRIPTS_UNDO_REDO
        assert "JSON.parse(JSON.stringify(panelPositions))" in SCRIPTS_UNDO_REDO

    def test_states_equal_compares_panel_positions(self):
        """Test that statesEqual compares panelPositions."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "function statesEqual(a, b)" in SCRIPTS_UNDO_REDO
        assert "a.panelPositions" in SCRIPTS_UNDO_REDO
        assert "b.panelPositions" in SCRIPTS_UNDO_REDO

    def test_apply_state_restores_panel_positions(self):
        """Test that applyState restores panelPositions via API."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        assert "/update_axes_position" in SCRIPTS_UNDO_REDO
        assert "savedPos.left" in SCRIPTS_UNDO_REDO
        assert "savedPos.top" in SCRIPTS_UNDO_REDO

    def test_apply_state_updates_local_panel_positions(self):
        """Test that applyState updates local panelPositions after API call."""
        from figrecipe._editor._templates._scripts._undo_redo import SCRIPTS_UNDO_REDO

        # After restoring via API, local state must be updated for redo to work
        assert "panelPositions[axKey] = { ...savedPos }" in SCRIPTS_UNDO_REDO

    def test_panel_drag_captures_history(self):
        """Test that panel drag start captures history."""
        from figrecipe._editor._templates._scripts._panel_drag import SCRIPTS_PANEL_DRAG

        assert "pushToHistory" in SCRIPTS_PANEL_DRAG

    def test_legend_drag_captures_history(self):
        """Test that legend drag start captures history."""
        from figrecipe._editor._templates._scripts._legend_drag import (
            SCRIPTS_LEGEND_DRAG,
        )

        assert "pushToHistory" in SCRIPTS_LEGEND_DRAG


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
