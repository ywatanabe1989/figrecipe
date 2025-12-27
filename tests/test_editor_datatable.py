#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for datatable functionality in the figrecipe editor.

These tests verify:
- Datatable CSS and JavaScript modules are properly included
- Datatable routes are registered and functional
- Data extraction from recorded figures works correctly
- CSV/JSON parsing works correctly
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestDatatableModules:
    """Test datatable module integration."""

    def test_datatable_styles_included(self):
        """Verify datatable styles are included in combined styles."""
        from figrecipe._editor._templates._styles import STYLES, STYLES_DATATABLE

        assert "datatable-panel" in STYLES_DATATABLE
        assert "datatable-table" in STYLES_DATATABLE
        assert STYLES_DATATABLE in STYLES

    def test_datatable_scripts_included(self):
        """Verify datatable scripts are included in combined scripts."""
        from figrecipe._editor._templates._scripts import SCRIPTS, SCRIPTS_DATATABLE

        assert "initDatatablePanel" in SCRIPTS_DATATABLE
        assert "toggleColumnSelection" in SCRIPTS_DATATABLE
        assert "plotFromVarAssignments" in SCRIPTS_DATATABLE
        assert SCRIPTS_DATATABLE in SCRIPTS

    def test_datatable_html_panel_exists(self):
        """Verify datatable HTML panel is properly defined."""
        from figrecipe._editor._templates._html_datatable import HTML_DATATABLE_PANEL

        assert "datatable-panel" in HTML_DATATABLE_PANEL
        assert "datatable-dropzone" in HTML_DATATABLE_PANEL
        assert "datatable-toggle" in HTML_DATATABLE_PANEL


class TestDatatableScriptIntegrity:
    """Test datatable JavaScript code integrity."""

    def test_no_obvious_js_errors(self):
        """Check for obvious JavaScript errors in datatable script."""
        from figrecipe._editor._templates._scripts import SCRIPTS_DATATABLE

        assert len(SCRIPTS_DATATABLE.strip()) > 0
        assert "fucntion" not in SCRIPTS_DATATABLE
        assert "retrun" not in SCRIPTS_DATATABLE
        assert "cosnt" not in SCRIPTS_DATATABLE

    def test_required_functions_defined(self):
        """Verify required JavaScript functions are defined."""
        from figrecipe._editor._templates._scripts import SCRIPTS_DATATABLE

        required_functions = [
            "toggleDatatablePanel",
            "initDatatablePanel",
            "handleDataFile",
            "parseCSV",
            "parseTSV",
            "parseJSON",
            "renderDatatable",
            "toggleColumnSelection",
            "plotFromVarAssignments",
            "clearDatatableData",
            "updateVarAssignSlots",
            "assignVariable",
        ]

        for func_name in required_functions:
            assert (
                f"function {func_name}" in SCRIPTS_DATATABLE
            ), f"Function {func_name} not found"


class TestDatatableRoutes:
    """Test datatable Flask routes."""

    def test_routes_module_exists(self):
        """Verify datatable routes module can be imported."""
        from figrecipe._editor._routes_datatable import register_datatable_routes

        assert callable(register_datatable_routes)

    def test_routes_registered_in_flask_app(self):
        """Verify datatable routes are registered in Flask app setup."""
        # Check that register_datatable_routes is imported in run method
        import inspect

        from figrecipe._editor._flask_app import FigureEditor

        source = inspect.getsource(FigureEditor.run)
        assert "register_datatable_routes" in source


class TestDatatableDataExtraction:
    """Test data extraction from recorded figures."""

    def test_extract_line_plot_data(self):
        """Test extracting data from a line plot."""
        import numpy as np

        import figrecipe as fr

        # Create a simple line plot
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        fig, ax = fr.subplots()
        ax.plot(x, y, label="test_line")

        # Check that record contains the data
        assert hasattr(fig, "_recorder")
        record = fig._recorder._figure_record

        # Find the plot call
        found_plot = False
        for ax_key, ax_record in record.axes.items():
            for call in ax_record.calls:
                if call.function == "plot":
                    found_plot = True
                    break

        assert found_plot, "plot call not found in record"

    def test_extract_scatter_plot_data(self):
        """Test extracting data from a scatter plot."""
        import numpy as np

        import figrecipe as fr

        x = np.array([1, 2, 3, 4])
        y = np.array([1, 4, 9, 16])

        fig, ax = fr.subplots()
        ax.scatter(x, y)

        assert hasattr(fig, "_recorder")
        record = fig._recorder._figure_record

        found_scatter = False
        for ax_key, ax_record in record.axes.items():
            for call in ax_record.calls:
                if call.function == "scatter":
                    found_scatter = True
                    break

        assert found_scatter, "scatter call not found in record"


class TestDatatableParsing:
    """Test CSV/JSON parsing utilities."""

    def test_parse_simple_csv(self):
        """Test that CSV parsing logic handles basic input."""
        csv_content = "x,y,z\n1,2,3\n4,5,6\n7,8,9"
        lines = csv_content.strip().split("\n")
        headers = lines[0].split(",")
        rows = []
        for line in lines[1:]:
            values = []
            for v in line.split(","):
                try:
                    values.append(float(v))
                except ValueError:
                    values.append(v)
            rows.append(values)

        assert headers == ["x", "y", "z"]
        assert len(rows) == 3
        assert rows[0] == [1.0, 2.0, 3.0]

    def test_parse_json_array_of_objects(self):
        """Test parsing JSON array of objects."""
        json_content = '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'
        data = json.loads(json_content)

        assert len(data) == 2
        headers = list(data[0].keys())
        rows = [[obj.get(h) for h in headers] for obj in data]

        assert headers == ["a", "b"]
        assert rows == [[1, 2], [3, 4]]


