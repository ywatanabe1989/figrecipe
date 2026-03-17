/** InnerEditor — React editor content (without shell chrome).
 *
 * This is what gets mounted inside Workspace's appContent slot.
 * Two tabs:
 *   - Plot: DataTable | PlotTypeNav | FigureViewer | Details
 *   - Canvas: Canvas | Details
 */

import { useCallback, useEffect, useRef, useState } from "react";
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

  // Ref for center pane (used by auto-collapse + context-zoom)
  const centerRef = useRef<HTMLElement | null>(null);

  // Center pane collapse — two modes:
  //   "manual"  = user double-clicked header → persisted to localStorage
  //   "auto"    = pane too narrow → temporary, auto-expands when space returns
  const CENTER_MIN_WIDTH = 60;
  const CENTER_EXPAND_WIDTH = 80;
  const collapseMode = useRef<"manual" | "auto" | null>(null);

  const [centerCollapsed, setCenterCollapsed] = useState(() => {
    try {
      if (localStorage.getItem("figrecipe-center-collapsed") === "true") {
        collapseMode.current = "manual";
        return true;
      }
    } catch {}
    return false;
  });

  const toggleCenter = useCallback(() => {
    setCenterCollapsed((prev) => {
      const next = !prev;
      collapseMode.current = next ? "manual" : null;
      try {
        localStorage.setItem("figrecipe-center-collapsed", String(next));
      } catch {}
      return next;
    });
  }, []);

  // Auto-collapse when narrow, auto-expand when space returns.
  // Only auto-collapse triggers auto-expand; manual collapse stays.
  useEffect(() => {
    const el = centerRef.current;
    if (!el) return;
    const obs = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const w = entry.contentRect.width;
        if (w < CENTER_MIN_WIDTH && !centerCollapsed) {
          // Auto-collapse (temporary, not persisted)
          collapseMode.current = "auto";
          setCenterCollapsed(true);
        } else if (
          w >= CENTER_EXPAND_WIDTH &&
          centerCollapsed &&
          collapseMode.current === "auto"
        ) {
          // Auto-expand — only if it was auto-collapsed, not manual
          collapseMode.current = null;
          setCenterCollapsed(false);
        }
      }
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, [centerCollapsed]);

  // Cross-panel refs for mutual width constraints
  const dataPanelRef = useRef<HTMLElement | null>(null);
  const rightPanelRef = useRef<HTMLElement | null>(null);

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
    // Cap: leave room for right panel (sibling) + 50px min center
    siblingRefs: [rightPanelRef],
    reservedWidth: 50,
  });

  const rightPanel = usePanelResize({
    direction: "right",
    minWidth: 40,
    defaultWidth: 240,
    storageKey: "figrecipe-right-width",
    collapseKey: "figrecipe-right-collapsed",
    // Cap: leave room for data panel + PlotTypeNav (sibling) + 50px min center
    siblingRefs: [dataPanelRef],
    reservedWidth: 50,
  });

  // Sync shared refs with actual panel refs
  useEffect(() => {
    rightPanelRef.current = rightPanel.panelRef.current;
    dataPanelRef.current = dataPanel.panelRef.current;
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

            {/* Plot type selector nav — fixed width, not resizable */}
            <PlotTypeNav />

            {/* Pane 2 — Figure Viewer (rendered image, not canvas) */}
            <main
              ref={centerRef as React.Ref<HTMLElement>}
              className={`split-pane split-pane-center${centerCollapsed ? " collapsed" : ""}`}
            >
              {centerCollapsed ? (
                <div className="pane-header" onDoubleClick={toggleCenter}>
                  <span className="panel-title">
                    <i className="fas fa-image" />
                    Viewer
                  </span>
                </div>
              ) : (
                <FigureViewer />
              )}
            </main>
          </>
        )}

        {activeTab === "canvas" && (
          <>
            {/* Canvas pane */}
            <main
              ref={centerRef as React.Ref<HTMLElement>}
              className={`split-pane split-pane-center${centerCollapsed ? " collapsed" : ""}`}
            >
              {centerCollapsed ? (
                <div className="pane-header" onDoubleClick={toggleCenter}>
                  <span className="panel-title">
                    <i className="fas fa-object-group" />
                    Canvas
                  </span>
                </div>
              ) : (
                <CanvasPane onHeaderDoubleClick={toggleCenter} />
              )}
            </main>
          </>
        )}

        {/* Resizer + Details grouped together and pushed to far right */}
        <div
          className="stx-layout-most-right"
          style={{ display: "flex", flexShrink: 0 }}
        >
          <div className="panel-resizer" {...rightPanel.resizerProps} />
          <aside
            ref={rightPanel.panelRef as React.Ref<HTMLElement>}
            className={`split-pane split-pane-right${rightPanel.collapsed ? " collapsed" : ""}`}
            style={
              rightPanel.collapsed
                ? { cursor: "pointer" }
                : { width: rightPanel.width }
            }
            onDoubleClick={
              rightPanel.collapsed ? rightPanel.toggleCollapse : undefined
            }
            title={rightPanel.collapsed ? "Double-click to expand" : undefined}
          >
            <PropertiesPane
              onHeaderDoubleClick={rightPanel.headerProps.onDoubleClick}
            />
          </aside>
        </div>
      </div>

      {loading && <Spinner />}
      <Toast />
    </div>
  );
}
