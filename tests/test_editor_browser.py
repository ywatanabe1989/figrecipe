#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JavaScript code integrity tests for the figrecipe editor.

These tests verify JavaScript code quality without requiring a browser.
For browser-based tests, see tests/editor/ directory.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestEditorScriptIntegrity:
    """Test JavaScript code integrity without running server."""

    def test_no_duplicate_const_declarations(self):
        """Check JavaScript templates for duplicate global const declarations.

        Note: This test only flags top-level const declarations (not inside functions).
        Local variables with common names (response, data, img, etc.) are expected
        to be reused across different script modules and functions.
        """
        import re

        from figrecipe._editor._templates._scripts import get_all_scripts

        scripts = get_all_scripts()

        # Only check for top-level const declarations (not inside functions)
        # Pattern: const at start of line (not indented) = likely global
        global_const_pattern = r"^const\s+(\w+)\s*="

        global_consts = {}
        duplicates = []

        for script_name, script_content in scripts.items():
            # Find const declarations at start of line (likely global scope)
            matches = re.findall(global_const_pattern, script_content, re.MULTILINE)

            for var_name in matches:
                if var_name in global_consts:
                    if global_consts[var_name] != script_name:
                        duplicates.append(
                            f"Global '{var_name}' declared in both "
                            f"'{global_consts[var_name]}' and '{script_name}'"
                        )
                else:
                    global_consts[var_name] = script_name

        # This should now pass since local variables are not flagged
        assert not duplicates, (
            "Duplicate global const declarations found:\n" + "\n".join(duplicates)
        )

    def test_scripts_no_obvious_errors(self):
        """Check for obvious JavaScript errors that would cause runtime failures."""
        from figrecipe._editor._templates._scripts import get_all_scripts

        scripts = get_all_scripts()

        for script_name, script_content in scripts.items():
            assert len(script_content.strip()) > 0, f"{script_name}: Empty script"

            assert "fucntion" not in script_content, f"{script_name}: Typo 'fucntion'"
            assert "retrun" not in script_content, f"{script_name}: Typo 'retrun'"
            assert "cosnt" not in script_content, f"{script_name}: Typo 'cosnt'"

            first_line = script_content.strip().split("\n")[0]
            assert not first_line.startswith(
                "def "
            ), f"{script_name}: Contains Python syntax"
            assert not first_line.startswith(
                "import "
            ), f"{script_name}: Contains Python import"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
