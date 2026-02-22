/** Left pane — Data table with vis_app pane-header. */

import { useCallback, useRef } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";

interface DataTablePaneProps {
  onHeaderDoubleClick?: () => void;
}

export function DataTablePane({ onHeaderDoubleClick }: DataTablePaneProps) {
  const { datatableTabs, activeTabId, showToast, loadDatatable } =
    useEditorStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const tabs = Object.values(datatableTabs);
  const activeTab = activeTabId ? datatableTabs[activeTabId] : null;

  const handleExportCsv = useCallback(async () => {
    try {
      const blob = await api.getBlob("download/csv");
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "data.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      showToast(`Export failed: ${e}`, "error");
    }
  }, [showToast]);

  const handleImportCsv = useCallback(
    async (file: File) => {
      try {
        const content = await file.text();
        const ext = file.name.split(".").pop()?.toLowerCase();
        const format = ext === "tsv" ? "tsv" : ext === "json" ? "json" : "csv";
        await api.post("datatable/import", { content, format });
        showToast("Imported data", "success");
        loadDatatable();
      } catch (e) {
        showToast(`Import failed: ${e}`, "error");
      }
    },
    [showToast, loadDatatable],
  );

  return (
    <>
      {/* vis_app .pane-header */}
      <div className="pane-header" onDoubleClick={onHeaderDoubleClick}>
        {/* Data dropdown */}
        <div className="data-dropdown-container">
          <button className="data-dropdown-toggle" type="button">
            <i className="fas fa-table" />
            <span className="data-dropdown-label">
              {tabs.length > 0
                ? `${tabs.length} table${tabs.length > 1 ? "s" : ""}`
                : "No tables"}
            </span>
            <i className="fas fa-chevron-down" />
          </button>
          <button
            className="pane-header-btn data-new-btn"
            type="button"
            onClick={() => fileInputRef.current?.click()}
            title="Import data"
          >
            <i className="fas fa-plus" />
          </button>
        </div>

        {/* WIP badge */}
        <span className="badge badge-wip">WIP</span>

        {/* Action buttons */}
        <div className="pane-header-buttons">
          <button
            className="pane-header-btn"
            onClick={handleExportCsv}
            title="Export CSV"
            disabled={tabs.length === 0}
            type="button"
          >
            <i className="fas fa-file-export" />
          </button>
          <button
            className="pane-header-btn"
            title="Sort (WIP)"
            type="button"
            disabled
          >
            <i className="fas fa-sort" />
          </button>
          <button
            className="pane-header-btn"
            title="Filter (WIP)"
            type="button"
            disabled
          >
            <i className="fas fa-filter" />
          </button>
          <button
            className="pane-header-btn"
            title="Keyboard shortcuts"
            type="button"
          >
            <i className="fas fa-keyboard" />
          </button>
        </div>

        {/* Vertical title (visible only when collapsed via CSS) */}
        <span className="panel-title">Data</span>
      </div>

      {/* Hidden file input for CSV import */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.tsv,.json,.xlsx"
        style={{ display: "none" }}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleImportCsv(file);
          e.target.value = "";
        }}
      />

      {/* Pane content */}
      <div className="pane-content">
        {tabs.length === 0 ? (
          <div className="datatable-empty-state">
            <i className="fas fa-th-large datatable-empty-icon" />
            <p className="datatable-empty-title">No data loaded</p>
            <p className="datatable-empty-hint">
              Import CSV or Excel, or drag &amp; drop files here
            </p>
          </div>
        ) : (
          <>
            {tabs.length > 1 && (
              <div className="datatable-panel__tabs">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    className={`datatable-panel__tab${tab.id === activeTabId ? " active" : ""}`}
                    onClick={() =>
                      useEditorStore.setState({ activeTabId: tab.id })
                    }
                    type="button"
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            )}

            {activeTab && (
              <div className="datatable-panel__table-wrapper">
                <table className="datatable-panel__table">
                  <thead>
                    <tr>
                      {activeTab.columns.map((col, i) => (
                        <th key={i}>{col.name}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {activeTab.rows.slice(0, 100).map((row, ri) => (
                      <tr key={ri}>
                        {row.map((cell, ci) => (
                          <td key={ci}>
                            {typeof cell === "number"
                              ? Number.isInteger(cell)
                                ? cell
                                : cell.toFixed(4)
                              : String(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {activeTab.rows.length > 100 && (
                  <p className="datatable-panel__truncated">
                    Showing 100 of {activeTab.rows.length} rows
                  </p>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
}