class TestEditableTable:
    """Test editable table functionality."""

    def test_editable_js_functions_exist(self):
        """Verify editable table JavaScript functions are defined."""
        from figrecipe._editor._templates._scripts import SCRIPTS_DATATABLE

        editable_functions = [
            "createNewCSV",
            "renderEditableTable",
            "updateColumnName",
            "updateColumnType",
            "updateCellValue",
            "addColumn",
            "addRow",
            "removeLastColumn",
            "removeLastRow",
        ]
        for func in editable_functions:
            assert f"function {func}" in SCRIPTS_DATATABLE, f"Missing: {func}"

    def test_editable_css_classes_exist(self):
        """Verify editable table CSS classes are defined."""
        from figrecipe._editor._templates._styles import STYLES_DATATABLE

        css_classes = [
            "editable-table-wrapper",
            "editable-table-scroll",
            "editable-table-actions",
            "editable-cell",
            "btn-create-csv",
            "col-name-input",
            "col-type-select",
        ]
        for css_class in css_classes:
            assert css_class in STYLES_DATATABLE, f"Missing CSS: {css_class}"

    def test_sticky_positioning_for_large_tables(self):
        """Verify sticky positioning CSS is applied for large table scrolling."""
        from figrecipe._editor._templates._styles import STYLES_DATATABLE

        # These patterns from vis_app ensure headers stay visible when scrolling
        assert "position: sticky" in STYLES_DATATABLE
        assert "z-index: 10" in STYLES_DATATABLE  # Header z-index
        assert "z-index: 11" in STYLES_DATATABLE  # Corner cell z-index

    def test_create_button_in_html(self):
        """Verify plot button is in HTML panel."""
        from figrecipe._editor._templates._html_datatable import HTML_DATATABLE_PANEL

        assert "btn-datatable-plot" in HTML_DATATABLE_PANEL
        assert "btn-new-tab" in HTML_DATATABLE_PANEL


class TestDecorationPlotHandlers:
    """Test decoration method handling in datatable plotting."""

    def test_dispatch_plot_import(self):
        """Verify dispatch_plot can be imported."""
        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        assert callable(dispatch_plot)

    def test_text_decoration_handler(self):
        """Test text decoration places text at correct positions."""
        import matplotlib.pyplot as plt

        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        fig, ax = plt.subplots()
        plot_data = {"x": [0.2, 0.5], "y": [0.3, 0.7], "s": ["A", "B"]}
        columns = ["x", "y", "s"]

        dispatch_plot(ax, "text", plot_data, columns)

        # Check that text objects were created
        texts = [c for c in ax.get_children() if hasattr(c, "get_text")]
        text_values = [t.get_text() for t in texts if t.get_text() in ["A", "B"]]
        assert "A" in text_values
        assert "B" in text_values
        plt.close(fig)

    def test_axhline_decoration_handler(self):
        """Test axhline creates horizontal lines."""
        import matplotlib.pyplot as plt

        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        fig, ax = plt.subplots()
        plot_data = {"y": [0.25, 0.5, 0.75]}
        columns = ["y"]

        dispatch_plot(ax, "axhline", plot_data, columns)

        # Check that lines were created
        lines = ax.get_lines()
        assert len(lines) == 3
        plt.close(fig)

    def test_axvline_decoration_handler(self):
        """Test axvline creates vertical lines."""
        import matplotlib.pyplot as plt

        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        fig, ax = plt.subplots()
        plot_data = {"x": [0.2, 0.8]}
        columns = ["x"]

        dispatch_plot(ax, "axvline", plot_data, columns)

        lines = ax.get_lines()
        assert len(lines) == 2
        plt.close(fig)

    def test_axhspan_decoration_handler(self):
        """Test axhspan creates horizontal spans."""
        import matplotlib.pyplot as plt

        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        fig, ax = plt.subplots()
        plot_data = {"ymin": [0.2, 0.6], "ymax": [0.4, 0.8]}
        columns = ["ymin", "ymax"]

        dispatch_plot(ax, "axhspan", plot_data, columns)

        # Check patches were created (spans are patches)
        patches = ax.patches
        assert len(patches) == 2
        plt.close(fig)

    def test_axvspan_decoration_handler(self):
        """Test axvspan creates vertical spans."""
        import matplotlib.pyplot as plt

        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        fig, ax = plt.subplots()
        plot_data = {"xmin": [0.1, 0.5], "xmax": [0.3, 0.7]}
        columns = ["xmin", "xmax"]

        dispatch_plot(ax, "axvspan", plot_data, columns)

        patches = ax.patches
        assert len(patches) == 2
        plt.close(fig)

    def test_arrow_decoration_handler(self):
        """Test arrow creates arrow patches."""
        import matplotlib.pyplot as plt

        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        fig, ax = plt.subplots()
        plot_data = {"x": [0.2], "y": [0.2], "dx": [0.3], "dy": [0.3]}
        columns = ["x", "y", "dx", "dy"]

        dispatch_plot(ax, "arrow", plot_data, columns)

        # Arrows are FancyArrow patches
        patches = ax.patches
        assert len(patches) >= 1
        plt.close(fig)

    def test_unknown_plot_type_raises_error(self):
        """Test that unknown plot type raises ValueError."""
        import matplotlib.pyplot as plt

        from figrecipe._editor._datatable_plot_handlers import dispatch_plot

        fig, ax = plt.subplots()
        plot_data = {"x": [1, 2, 3]}
        columns = ["x"]

        with pytest.raises(ValueError, match="Unknown plot type"):
            dispatch_plot(ax, "nonexistent_method", plot_data, columns)
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
