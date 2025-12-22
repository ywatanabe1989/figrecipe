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
                    <button id="btn-refresh" title="Refresh preview">Refresh</button>
                    <button id="btn-show-hitmap" title="Toggle hitmap overlay for debugging">Show Hit Regions</button>
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
                <h2>Style Properties</h2>
                <div class="controls-actions">
                    <button id="btn-restore" class="btn-warning" title="Restore to original programmatic style">Restore</button>
                    <button id="btn-reset" class="btn-secondary" title="Reset to last saved">Reset</button>
                    <button id="btn-save" class="btn-primary">Save</button>
                </div>
            </div>
            <div id="override-status" class="override-status" style="display: none;">
                <span class="override-indicator">Manual overrides active</span>
                <span id="override-timestamp" class="override-timestamp"></span>
            </div>

            <div class="controls-sections">
                <!-- Dimensions Section -->
                <details class="section" id="section-dimensions" open>
                    <summary>Dimensions</summary>
                    <div class="section-content">
                        <div class="subsection">
                            <h4>Axes</h4>
                            <div class="form-row">
                                <label>Width (mm)</label>
                                <input type="number" id="axes_width_mm" step="1" min="10" max="200">
                            </div>
                            <div class="form-row">
                                <label>Height (mm)</label>
                                <input type="number" id="axes_height_mm" step="1" min="10" max="200">
                            </div>
                            <div class="form-row">
                                <label>Thickness (mm)</label>
                                <input type="number" id="axes_thickness_mm" step="0.05" min="0.1" max="2">
                            </div>
                        </div>
                        <div class="subsection">
                            <h4>Margins</h4>
                            <div class="form-grid">
                                <div class="form-row">
                                    <label>Left</label>
                                    <input type="number" id="margins_left_mm" step="1" min="0" max="50">
                                </div>
                                <div class="form-row">
                                    <label>Right</label>
                                    <input type="number" id="margins_right_mm" step="1" min="0" max="50">
                                </div>
                                <div class="form-row">
                                    <label>Bottom</label>
                                    <input type="number" id="margins_bottom_mm" step="1" min="0" max="50">
                                </div>
                                <div class="form-row">
                                    <label>Top</label>
                                    <input type="number" id="margins_top_mm" step="1" min="0" max="50">
                                </div>
                            </div>
                        </div>
                        <div class="subsection">
                            <h4>Spacing</h4>
                            <div class="form-row">
                                <label>Horizontal (mm)</label>
                                <input type="number" id="spacing_horizontal_mm" step="1" min="0" max="30">
                            </div>
                            <div class="form-row">
                                <label>Vertical (mm)</label>
                                <input type="number" id="spacing_vertical_mm" step="1" min="0" max="30">
                            </div>
                        </div>
                    </div>
                </details>

                <!-- Fonts Section -->
                <details class="section" id="section-fonts">
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
                        <div class="form-row">
                            <label>Annotation (pt)</label>
                            <input type="number" id="fonts_annotation_pt" step="0.5" min="4" max="24">
                        </div>
                    </div>
                </details>

                <!-- Lines & Markers Section -->
                <details class="section" id="section-lines">
                    <summary>Lines & Markers</summary>
                    <div class="section-content">
                        <div class="subsection">
                            <h4>Lines</h4>
                            <div class="form-row">
                                <label>Trace (mm)</label>
                                <input type="number" id="lines_trace_mm" step="0.05" min="0.1" max="3">
                            </div>
                            <div class="form-row">
                                <label>Errorbar (mm)</label>
                                <input type="number" id="lines_errorbar_mm" step="0.05" min="0.1" max="3">
                            </div>
                            <div class="form-row">
                                <label>Errorbar Cap (mm)</label>
                                <input type="number" id="lines_errorbar_cap_mm" step="0.1" min="0" max="5">
                            </div>
                        </div>
                        <div class="subsection">
                            <h4>Markers</h4>
                            <div class="form-row">
                                <label>Size (mm)</label>
                                <input type="number" id="markers_size_mm" step="0.1" min="0.5" max="10">
                            </div>
                            <div class="form-row">
                                <label>Scatter (mm)</label>
                                <input type="number" id="markers_scatter_mm" step="0.1" min="0.5" max="10">
                            </div>
                            <div class="form-row">
                                <label>Edge Width (mm)</label>
                                <input type="number" id="markers_edge_width_mm" step="0.05" min="0" max="2">
                            </div>
                        </div>
                    </div>
                </details>

                <!-- Ticks Section -->
                <details class="section" id="section-ticks">
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

                <!-- Legend Section -->
                <details class="section" id="section-legend">
                    <summary>Legend</summary>
                    <div class="section-content">
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
                            </select>
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
                        <div class="form-row">
                            <label>Edge Color</label>
                            <input type="color" id="legend_edgecolor" value="#cccccc">
                        </div>
                    </div>
                </details>

                <!-- Behavior Section -->
                <details class="section" id="section-behavior">
                    <summary>Behavior</summary>
                    <div class="section-content">
                        <div class="form-row">
                            <label>Grid</label>
                            <input type="checkbox" id="behavior_grid">
                        </div>
                        <div class="form-row">
                            <label>Hide Top Spine</label>
                            <input type="checkbox" id="behavior_hide_top_spine">
                        </div>
                        <div class="form-row">
                            <label>Hide Right Spine</label>
                            <input type="checkbox" id="behavior_hide_right_spine">
                        </div>
                        <div class="form-row">
                            <label>Auto Scale Axes</label>
                            <input type="checkbox" id="behavior_auto_scale_axes">
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
                        <div class="form-row">
                            <label>Format</label>
                            <select id="output_format">
                                <option value="png">PNG</option>
                                <option value="svg">SVG</option>
                                <option value="pdf">PDF</option>
                            </select>
                        </div>
                    </div>
                </details>

                <!-- Download Section -->
                <details class="section" open>
                    <summary>Download</summary>
                    <div class="section-content">
                        <div class="download-buttons">
                            <button id="btn-download-png">PNG</button>
                            <button id="btn-download-svg">SVG</button>
                            <button id="btn-download-pdf">PDF</button>
                        </div>
                    </div>
                </details>
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

__all__ = ['HTML_TEMPLATE']
