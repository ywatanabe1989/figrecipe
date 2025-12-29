#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File browser panel HTML for the figure editor."""

HTML_FILE_BROWSER = """
        <!-- File Browser Panel -->
        <div class="file-browser-panel" id="file-browser-panel">
            <div class="file-browser-header">
                <div class="header-title">
                    <span>Files</span>
                </div>
                <div class="file-browser-actions">
                    <button id="btn-new-file" class="btn-new-file" title="Create new figure">+</button>
                    <button id="btn-refresh-files" title="Refresh file list">&#x21bb;</button>
                    <button id="btn-collapse-browser" class="btn-collapse" title="Collapse panel">&#x276E;</button>
                </div>
            </div>
            <div class="file-tree-container" id="file-tree-container">
                <ul class="file-tree" id="file-tree">
                    <!-- File tree items populated by JavaScript -->
                </ul>
            </div>
            <div class="file-browser-resize" id="file-browser-resize"></div>
        </div>
"""

__all__ = ["HTML_FILE_BROWSER"]

# EOF
