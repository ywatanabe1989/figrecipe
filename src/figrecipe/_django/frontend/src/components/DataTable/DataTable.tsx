/** Data table panel — displays plot data with CSV import/export. */

import { useCallback, useRef } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";

export function DataTable() {
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
    <div className="datatable-panel">
      <div className="datatable-panel__header">
        <h3>Data</h3>
        <div className="datatable-panel__actions">
          <button
            className="file-browser__btn"
            onClick={() => fileInputRef.current?.click()}
            title="Import CSV"
          >
            &#x2191;
          </button>
          <button
            className="file-browser__btn"
            onClick={handleExportCsv}
            title="Export CSV"
            disabled={tabs.length === 0}
          >
            &#x2193;
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.tsv,.json"
          style={{ display: "none" }}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleImportCsv(file);
            e.target.value = "";
          }}
        />
      </div>

      {tabs.length === 0 ? (
        <div className="datatable-panel__empty">
          <p>No data available</p>
          <p className="datatable-panel__hint">
            Plot data will appear here when a figure is loaded
          </p>
        </div>
      ) : (
        <>
          <div className="datatable-panel__tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`datatable-panel__tab${tab.id === activeTabId ? " active" : ""}`}
                onClick={() => useEditorStore.setState({ activeTabId: tab.id })}
              >
                {tab.label}
              </button>
            ))}
          </div>

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
  );
}
