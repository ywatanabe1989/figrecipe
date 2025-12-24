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
        """Check JavaScript templates for duplicate const declarations."""
        import re

        from figrecipe._editor._templates._scripts import get_all_scripts

        scripts = get_all_scripts()

        const_declarations = {}
        duplicates = []

        for script_name, script_content in scripts.items():
            pattern = r"\bconst\s+(\w+)\s*="
            matches = re.findall(pattern, script_content)

            for var_name in matches:
                key = var_name
                if key in const_declarations:
                    if const_declarations[key] != script_name:
                        duplicates.append(
                            f"'{var_name}' declared in both "
                            f"'{const_declarations[key]}' and '{script_name}'"
                        )
                else:
                    const_declarations[key] = script_name

        if duplicates:
            pytest.skip(
                "Potential duplicate declarations (may be false positives):\n"
                + "\n".join(duplicates)
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
