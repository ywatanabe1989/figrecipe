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
                <span class="style-label">Applied Theme:</span>
                <span id="style-name" class="style-name">STYLE_NAME_PLACEHOLDER</span>
            </div>
            <div id="override-status" class="override-status" style="display: none;">
                <span class="override-indicator">Manual overrides active</span>
                <span id="override-timestamp" class="override-timestamp"></span>
            </div>

            <div class="controls-sections">
                <!-- Mode toggle -->
                <div class="view-mode-toggle">
                    <button id="btn-show-all" class="btn-toggle active" title="Show all properties">General</button>
                    <button id="btn-show-selected" class="btn-toggle" title="Show only properties for selected element">Selected</button>
                    <span class="selection-hint" id="selection-hint">Click an element to filter</span>
                </div>

                <!-- Dynamic call properties (shown when element selected) -->
                <div id="dynamic-call-properties" class="dynamic-call-properties" style="display: none;"></div>

                <!-- Dimensions Section - applies to axes, spine -->
                <details class="section" id="section-dimensions" data-element-types="axes,spine" open>
                    <summary>Dimensions</summary>
                    <div class="section-content">
                        <div class="subsection">
                            <h4>Axes</h4>
                            <div class="form-row" data-element-types="axes,spine">
                                <label>Width (mm)</label>
                                <input type="number" id="axes_width_mm" step="1" min="10" max="200" placeholder="80">
                            </div>
                            <div class="form-row" data-element-types="axes,spine">
                                <label>Height (mm)</label>
                                <input type="number" id="axes_height_mm" step="1" min="10" max="200" placeholder="55">
                            </div>
                            <div class="form-row" data-element-types="axes,spine">
                                <label>Thickness (mm)</label>
                                <input type="number" id="axes_thickness_mm" step="0.05" min="0.1" max="2" placeholder="0.35">
                            </div>
                        </div>
                        <div class="subsection">
                            <h4>Margins</h4>
                            <div class="form-grid">
                                <div class="form-row" data-element-types="axes">
                                    <label>Left</label>
                                    <input type="number" id="margins_left_mm" step="1" min="0" max="50" placeholder="12">
                                </div>
                                <div class="form-row" data-element-types="axes">
                                    <label>Right</label>
                                    <input type="number" id="margins_right_mm" step="1" min="0" max="50" placeholder="3">
                                </div>
                                <div class="form-row" data-element-types="axes">
                                    <label>Bottom</label>
                                    <input type="number" id="margins_bottom_mm" step="1" min="0" max="50" placeholder="10">
                                </div>
                                <div class="form-row" data-element-types="axes">
                                    <label>Top</label>
                                    <input type="number" id="margins_top_mm" step="1" min="0" max="50" placeholder="6">
                                </div>
                            </div>
                        </div>
                        <div class="subsection">
                            <h4>Spacing</h4>
                            <div class="form-row" data-element-types="axes">
                                <label>Horizontal (mm)</label>
                                <input type="number" id="spacing_horizontal_mm" step="1" min="0" max="30" placeholder="8">
                            </div>
                            <div class="form-row" data-element-types="axes">
                                <label>Vertical (mm)</label>
                                <input type="number" id="spacing_vertical_mm" step="1" min="0" max="30" placeholder="8">
                            </div>
                        </div>
                    </div>
                </details>

                <!-- Fonts Section - applies to title, xlabel, ylabel, xticks, yticks, legend -->
                <details class="section" id="section-fonts" data-element-types="title,xlabel,ylabel,xticks,yticks,legend">
                    <summary>Fonts</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="title,xlabel,ylabel,xticks,yticks,legend">
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
                        <div class="form-row" data-element-types="xlabel,ylabel">
                            <label>Axis Label (pt)</label>
                            <input type="number" id="fonts_axis_label_pt" step="0.5" min="4" max="24">
                        </div>
                        <div class="form-row" data-element-types="xticks,yticks">
                            <label>Tick Label (pt)</label>
                            <input type="number" id="fonts_tick_label_pt" step="0.5" min="4" max="24">
                        </div>
                        <div class="form-row" data-element-types="title">
                            <label>Title (pt)</label>
                            <input type="number" id="fonts_title_pt" step="0.5" min="4" max="24">
                        </div>
                        <div class="form-row" data-element-types="title">
                            <label>Suptitle (pt)</label>
                            <input type="number" id="fonts_suptitle_pt" step="0.5" min="4" max="30">
                        </div>
                        <div class="form-row" data-element-types="legend">
                            <label>Legend (pt)</label>
                            <input type="number" id="fonts_legend_pt" step="0.5" min="4" max="24">
                        </div>
                        <div class="form-row" data-element-types="title,xlabel,ylabel">
                            <label>Annotation (pt)</label>
                            <input type="number" id="fonts_annotation_pt" step="0.5" min="4" max="24">
                        </div>
                    </div>
                </details>

                <!-- Lines Section - applies to line, bar, fill -->
                <details class="section" id="section-lines" data-element-types="line,bar,fill">
                    <summary>Lines</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="line,bar,fill">
                            <label>Trace (mm)</label>
                            <input type="number" id="lines_trace_mm" step="0.05" min="0.1" max="3">
                        </div>
                        <div class="form-row" data-element-types="line">
                            <label>Errorbar (mm)</label>
                            <input type="number" id="lines_errorbar_mm" step="0.05" min="0.1" max="3">
                        </div>
                        <div class="form-row" data-element-types="line">
                            <label>Errorbar Cap (mm)</label>
                            <input type="number" id="lines_errorbar_cap_mm" step="0.1" min="0" max="5">
                        </div>
                    </div>
                </details>

                <!-- Markers Section - applies to scatter, line (with markers) -->
                <details class="section" id="section-markers" data-element-types="scatter,line">
                    <summary>Markers</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="line">
                            <label>Size (mm)</label>
                            <input type="number" id="markers_size_mm" step="0.1" min="0.5" max="10">
                        </div>
                        <div class="form-row" data-element-types="scatter">
                            <label>Scatter (mm)</label>
                            <input type="number" id="markers_scatter_mm" step="0.1" min="0.5" max="10">
                        </div>
                        <div class="form-row" data-element-types="scatter,line">
                            <label>Edge Width (mm)</label>
                            <input type="number" id="markers_edge_width_mm" step="0.05" min="0" max="2">
                        </div>
                    </div>
                </details>

                <!-- Ticks Section - applies to xticks, yticks -->
                <details class="section" id="section-ticks" data-element-types="xticks,yticks">
                    <summary>Ticks</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="xticks,yticks">
                            <label>Length (mm)</label>
                            <input type="number" id="ticks_length_mm" step="0.1" min="0.5" max="5">
                        </div>
                        <div class="form-row" data-element-types="xticks,yticks">
                            <label>Thickness (mm)</label>
                            <input type="number" id="ticks_thickness_mm" step="0.05" min="0.1" max="2">
                        </div>
                        <div class="form-row" data-element-types="xticks,yticks">
                            <label>Direction</label>
                            <select id="ticks_direction">
                                <option value="out">Out</option>
                                <option value="in">In</option>
                                <option value="inout">Both</option>
                            </select>
                        </div>
                        <div class="form-row" data-element-types="xticks,yticks">
                            <label>N Ticks</label>
                            <input type="number" id="ticks_n_ticks" step="1" min="2" max="20">
                        </div>
                    </div>
                </details>

                <!-- Legend Section - applies to legend -->
                <details class="section" id="section-legend" data-element-types="legend">
                    <summary>Legend</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="legend">
                            <label>Show Frame</label>
                            <input type="checkbox" id="legend_frameon">
                        </div>
                        <div class="form-row" data-element-types="legend">
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
                        <div class="form-row" data-element-types="legend">
                            <label>Alpha</label>
                            <input type="range" id="legend_alpha" min="0" max="1" step="0.1">
                            <span id="legend_alpha_value">0.8</span>
                        </div>
                        <div class="form-row" data-element-types="legend">
                            <label>Background</label>
                            <input type="color" id="legend_bg" value="#ffffff">
                        </div>
                        <div class="form-row" data-element-types="legend">
                            <label>Edge Color</label>
                            <input type="color" id="legend_edgecolor" value="#cccccc">
                        </div>
                    </div>
                </details>

                <!-- Boxplot Section - applies to boxplot -->
                <details class="section" id="section-boxplot" data-element-types="boxplot">
                    <summary>Boxplot</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="boxplot">
                            <label>Line Width (mm)</label>
                            <input type="number" id="lines_trace_mm" step="0.05" min="0.1" max="3">
                        </div>
                        <div class="form-row" data-element-types="boxplot">
                            <label>Flier Size (mm)</label>
                            <input type="number" id="markers_flier_mm" step="0.1" min="0.1" max="5">
                        </div>
                        <div class="form-row" data-element-types="boxplot">
                            <label>Median Color</label>
                            <input type="color" id="boxplot_median_color" value="#000000">
                        </div>
                    </div>
                </details>

                <!-- Violin Section - applies to violin -->
                <details class="section" id="section-violin" data-element-types="violin">
                    <summary>Violin</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="violin">
                            <label>Line Width (mm)</label>
                            <input type="number" id="lines_trace_mm" step="0.05" min="0.1" max="3">
                        </div>
                    </div>
                </details>

                <!-- Behavior Section - global -->
                <details class="section" id="section-behavior" data-element-types="axes,spine">
                    <summary>Behavior</summary>
                    <div class="section-content">
                        <div class="form-row" data-element-types="axes">
                            <label>Grid</label>
                            <input type="checkbox" id="behavior_grid">
                        </div>
                        <div class="form-row" data-element-types="spine">
                            <label>Hide Top Spine</label>
                            <input type="checkbox" id="behavior_hide_top_spine">
                        </div>
                        <div class="form-row" data-element-types="spine">
                            <label>Hide Right Spine</label>
                            <input type="checkbox" id="behavior_hide_right_spine">
                        </div>
                        <div class="form-row" data-element-types="axes">
                            <label>Auto Scale Axes</label>
                            <input type="checkbox" id="behavior_auto_scale_axes">
                        </div>
                    </div>
                </details>

                <!-- Output Section - global, always visible -->
                <details class="section" id="section-output" data-element-types="global">
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

                <!-- Download Section - always visible -->
                <details class="section" id="section-download" data-element-types="global" open>
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

__all__ = ["HTML_TEMPLATE"]
