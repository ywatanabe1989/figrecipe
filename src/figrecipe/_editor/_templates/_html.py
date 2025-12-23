#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML template for figure editor.
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>figrecipe Editor</title>
    <style>
        /* STYLES_PLACEHOLDER */
    </style>
</head>
<body>
    <div class="editor-container">
        <!-- Preview Panel -->
        <div class="preview-panel">
            <div class="preview-header">
                <h2>Preview</h2>
                <div class="preview-controls">
                    <div class="download-dropdown">
                        <button id="btn-download-main" class="btn-primary download-main" title="Download as PNG">Download PNG</button>
                        <button id="btn-download-toggle" class="btn-primary download-toggle" title="More formats">▼</button>
                        <div id="download-menu" class="download-menu">
                            <button id="btn-download-png-menu" class="download-option active" data-format="png">PNG</button>
                            <button id="btn-download-svg-menu" class="download-option" data-format="svg">SVG</button>
                            <button id="btn-download-pdf-menu" class="download-option" data-format="pdf">PDF</button>
                        </div>
                    </div>
                    <button id="btn-refresh" title="Refresh preview">Refresh</button>
                    <button id="btn-show-hitmap" title="Toggle hitmap overlay for debugging" style="display: none;">Show Hit Regions</button>
                    <label class="theme-toggle">
                        <input type="checkbox" id="dark-mode-toggle">
                        <span>Dark Mode</span>
                    </label>
                </div>
            </div>
            <div class="preview-wrapper">
                <img id="preview-image" src="data:image/png;base64,IMAGE_BASE64_PLACEHOLDER" alt="Figure preview">
                <svg id="hitregion-overlay" class="hitregion-overlay"></svg>
                <svg id="selection-overlay" class="selection-overlay"></svg>
                <canvas id="hitmap-canvas" style="display: none;"></canvas>
            </div>
            <div class="selected-element-info" id="selected-info">
                Click on an element to select it
            </div>
        </div>

        <!-- Controls Panel -->
        <div class="controls-panel">
            <div class="controls-header">
                <h2>Properties</h2>
                <div class="controls-actions">
                    <button id="btn-restore" class="btn-warning" title="Restore to original programmatic style">Restore</button>
                    <button id="btn-reset" class="btn-secondary" title="Reset to last saved">Reset</button>
                    <button id="btn-save" class="btn-primary">Save</button>
                </div>
            </div>
            <div class="style-info">
                <span class="style-label">Theme:</span>
                <select id="theme-selector" class="theme-selector" title="Switch theme preset">
                    <option value="SCITEX">SCITEX</option>
                    <option value="MATPLOTLIB">MATPLOTLIB</option>
                </select>
                <div class="theme-actions">
                    <button id="btn-view-theme" class="btn-small" title="View theme contents">View</button>
                    <button id="btn-download-theme" class="btn-small" title="Download theme as YAML">Download</button>
                    <button id="btn-copy-theme" class="btn-small" title="Copy theme to clipboard">Copy</button>
                </div>
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
            <div id="override-status" class="override-status" style="display: none;">
                <span class="override-indicator">Manual overrides active</span>
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
                    <details class="section" open>
                        <summary>Dimensions</summary>
                        <div class="section-content">
                            <div class="subsection">
                                <h4>Margins</h4>
                                <div class="form-grid">
                                    <div class="form-row">
                                        <label>Left</label>
                                        <input type="number" id="margins_left_mm" step="1" min="0" max="50" placeholder="12">
                                    </div>
                                    <div class="form-row">
                                        <label>Right</label>
                                        <input type="number" id="margins_right_mm" step="1" min="0" max="50" placeholder="3">
                                    </div>
                                    <div class="form-row">
                                        <label>Bottom</label>
                                        <input type="number" id="margins_bottom_mm" step="1" min="0" max="50" placeholder="10">
                                    </div>
                                    <div class="form-row">
                                        <label>Top</label>
                                        <input type="number" id="margins_top_mm" step="1" min="0" max="50" placeholder="6">
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
                            <div class="form-row">
                                <label>DPI</label>
                                <input type="number" id="output_dpi" step="50" min="72" max="600">
                            </div>
                            <div class="form-row">
                                <label>Transparent</label>
                                <input type="checkbox" id="output_transparent">
                            </div>
                        </div>
                    </details>
                </div>

                <!-- AXIS TAB -->
                <div id="tab-content-axis" class="tab-content">
                    <div class="tab-hint" id="axis-tab-hint">Select an axis element (title, label, ticks, legend) to edit</div>

                    <!-- Axes Size Section -->
                    <details class="section" open>
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
                    <details class="section" open>
                        <summary>Labels</summary>
                        <div class="section-content">
                            <div class="form-row">
                                <label>Title</label>
                                <input type="text" id="label_title" class="label-input" placeholder="(no title)">
                            </div>
                            <div class="form-row">
                                <label>X Label</label>
                                <input type="text" id="label_xlabel" class="label-input" placeholder="(no xlabel)">
                            </div>
                            <div class="form-row">
                                <label>Y Label</label>
                                <input type="text" id="label_ylabel" class="label-input" placeholder="(no ylabel)">
                            </div>
                            <div class="form-row">
                                <label>Suptitle</label>
                                <input type="text" id="label_suptitle" class="label-input" placeholder="(no suptitle)">
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
                            <div class="form-row">
                                <label>Hide Top</label>
                                <input type="checkbox" id="behavior_hide_top_spine">
                            </div>
                            <div class="form-row">
                                <label>Hide Right</label>
                                <input type="checkbox" id="behavior_hide_right_spine">
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
