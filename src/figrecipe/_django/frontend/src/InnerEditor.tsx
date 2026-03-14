/** InnerEditor — React editor content (without shell chrome).
 *
 * This is what gets mounted inside AppShell's mainContent slot.
 * Contains: DataTable | PlotTypeNav | Canvas | Properties panes.
 */

import { useEffect } from "react";
import { CanvasPane } from "./components/CanvasPane/CanvasPane";
import { DataTablePane } from "./components/DataTablePane/DataTablePane";
import { PlotTypeNav } from "./components/PlotTypeNav/PlotTypeNav";
import { PropertiesPane } from "./components/PropertiesPane/PropertiesPane";
import { Spinner } from "./components/common/Spinner";
import { Toast } from "./components/common/Toast";
import { useElementInspector } from "./hooks/useElementInspector";
import { useEmbeddedMessages } from "./hooks/useEmbeddedMessages";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { usePanelResize } from "./hooks/usePanelResize";
import { useSessionPersistence } from "./hooks/useSessionPersistence";
import { initUndoHistory } from "./hooks/useUndoRedo";
import { useEditorStore } from "./store/useEditorStore";

interface InnerEditorProps {
  embedded?: boolean;
}

export function InnerEditor({ embedded = false }: InnerEditorProps) {
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
  useEmbeddedMessages(embedded);

  // Initialize undo history once on mount
  useEffect(() => {
    initUndoHistory();
  }, []);

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
    <div className="inner-editor">
      <div className="editor-body">
        {/* Pane 1 — Data Table */}
        <aside
          className={`split-pane split-pane-left${dataPanel.collapsed ? " collapsed" : ""}`}
          style={dataPanel.collapsed ? undefined : { width: dataPanel.width }}
        >
          <DataTablePane
            onHeaderDoubleClick={dataPanel.headerProps.onDoubleClick}
          />
        </aside>

        <div className="panel-resizer" {...dataPanel.resizerProps} />

        {/* Plot type selector nav */}
        <PlotTypeNav />

        {/* Pane 2 — Canvas (flex: 1) */}
        <main className="split-pane split-pane-center">
          <CanvasPane />
        </main>

        <div className="panel-resizer" {...rightPanel.resizerProps} />

        {/* Pane 3 — Properties/Details */}
        <aside
          className={`split-pane split-pane-right${rightPanel.collapsed ? " collapsed" : ""}`}
          style={rightPanel.collapsed ? undefined : { width: rightPanel.width }}
        >
          <PropertiesPane
            onHeaderDoubleClick={rightPanel.headerProps.onDoubleClick}
          />
        </aside>
      </div>

      {loading && <Spinner />}
      <Toast />
    </div>
  );
}
