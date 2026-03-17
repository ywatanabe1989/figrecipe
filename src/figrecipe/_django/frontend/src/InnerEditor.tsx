/** InnerEditor — React editor content (without shell chrome).
 *
 * This is what gets mounted inside Workspace's appContent slot.
 * Two tabs:
 *   - Plot: DataTable | PlotTypeNav | FigureViewer | Details
 *   - Canvas: Canvas | Details
 *
 * Layout is managed by PaneLayout (scitex-ui) — pure TS, no React
 * state for widths. Panes declare constraints via data attributes.
 */

import { useEffect, useState } from "react";
import { CanvasPane } from "./components/CanvasPane/CanvasPane";
import { DataTablePane } from "./components/DataTablePane/DataTablePane";
import { FigureViewer } from "./components/FigureViewer/FigureViewer";
import { PlotTypeNav } from "./components/PlotTypeNav/PlotTypeNav";
import { PropertiesPane } from "./components/PropertiesPane/PropertiesPane";
import { Spinner } from "./components/common/Spinner";
import { Toast } from "./components/common/Toast";
import { useEmbeddedMessages } from "./hooks/useEmbeddedMessages";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { useSessionPersistence } from "./hooks/useSessionPersistence";
import { initUndoHistory } from "./hooks/useUndoRedo";
import { useEditorStore } from "./store/useEditorStore";
import {
  PaneLayout,
  Pane,
} from "@scitex/ui/src/scitex_ui/static/scitex_ui/react/app/pane-layout";

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

  useKeyboardShortcuts();
  useSessionPersistence();
  useEmbeddedMessages(embedded);

  useEffect(() => {
    initUndoHistory();
  }, []);

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

      {/* ── Tab Content — PaneLayout manages all resize/collapse ── */}
      {activeTab === "plot" && (
        <PaneLayout storagePrefix="figrecipe-plot" className="editor-body">
          <Pane
            id="data-table"
            as="aside"
            minWidth={40}
            defaultWidth={200}
            canCollapse
          >
            <DataTablePane />
          </Pane>
          <Pane id="plot-nav" as="nav" fixed width={56}>
            <PlotTypeNav />
          </Pane>
          <Pane id="viewer" as="main" minWidth={60} canCollapse>
            <FigureViewer />
          </Pane>
          <Pane
            id="details"
            as="aside"
            minWidth={40}
            defaultWidth={240}
            canCollapse
          >
            <PropertiesPane />
          </Pane>
        </PaneLayout>
      )}

      {activeTab === "canvas" && (
        <PaneLayout storagePrefix="figrecipe-canvas" className="editor-body">
          <Pane id="canvas" as="main" minWidth={60} canCollapse>
            <CanvasPane />
          </Pane>
          <Pane
            id="details"
            as="aside"
            minWidth={40}
            defaultWidth={240}
            canCollapse
          >
            <PropertiesPane />
          </Pane>
        </PaneLayout>
      )}

      {loading && <Spinner />}
      <Toast />
    </div>
  );
}
