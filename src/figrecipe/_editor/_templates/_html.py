#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML template for figure editor.
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="DARK_MODE_THEME_PLACEHOLDER">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FigRecipe Editor</title>
    <link rel="icon" type="image/x-icon" href="/static/icons/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/icons/favicon-32x32.png">
    <link rel="apple-touch-icon" sizes="192x192" href="/static/icons/scitex-icon.png">
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
    <style>
        /* STYLES_PLACEHOLDER */
    </style>
</head>
<body>
    <div class="spinner-overlay"><div class="spinner-container"><div class="spinner"></div><div class="spinner-text">Loading...</div></div></div>
    <div class="editor-container">
        <!-- FILE_BROWSER_PLACEHOLDER -->
        <!-- Preview Panel -->
        <div class="preview-panel" id="preview-panel">
            <div class="preview-header">
                <button id="btn-collapse-preview" class="btn-collapse" title="Collapse canvas">&#x276F;</button>
                <span class="panel-label">CANVAS</span>
                <div class="preview-controls">
                    <div class="download-dropdown">
                        <button id="btn-download-main" class="btn-primary download-main" title="Download as PNG">Download PNG</button>
                        <button id="btn-download-toggle" class="btn-primary download-toggle" title="More formats">▼</button>
                        <div id="download-menu" class="download-menu">
                            <button id="btn-download-png-menu" class="download-option active" data-format="png">PNG</button>
                            <button id="btn-download-svg-menu" class="download-option" data-format="svg">SVG</button>
                            <button id="btn-download-pdf-menu" class="download-option" data-format="pdf">PDF</button>
                            <hr style="margin: 4px 0; border: none; border-top: 1px solid #ddd;">
                            <button id="btn-download-csv-menu" class="download-option" data-format="csv" title="Export plot data as CSV">CSV (Data)</button>
                        </div>
                    </div>
                    <button id="btn-refresh" title="Re-render figure (R)">Render</button>
                    <div class="zoom-controls">
                        <select id="zoom-select" title="Zoom level (+/- or scroll)">
                            <option value="25">25%</option>
                            <option value="50">50%</option>
                            <option value="75">75%</option>
                            <option value="100" selected>100%</option>
                            <option value="125">125%</option>
                            <option value="150">150%</option>
                            <option value="200">200%</option>
                        </select>
                        <button id="btn-zoom-fit" title="Fit to view (F)">Fit</button>
                    </div>
                    <button id="btn-ruler-grid" class="btn-ruler" title="Toggle rulers and grid (G)">Grid</button>
                    <button id="dark-mode-toggle" class="btn-theme" title="Toggle theme (D)">🌙</button>
                    <div class="toolbar-separator"></div>
                    <button id="btn-undo" class="btn-icon" title="Undo (Ctrl+Z)" disabled>↶</button>
                    <button id="btn-redo" class="btn-icon" title="Redo (Ctrl+Y)" disabled>↷</button>
                    <button id="btn-restore" class="btn-secondary" title="Revert all changes">Revert</button>
                    <button id="btn-save" class="btn-primary" title="Save (Ctrl+S)">Save</button>
                    <button id="btn-shortcuts" class="btn-icon btn-shortcuts" title="Keyboard shortcuts (?)">⌨</button>
                </div>
            </div>
            <div class="preview-wrapper" id="preview-wrapper">
                <div class="zoom-container" id="zoom-container">
                    <img id="preview-image" src="data:image/png;base64,IMAGE_BASE64_PLACEHOLDER" alt="Figure preview">
                    <svg id="hitregion-overlay" class="hitregion-overlay"></svg>
                    <svg id="selection-overlay" class="selection-overlay"></svg>
                    <svg id="ruler-overlay" class="ruler-overlay"></svg>
                    <svg id="grid-overlay" class="grid-overlay"></svg>
                    <svg id="column-overlay" class="column-overlay"></svg>
                    <canvas id="hitmap-canvas" style="display: none;"></canvas>
                </div>
                <!-- Welcome overlay -->
                <div id="welcome-overlay" class="welcome-overlay" style="display: WELCOME_DISPLAY_PLACEHOLDER;"><div class="welcome-content"><h2>Getting Started</h2><div class="welcome-steps"><div class="welcome-step"><span class="step-number">1</span><span class="step-text">Drop CSV/TSV in <strong>Data</strong></span></div><div class="welcome-step"><span class="step-number">2</span><span class="step-text">Click <strong>Plot</strong></span></div><div class="welcome-step"><span class="step-number">3</span><span class="step-text">Adjust in <strong>Properties</strong></span></div></div><p class="welcome-hint">Or load .yaml from Files</p></div></div>
            </div>
            <!-- Caption Pane (below canvas) -->
            <div class="caption-pane" id="caption-pane">
                <span id="canvas-caption-text"><b>Fig. 1.</b></span>
            </div>
        </div>

        <!-- Controls Panel -->
        <div class="controls-panel" id="controls-panel">
            <div class="controls-header">
                <div class="header-title">
                    <button id="btn-collapse-properties" class="btn-collapse" title="Collapse panel">&#x276F;</button>
                    <span>PROPERTIES</span>
                </div>
            </div>
            <div class="style-info">
                <span class="style-label">Theme:</span>
                <select id="theme-selector" class="theme-selector" title="Switch theme preset">
                    <option value="SCITEX">SCITEX</option>
                    <option value="MATPLOTLIB">MATPLOTLIB</option>
                </select>
                <label class="checkbox-inline" title="Transparent background">
                    <input type="checkbox" id="output_transparent" checked>
                    <span>Transparent</span>
                </label>
            </div>
            <!-- Theme Modal -->
            <div id="theme-modal" class="modal" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Theme: <span id="theme-modal-name">SCITEX</span></h3>
                        <button id="theme-modal-close" class="modal-close">&times;</button>
                    </div>
                    <pre id="theme-content" class="theme-content-pre"></pre>
                    <div class="modal-footer">
                        <button id="theme-modal-download" class="btn-primary">Download YAML</button>
                        <button id="theme-modal-copy" class="btn-secondary">Copy to Clipboard</button>
                    </div>
                </div>
            </div>
            <!-- Shortcuts Modal -->
            <div id="shortcuts-modal" class="modal" style="display: none;">
                <div class="modal-content shortcuts-modal-content">
                    <div class="modal-header">
                        <h3>Keyboard Shortcuts</h3>
                        <button id="shortcuts-modal-close" class="modal-close">&times;</button>
                    </div>
                    <div class="shortcuts-content">
                        <div class="shortcut-section"><h4>General</h4>
                            <div class="shortcut-row"><span class="shortcut-keys"><kbd>Ctrl</kbd>+<kbd>Z</kbd>/<kbd>Shift+Z</kbd></span><span class="shortcut-desc">Undo/Redo</span></div>
                            <div class="shortcut-row"><span class="shortcut-keys"><kbd>Ctrl</kbd>+<kbd>S</kbd>/<kbd>Shift+S</kbd></span><span class="shortcut-desc">Save/Download</span></div>
                            <div class="shortcut-row"><span class="shortcut-keys"><kbd>F5</kbd>/<kbd>Esc</kbd>/<kbd>R</kbd></span><span class="shortcut-desc">Refresh/Clear/Reset</span></div></div>
                        <div class="shortcut-section"><h4>Navigation</h4>
                            <div class="shortcut-row"><span class="shortcut-keys"><kbd>1</kbd>/<kbd>2</kbd>/<kbd>3</kbd></span><span class="shortcut-desc">Figure/Axis/Element tab</span></div></div>
                        <div class="shortcut-section"><h4>View</h4>
                            <div class="shortcut-row"><span class="shortcut-keys"><kbd>G</kbd>/<kbd>+</kbd>/<kbd>-</kbd>/<kbd>0</kbd>/<kbd>F</kbd></span><span class="shortcut-desc">Grid/Zoom/Reset/Fit</span></div></div>
                        <div class="shortcut-section"><h4>Panel</h4>
                            <div class="shortcut-row"><span class="shortcut-keys">Drag/<kbd>Alt</kbd>+Drag</span><span class="shortcut-desc">Move (snap/free)</span></div></div>
                        DEBUG_SHORTCUTS_PLACEHOLDER
                    </div>
                </div>
            </div>
            <div id="override-status" class="override-status" style="display: none;">
                <span class="override-indicator">Modified</span>
                <span id="override-timestamp" class="override-timestamp"></span>
            </div>

            <div class="controls-sections">
                <!-- Tab Navigation -->
                <div class="tab-navigation">
                    <button id="tab-figure" class="tab-btn active" title="Figure-level properties">Figure</button>
                    <button id="tab-axis" class="tab-btn" title="Axis-level properties">Axis</button>
                    <button id="tab-element" class="tab-btn" title="Element-specific properties">Element</button>
                </div>

                <!-- FIGURE TAB -->
                <div id="tab-content-figure" class="tab-content active">
                    <!-- Dimensions Section -->
                    <details class="section">
                        <summary>Dimensions</summary>
                        <div class="section-content">
                            <div class="subsection">
                                <h4>Margins</h4>
                                <div class="form-grid">
                                    <div class="form-row">
                                        <label>Left</label>
                                        <input type="number" id="margins_left_mm" step="1" min="0" max="50" placeholder="1">
                                    </div>
                                    <div class="form-row">
                                        <label>Right</label>
                                        <input type="number" id="margins_right_mm" step="1" min="0" max="50" placeholder="1">
                                    </div>
                                    <div class="form-row">
                                        <label>Bottom</label>
                                        <input type="number" id="margins_bottom_mm" step="1" min="0" max="50" placeholder="1">
                                    </div>
                                    <div class="form-row">
                                        <label>Top</label>
                                        <input type="number" id="margins_top_mm" step="1" min="0" max="50" placeholder="1">
                                    </div>
                                </div>
                            </div>
                            <div class="subsection">
                                <h4>Spacing</h4>
                                <div class="form-row">
                                    <label>Horizontal (mm)</label>
                                    <input type="number" id="spacing_horizontal_mm" step="1" min="0" max="30" placeholder="8">
                                </div>
                                <div class="form-row">
                                    <label>Vertical (mm)</label>
                                    <input type="number" id="spacing_vertical_mm" step="1" min="0" max="30" placeholder="8">
                                </div>
                            </div>
                        </div>
                    </details>

                    <!-- Output Section -->
                    <details class="section">
                        <summary>Output</summary>
                        <div class="section-content">
                            <div class="form-row"><label>DPI</label><input type="number" id="output_dpi" step="50" min="72" max="600"></div>
                            <div class="form-row"><label>Transparent</label><input type="checkbox" id="output_transparent"></div>
                        </div>
                    </details>
                    <!-- Figure Caption (Scientific) -->
                    <details class="section">
                        <summary>Figure Caption</summary>
                        <div class="section-content">
                            <div class="form-row"><label>Fig. #</label><input type="number" id="caption_figure_number" min="1" max="99" step="1" value="1" style="width:60px"></div>
                            <div class="form-row caption-row"><label>Caption</label><textarea id="caption_figure_text" class="caption-textarea" rows="2" placeholder="e.g., Comparison of sin and cos functions"></textarea></div>
                            <div class="composed-caption-preview" id="composed-caption-container">
                                <div class="composed-caption-label">Composed Caption:</div>
                                <div class="composed-caption-text" id="composed-caption-text"><b>Fig. 1.</b></div>
                            </div>
                        </div>
                    </details>
                </div>

                <!-- AXIS TAB -->
                <div id="tab-content-axis" class="tab-content">
                    <div class="tab-hint" id="axis-tab-hint">Select an axis element (title, label, ticks, legend) to edit</div>

                    <!-- Panel Position Section -->
                    <details class="section">
                        <summary>Panel Position</summary>
                        <div class="section-content">
                            <div class="form-row panel-indicator-row">
                                <label>Panel</label>
                                <span id="current_panel_indicator" class="panel-indicator">Select an element</span>
                            </div>
                            <div class="position-grid">
                                <div class="form-row">
                                    <label>Left (mm)</label>
                                    <input type="number" id="panel_left" step="1" min="0" placeholder="20">
                                </div>
                                <div class="form-row">
                                    <label>Top (mm)</label>
                                    <input type="number" id="panel_top" step="1" min="0" placeholder="15">
                                </div>
                                <div class="form-row">
                                    <label>Width (mm)</label>
                                    <input type="number" id="panel_width" step="1" min="0" placeholder="120">
                                </div>
                                <div class="form-row">
                                    <label>Height (mm)</label>
                                    <input type="number" id="panel_height" step="1" min="0" placeholder="90">
                                </div>
                            </div>
                            <div class="form-row" style="margin-top: 8px;">
                                <button id="apply_panel_position" class="btn-small">Apply Position</button>
                            </div>
                        </div>
                    </details>

                    <!-- Axes Size Section -->
                    <details class="section">
                        <summary>Axes Size</summary>
                        <div class="section-content">
                            <div class="form-row">
                                <label>Width (mm)</label>
                                <input type="number" id="axes_width_mm" step="1" min="10" max="200" placeholder="80">
                            </div>
                            <div class="form-row">
                                <label>Height (mm)</label>
                                <input type="number" id="axes_height_mm" step="1" min="10" max="200" placeholder="55">
                            </div>
                        </div>
                    </details>

                    <!-- Labels Section -->
                    <details class="section">
                        <summary>Labels</summary>
                        <div class="section-content">
                            <div class="form-row"><label>Title</label><input type="text" id="label_title" class="label-input" placeholder="(no title)"></div>
                            <div class="form-row"><label>X Label</label><input type="text" id="label_xlabel" class="label-input" placeholder="(no xlabel)"></div>
                            <div class="form-row"><label>Y Label</label><input type="text" id="label_ylabel" class="label-input" placeholder="(no ylabel)"></div>
                            <div class="form-row"><label>Suptitle</label><input type="text" id="label_suptitle" class="label-input" placeholder="(no suptitle)"></div>
                        </div>
                    </details>

                    <!-- Caption Section -->
                    <details class="section">
                        <summary>Caption</summary>
                        <div class="section-content">
                            <div class="form-row caption-row">
                                <label>Panel</label>
                                <textarea id="caption_panel_text" class="caption-textarea" rows="2" placeholder="e.g., Line plot showing sinusoidal functions"></textarea>
                            </div>
                            <div class="form-row caption-row">
                                <label>Figure</label>
                                <textarea id="caption_figure_text" class="caption-textarea" rows="3" placeholder="e.g., Overview of visualization methods..."></textarea>
                            </div>
                        </div>
                    </details>

                    <!-- Axis Type Section -->
                    <details class="section">
                        <summary>Axis Type</summary>
                        <div class="section-content">
                            <div class="form-row">
                                <label>X Axis</label>
                                <div class="axis-type-toggle">
                                    <button id="xaxis-numerical" class="axis-type-btn active" data-axis="x" data-type="numerical">Numerical</button>
                                    <button id="xaxis-categorical" class="axis-type-btn" data-axis="x" data-type="categorical">Categorical</button>
                                </div>
                            </div>
                            <div class="form-row">
                                <label>Y Axis</label>
                                <div class="axis-type-toggle">
                                    <button id="yaxis-numerical" class="axis-type-btn active" data-axis="y" data-type="numerical">Numerical</button>
                                    <button id="yaxis-categorical" class="axis-type-btn" data-axis="y" data-type="categorical">Categorical</button>
                                </div>
                            </div>
                            <div class="form-row" id="xaxis-labels-row" style="display: none;">
                                <label>X Labels</label>
                                <input type="text" id="xaxis_labels" class="label-input" placeholder="label1, label2, ...">
                            </div>
                            <div class="form-row" id="yaxis-labels-row" style="display: none;">
                                <label>Y Labels</label>
                                <input type="text" id="yaxis_labels" class="label-input" placeholder="label1, label2, ...">
                            </div>
                        </div>
                    </details>

                    <!-- Fonts Section -->
                    <details class="section">
                        <summary>Fonts</summary>
                        <div class="section-content">
                            <div class="form-row">
                                <label>Family</label>
                                <select id="fonts_family">
                                    <option value="Arial">Arial</option>
                                    <option value="DejaVu Sans">DejaVu Sans</option>
                                    <option value="Helvetica">Helvetica</option>
                                    <option value="Times New Roman">Times New Roman</option>
                                    <option value="sans-serif">sans-serif</option>
                                    <option value="serif">serif</option>
                                </select>
                            </div>
                            <div class="form-row">
                                <label>Axis Label (pt)</label>
                                <input type="number" id="fonts_axis_label_pt" step="0.5" min="4" max="24">
                            </div>
                            <div class="form-row">
                                <label>Tick Label (pt)</label>
                                <input type="number" id="fonts_tick_label_pt" step="0.5" min="4" max="24">
                            </div>
                            <div class="form-row">
                                <label>Title (pt)</label>
                                <input type="number" id="fonts_title_pt" step="0.5" min="4" max="24">
                            </div>
                            <div class="form-row">
                                <label>Suptitle (pt)</label>
                                <input type="number" id="fonts_suptitle_pt" step="0.5" min="4" max="30">
                            </div>
                            <div class="form-row">
                                <label>Legend (pt)</label>
                                <input type="number" id="fonts_legend_pt" step="0.5" min="4" max="24">
                            </div>
                        </div>
                    </details>

                    <!-- Ticks Section -->
                    <details class="section">
                        <summary>Ticks</summary>
                        <div class="section-content">
                            <div class="form-row">
                                <label>Length (mm)</label>
                                <input type="number" id="ticks_length_mm" step="0.1" min="0.5" max="5">
                            </div>
                            <div class="form-row">
                                <label>Thickness (mm)</label>
                                <input type="number" id="ticks_thickness_mm" step="0.05" min="0.1" max="2">
                            </div>
                            <div class="form-row">
                                <label>Direction</label>
                                <select id="ticks_direction">
                                    <option value="out">Out</option>
                                    <option value="in">In</option>
                                    <option value="inout">Both</option>
                                </select>
                            </div>
                            <div class="form-row">
                                <label>N Ticks</label>
                                <input type="number" id="ticks_n_ticks" step="1" min="2" max="20">
                            </div>
                        </div>
                    </details>

                    <!-- Spines Section -->
                    <details class="section">
                        <summary>Spines</summary>
                        <div class="section-content">
                            <div class="form-row">
                                <label>Thickness (mm)</label>
                                <input type="number" id="axes_thickness_mm" step="0.05" min="0.1" max="2" placeholder="0.35">
                            </div>
                            <div class="spine-visibility-grid">
                                <div class="form-row"><label>Hide Top</label><input type="checkbox" id="behavior_hide_top_spine"></div>
                                <div class="form-row"><label>Hide Right</label><input type="checkbox" id="behavior_hide_right_spine"></div>
                                <div class="form-row"><label>Hide Bottom</label><input type="checkbox" id="behavior_hide_bottom_spine"></div>
                                <div class="form-row"><label>Hide Left</label><input type="checkbox" id="behavior_hide_left_spine"></div>
                            </div>
                            <div class="form-row">
                                <label>Grid</label>
                                <input type="checkbox" id="behavior_grid">
                            </div>
                        </div>
                    </details>

                    <!-- Legend Section -->
                    <details class="section">
                        <summary>Legend</summary>
                        <div class="section-content">
                            <div class="form-row">
                                <label>Visible</label>
                                <input type="checkbox" id="legend_visible" checked>
                            </div>
                            <div class="form-row">
                                <label>Show Frame</label>
                                <input type="checkbox" id="legend_frameon">
                            </div>
                            <div class="form-row">
                                <label>Location</label>
                                <select id="legend_loc">
                                    <option value="best">Best</option>
                                    <option value="upper right">Upper Right</option>
                                    <option value="upper left">Upper Left</option>
                                    <option value="lower right">Lower Right</option>
                                    <option value="lower left">Lower Left</option>
                                    <option value="center">Center</option>
                                    <option value="center left">Center Left</option>
                                    <option value="center right">Center Right</option>
                                    <option value="lower center">Lower Center</option>
                                    <option value="upper center">Upper Center</option>
                                    <option value="custom">Custom (xy)</option>
                                </select>
                            </div>
                            <div id="legend-custom-pos" class="legend-custom-pos" style="display: none;">
                                <div class="form-row">
                                    <label>X (0-1)</label>
                                    <input type="number" id="legend_x" step="0.05" min="0" max="1.5" value="1.02" placeholder="1.02">
                                </div>
                                <div class="form-row">
                                    <label>Y (0-1)</label>
                                    <input type="number" id="legend_y" step="0.05" min="0" max="1.5" value="1" placeholder="1">
                                </div>
                                <div class="form-hint">Coordinates are relative to axes (0-1). Values >1 place legend outside.</div>
                            </div>
                            <div class="form-row">
                                <label>Alpha</label>
                                <input type="range" id="legend_alpha" min="0" max="1" step="0.1">
                                <span id="legend_alpha_value">0.8</span>
                            </div>
                            <div class="form-row">
                                <label>Background</label>
                                <input type="color" id="legend_bg" value="#ffffff">
                            </div>
                        </div>
                    </details>
                </div>

                <!-- ELEMENT TAB -->
                <div id="tab-content-element" class="tab-content">
                    <div class="tab-hint" id="element-tab-hint">
                        <p>Select a plot element to edit its properties</p>
                        <p class="hint-sub">Click on lines, scatter, bars, etc. in the preview</p>
                    </div>

                    <!-- Selected element info -->
                    <div id="selected-element-panel" style="display: none;">
                        <div class="selected-element-header">
                            <span class="element-type-badge" id="element-type-badge">line</span>
                            <span class="element-name" id="element-name">element</span>
                        </div>
                    </div>

                    <!-- Dynamic call properties (populated when element selected) -->
                    <div id="dynamic-call-properties" class="dynamic-call-properties"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initial data from server
        const initialBboxes = BBOXES_PLACEHOLDER;
        const initialColorMap = COLOR_MAP_PLACEHOLDER;
        const initialValues = INITIAL_VALUES_PLACEHOLDER;
        const imgWidth = IMG_WIDTH_PLACEHOLDER;
        const imgHeight = IMG_HEIGHT_PLACEHOLDER;

        /* SCRIPTS_PLACEHOLDER */
    </script>
</body>
</html>
"""

__all__ = ["HTML_TEMPLATE"]
