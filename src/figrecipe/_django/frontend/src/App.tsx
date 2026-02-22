/** Root layout — vis_app 3-pane: DataTable | Canvas | Details. No top toolbar. */

import { useEffect } from "react";
import { CanvasPane } from "./components/CanvasPane/CanvasPane";
import { DataTablePane } from "./components/DataTablePane/DataTablePane";
import { PropertiesPane } from "./components/PropertiesPane/PropertiesPane";
import { Spinner } from "./components/common/Spinner";
import { Toast } from "./components/common/Toast";
import { useElementInspector } from "./hooks/useElementInspector";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { usePanelResize } from "./hooks/usePanelResize";
import { useEditorStore } from "./store/useEditorStore";

export function App() {
  const {
    loading,
    loadPreview,
    loadHitmap,
    loadFiles,
    loadThemes,
    loadDatatable,
  } = useEditorStore();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const hasRecipe = !!params.get("recipe");

    loadFiles();
    loadThemes();

    if (hasRecipe) {
      loadPreview();
      loadHitmap();
      loadDatatable();
    }
  }, [loadPreview, loadHitmap, loadFiles, loadThemes, loadDatatable]);

  // Global hooks
  useElementInspector();
  useKeyboardShortcuts();

  const leftPanel = usePanelResize({
    direction: "left",
    minWidth: 40,
    defaultWidth: 400,
    storageKey: "figrecipe-left-width",
    collapseKey: "figrecipe-left-collapsed",
  });

  const rightPanel = usePanelResize({
    direction: "right",
    minWidth: 40,
    defaultWidth: 320,
    storageKey: "figrecipe-right-width",
    collapseKey: "figrecipe-right-collapsed",
  });

  return (
    <div className="editor-root">
      <div className="editor-body">
        {/* Left pane — Data Table (400px default) */}
        <aside
          className={`split-pane split-pane-left${leftPanel.collapsed ? " collapsed" : ""}`}
          style={leftPanel.collapsed ? undefined : { width: leftPanel.width }}
          onClick={leftPanel.collapsed ? leftPanel.toggleCollapse : undefined}
        >
          <DataTablePane
            collapsed={leftPanel.collapsed}
            toggleCollapse={leftPanel.toggleCollapse}
          />
        </aside>

        <div className="panel-resizer" {...leftPanel.resizerProps} />

        {/* Center pane — Canvas (flex: 1) */}
        <main className="split-pane split-pane-center">
          <CanvasPane />
        </main>

        <div className="panel-resizer" {...rightPanel.resizerProps} />

        {/* Right pane — Properties/Details (320px default) */}
        <aside
          className={`split-pane split-pane-right${rightPanel.collapsed ? " collapsed" : ""}`}
          style={rightPanel.collapsed ? undefined : { width: rightPanel.width }}
          onClick={rightPanel.collapsed ? rightPanel.toggleCollapse : undefined}
        >
          <PropertiesPane
            collapsed={rightPanel.collapsed}
            toggleCollapse={rightPanel.toggleCollapse}
          />
        </aside>
      </div>

      {loading && <Spinner />}
      <Toast />
    </div>
  );
}
