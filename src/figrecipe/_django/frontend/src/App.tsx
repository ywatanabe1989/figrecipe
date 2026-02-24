/** Root layout — vis_app 4-pane: Ribbon | FileTree | DataTable | Canvas | Details. */

import { useEffect } from "react";
import { CanvasPane } from "./components/CanvasPane/CanvasPane";
import { DataTablePane } from "./components/DataTablePane/DataTablePane";
import { FileTreePane } from "./components/FileTreePane/FileTreePane";
import { PropertiesPane } from "./components/PropertiesPane/PropertiesPane";
import { Ribbon } from "./components/Ribbon/Ribbon";
import { StatusBar } from "./components/StatusBar/StatusBar";
import { Spinner } from "./components/common/Spinner";
import { Toast } from "./components/common/Toast";
import { useElementInspector } from "./hooks/useElementInspector";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { usePanelResize } from "./hooks/usePanelResize";
import { useSessionPersistence } from "./hooks/useSessionPersistence";
import { initUndoHistory } from "./hooks/useUndoRedo";
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
  useSessionPersistence();

  // Initialize undo history once on mount
  useEffect(() => {
    initUndoHistory();
  }, []);

  const fileTreePanel = usePanelResize({
    direction: "left",
    minWidth: 40,
    defaultWidth: 200,
    storageKey: "figrecipe-filetree-width",
    collapseKey: "figrecipe-filetree-collapsed",
  });

  const dataPanel = usePanelResize({
    direction: "left",
    minWidth: 40,
    defaultWidth: 350,
    storageKey: "figrecipe-data-width",
    collapseKey: "figrecipe-data-collapsed",
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
      <Ribbon />
      <div className="editor-body">
        {/* Pane 1 — File Tree (200px default) */}
        <aside
          className={`split-pane split-pane-left${fileTreePanel.collapsed ? " collapsed" : ""}`}
          style={
            fileTreePanel.collapsed ? undefined : { width: fileTreePanel.width }
          }
        >
          <FileTreePane
            onHeaderDoubleClick={fileTreePanel.headerProps.onDoubleClick}
          />
        </aside>

        <div className="panel-resizer" {...fileTreePanel.resizerProps} />

        {/* Pane 2 — Data Table (350px default) */}
        <aside
          className={`split-pane split-pane-left${dataPanel.collapsed ? " collapsed" : ""}`}
          style={dataPanel.collapsed ? undefined : { width: dataPanel.width }}
        >
          <DataTablePane
            onHeaderDoubleClick={dataPanel.headerProps.onDoubleClick}
          />
        </aside>

        <div className="panel-resizer" {...dataPanel.resizerProps} />

        {/* Pane 3 — Canvas (flex: 1) */}
        <main className="split-pane split-pane-center">
          <CanvasPane />
        </main>

        <div className="panel-resizer" {...rightPanel.resizerProps} />

        {/* Pane 4 — Properties/Details (320px default) */}
        <aside
          className={`split-pane split-pane-right${rightPanel.collapsed ? " collapsed" : ""}`}
          style={rightPanel.collapsed ? undefined : { width: rightPanel.width }}
        >
          <PropertiesPane
            onHeaderDoubleClick={rightPanel.headerProps.onDoubleClick}
          />
        </aside>
      </div>

      <StatusBar />
      {loading && <Spinner />}
      <Toast />
    </div>
  );
}
