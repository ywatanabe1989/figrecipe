#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File browser panel HTML for the figure editor."""

HTML_FILE_BROWSER = """
        <!-- File Browser Panel -->
        <div class="file-browser-panel" id="file-browser-panel">
            <div class="file-browser-header">
                <div class="header-title">
                    <span>FILES</span>
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
            <div class="file-browser-footer">
                <a href="https://scitex.ai" target="_blank" class="brand-link" title="FigRecipe - Part of SciTeX">
                    <img src="data:image/png;base64,SCITEX_ICON_PLACEHOLDER" alt="SciTeX" class="brand-icon">
                    <div class="brand-info">
                        <span class="brand-name">FigRecipe</span>
                        <span class="brand-version">vVERSION_PLACEHOLDER by SciTeX™</span>
                    </div>
                </a>
                <div class="brand-meta" DEBUG_META_DISPLAY_PLACEHOLDER>
                    <span class="server-time">Started: SERVER_START_TIME_PLACEHOLDER</span>
                </div>
            </div>
            <div class="file-browser-resize" id="file-browser-resize"></div>
        </div>
"""

__all__ = ["HTML_FILE_BROWSER"]

# EOF
