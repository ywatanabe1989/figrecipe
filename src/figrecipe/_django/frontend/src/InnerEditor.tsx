/** InnerEditor — React editor content (without shell chrome).
 *
 * This is what gets mounted inside Workspace's appContent slot.
 * Two tabs:
 *   - Plot: DataTable | PlotTypeNav | FigureViewer | Details
 *   - Canvas: Canvas | Details
 */

import { useEffect, useState } from "react";
import { CanvasPane } from "./components/CanvasPane/CanvasPane";
import { DataTablePane } from "./components/DataTablePane/DataTablePane";
import { FigureViewer } from "./components/FigureViewer/FigureViewer";
import { PlotTypeNav } from "./components/PlotTypeNav/PlotTypeNav";
import { PropertiesPane } from "./components/PropertiesPane/PropertiesPane";
import { Spinner } from "./components/common/Spinner";
import { Toast } from "./components/common/Toast";
// Element inspector now provided by scitex-ui (imported in main.tsx)
import { useEmbeddedMessages } from "./hooks/useEmbeddedMessages";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { usePanelResize } from "@scitex/ui/src/scitex_ui/static/scitex_ui/react/app/usePanelResize";
import { useWorkspaceResize } from "@scitex/ui/src/scitex_ui/static/scitex_ui/react/shell/workspace/WorkspaceResizeContext";
import { useSessionPersistence } from "./hooks/useSessionPersistence";
import { initUndoHistory } from "./hooks/useUndoRedo";
import { useEditorStore } from "./store/useEditorStore";

type AppTab = "plot" | "canvas";

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

  const [activeTab, setActiveTab] = useState<AppTab>(() => {
    try {
      return (localStorage.getItem("figrecipe-app-tab") as AppTab) || "plot";
    } catch {
      return "plot";
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem("figrecipe-app-tab", activeTab);
    } catch {}
  }, [activeTab]);

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

  // Global hooks (element inspector from scitex-ui, initialized in main.tsx)
  useKeyboardShortcuts();
  useSessionPersistence();
  useEmbeddedMessages(embedded);

  // Initialize undo history once on mount
  useEffect(() => {
    initUndoHistory();
  }, []);

  const { propagateLeft } = useWorkspaceResize();

  const dataPanel = usePanelResize({
    direction: "left",
    minWidth: 40,
    defaultWidth: 200,
    storageKey: "figrecipe-data-width",
    collapseKey: "figrecipe-data-collapsed",
    onBoundaryOverflow: (overflow, dir) => {
      console.log("[resize] data panel overflow:", overflow, "px", dir);
      if (dir === "left") propagateLeft(overflow);
    },
  });

  const selectorPanel = usePanelResize({
    direction: "left",
    minWidth: 40,
    defaultWidth: 56,
    storageKey: "figrecipe-selector-width",
    collapseKey: "figrecipe-selector-collapsed",
  });

  const rightPanel = usePanelResize({
    direction: "right",
    minWidth: 40,
    defaultWidth: 240,
    storageKey: "figrecipe-right-width",
    collapseKey: "figrecipe-right-collapsed",
  });

  return (
    <div className="inner-editor">
      {/* ── Tab Switcher ────────────────────────────── */}
      <div className="inner-editor__tabs">
        <button
          className={`inner-editor__tab${activeTab === "plot" ? " inner-editor__tab--active" : ""}`}
          onClick={() => setActiveTab("plot")}
        >
          <i className="fas fa-chart-line" /> Plot
        </button>
        <button
          className={`inner-editor__tab${activeTab === "canvas" ? " inner-editor__tab--active" : ""}`}
          onClick={() => setActiveTab("canvas")}
        >
          <i className="fas fa-object-group" /> Canvas
        </button>
      </div>

      {/* ── Tab Content ─────────────────────────────── */}
      <div className="editor-body">
        {activeTab === "plot" && (
          <>
            {/* Pane 1 — Data Table */}
            <aside
              ref={dataPanel.panelRef as React.Ref<HTMLElement>}
              className={`split-pane split-pane-left${dataPanel.collapsed ? " collapsed" : ""}`}
              style={
                dataPanel.collapsed ? undefined : { width: dataPanel.width }
              }
            >
              <DataTablePane
                onHeaderDoubleClick={dataPanel.headerProps.onDoubleClick}
              />
            </aside>

            <div className="panel-resizer" {...dataPanel.resizerProps} />

            {/* Plot type selector nav — resizable */}
            <div
              ref={selectorPanel.panelRef as React.Ref<HTMLDivElement>}
              style={
                selectorPanel.collapsed
                  ? { width: 40, overflow: "hidden", flexShrink: 0 }
                  : { width: selectorPanel.width, flexShrink: 0 }
              }
            >
              <PlotTypeNav />
            </div>
            <div className="panel-resizer" {...selectorPanel.resizerProps} />

            {/* Pane 2 — Figure Viewer (rendered image, not canvas) */}
            <main className="split-pane split-pane-center">
              <FigureViewer />
            </main>
          </>
        )}

        {activeTab === "canvas" && (
          <>
            {/* Canvas — full width */}
            <main className="split-pane split-pane-center">
              <CanvasPane />
            </main>
          </>
        )}

        <div className="panel-resizer" {...rightPanel.resizerProps} />

        {/* Details panel — shared between both tabs */}
        <aside
          ref={rightPanel.panelRef as React.Ref<HTMLElement>}
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
