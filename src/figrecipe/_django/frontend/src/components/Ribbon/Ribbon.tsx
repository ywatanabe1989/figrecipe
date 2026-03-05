/** Ribbon toolbar — tabbed groups matching vis_app ribbon pattern.
 * Tabs: Home, Layout, Style, View.
 * Each tab shows a panel of grouped buttons.
 */

import { useState } from "react";
import { redo, undo } from "../../hooks/useUndoRedo";
import { useEditorStore } from "../../store/useEditorStore";
import { ExportDialog } from "../ExportDialog/ExportDialog";
import { RibbonButton } from "./RibbonButton";
import { RibbonGroup } from "./RibbonGroup";

type TabId = "home" | "layout" | "style" | "view";

export function Ribbon() {
  const [activeTab, setActiveTab] = useState<TabId>("home");

  return (
    <div className="ribbon">
      {/* Tab buttons */}
      <div className="ribbon-tabs">
        <Tab
          id="home"
          icon="fas fa-home"
          label="Home"
          active={activeTab}
          onClick={setActiveTab}
        />
        <Tab
          id="layout"
          icon="fas fa-th-large"
          label="Layout"
          active={activeTab}
          onClick={setActiveTab}
        />
        <Tab
          id="style"
          icon="fas fa-palette"
          label="Style"
          active={activeTab}
          onClick={setActiveTab}
        />
        <Tab
          id="view"
          icon="fas fa-eye"
          label="View"
          active={activeTab}
          onClick={setActiveTab}
        />
      </div>

      {/* Tab content panels */}
      <div className="ribbon-content">
        <HomePanel active={activeTab === "home"} />
        <LayoutPanel active={activeTab === "layout"} />
        <StylePanel active={activeTab === "style"} />
        <ViewPanel active={activeTab === "view"} />
      </div>
    </div>
  );
}

/* ── Tab button ───────────────────────────────────────────── */

function Tab({
  id,
  icon,
  label,
  active,
  onClick,
}: {
  id: TabId;
  icon: string;
  label: string;
  active: TabId;
  onClick: (id: TabId) => void;
}) {
  return (
    <button
      className={`ribbon-tab${active === id ? " active" : ""}`}
      onClick={() => onClick(id)}
      type="button"
    >
      <i className={icon} />
      {label}
    </button>
  );
}

/* ── Home Panel ───────────────────────────────────────────── */

function HomePanel({ active }: { active: boolean }) {
  const {
    save,
    restore,
    selectedFigureId,
    copyFigure,
    pasteFigure,
    removeFigure,
    clipboard,
  } = useEditorStore();
  const [exportOpen, setExportOpen] = useState(false);

  return (
    <div className={`ribbon-panel${active ? " active" : ""}`}>
      <RibbonGroup label="File">
        <RibbonButton
          icon="fas fa-save"
          label="Save"
          onClick={save}
          title="Compose canvas figures and save (Ctrl+S)"
        />
        <RibbonButton
          icon="fas fa-undo"
          label="Restore"
          onClick={restore}
          title="Restore original"
        />
        <RibbonButton
          icon="fas fa-download"
          label="Export"
          onClick={() => setExportOpen(true)}
          title="Compose and export as PNG/SVG/PDF"
        />
        {exportOpen && <ExportDialog onClose={() => setExportOpen(false)} />}
      </RibbonGroup>

      <RibbonGroup label="Undo">
        <RibbonButton
          icon="fas fa-undo"
          label="Undo"
          onClick={undo}
          title="Undo (Ctrl+Z)"
        />
        <RibbonButton
          icon="fas fa-redo"
          label="Redo"
          onClick={redo}
          title="Redo (Ctrl+Shift+Z)"
        />
      </RibbonGroup>

      <RibbonGroup label="Clipboard" separator={false}>
        <RibbonButton
          icon="fas fa-copy"
          label="Copy"
          onClick={copyFigure}
          disabled={!selectedFigureId}
          title="Copy (Ctrl+C)"
        />
        <RibbonButton
          icon="fas fa-paste"
          label="Paste"
          onClick={pasteFigure}
          disabled={!clipboard}
          title="Paste (Ctrl+V)"
        />
        <RibbonButton
          icon="fas fa-trash-alt"
          label="Delete"
          onClick={() => selectedFigureId && removeFigure(selectedFigureId)}
          disabled={!selectedFigureId}
          title="Delete (Del)"
        />
      </RibbonGroup>
    </div>
  );
}

/* ── Layout Panel ─────────────────────────────────────────── */

function LayoutPanel({ active }: { active: boolean }) {
  const {
    snapEnabled,
    showRulers,
    rulerUnit,
    toggleSnap,
    toggleRulers,
    toggleRulerUnit,
    alignFigures,
    distributeFigures,
    reorderPanelLetters,
    groupFigures,
    ungroupFigures,
    placedFigures,
    selectedFigureId,
  } = useEditorStore();

  return (
    <div className={`ribbon-panel${active ? " active" : ""}`}>
      <RibbonGroup label="Figure Align">
        <RibbonButton
          icon="fas fa-align-left"
          label="Left"
          onClick={() => alignFigures("left")}
        />
        <RibbonButton
          icon="fas fa-align-right"
          label="Right"
          onClick={() => alignFigures("right")}
        />
        <RibbonButton
          icon="fas fa-arrow-up"
          label="Top"
          onClick={() => alignFigures("top")}
        />
        <RibbonButton
          icon="fas fa-arrow-down"
          label="Bottom"
          onClick={() => alignFigures("bottom")}
        />
        <RibbonButton
          icon="fas fa-arrows-alt-h"
          label="Ctr H"
          onClick={() => alignFigures("center-h")}
        />
        <RibbonButton
          icon="fas fa-arrows-alt-v"
          label="Ctr V"
          onClick={() => alignFigures("center-v")}
        />
      </RibbonGroup>

      <RibbonGroup label="Axes Align">
        <RibbonButton
          icon="fas fa-align-left"
          label="Ax Left"
          onClick={() => alignFigures("axes-left")}
        />
        <RibbonButton
          icon="fas fa-align-right"
          label="Ax Right"
          onClick={() => alignFigures("axes-right")}
        />
        <RibbonButton
          icon="fas fa-arrow-up"
          label="Ax Top"
          onClick={() => alignFigures("axes-top")}
        />
        <RibbonButton
          icon="fas fa-arrow-down"
          label="Ax Bot"
          onClick={() => alignFigures("axes-bottom")}
        />
      </RibbonGroup>

      <RibbonGroup label="Distribute">
        <RibbonButton
          icon="fas fa-grip-lines-vertical"
          label="Horiz"
          onClick={() => distributeFigures("horizontal")}
        />
        <RibbonButton
          icon="fas fa-grip-lines"
          label="Vert"
          onClick={() => distributeFigures("vertical")}
        />
      </RibbonGroup>

      <RibbonGroup label="Panels">
        <RibbonButton
          icon="fas fa-sort-alpha-down"
          label="Reorder"
          onClick={reorderPanelLetters}
          title="Reorder panel letters by position (top-left → bottom-right)"
        />
        <RibbonButton
          icon="fas fa-object-group"
          label="Group"
          onClick={() => {
            const ids = placedFigures.map((f) => f.id);
            if (ids.length >= 2) groupFigures(ids);
          }}
          disabled={placedFigures.length < 2}
          title="Group all figures (Ctrl+G)"
        />
        <RibbonButton
          icon="fas fa-object-ungroup"
          label="Ungroup"
          onClick={() => {
            const sel = placedFigures.find((f) => f.id === selectedFigureId);
            if (sel?.groupId) ungroupFigures(sel.groupId);
          }}
          disabled={
            !selectedFigureId ||
            !placedFigures.find((f) => f.id === selectedFigureId)?.groupId
          }
          title="Ungroup selected figure's group"
        />
      </RibbonGroup>

      <RibbonGroup label="Guides" separator={false}>
        <RibbonButton
          icon="fas fa-magnet"
          label="Snap"
          onClick={toggleSnap}
          active={snapEnabled}
          title={`Snap: ${snapEnabled ? "ON" : "OFF"}`}
        />
        <RibbonButton
          icon="fas fa-ruler-combined"
          label="Rulers"
          onClick={toggleRulers}
          active={showRulers}
        />
        <RibbonButton
          icon="fas fa-ruler"
          label={rulerUnit}
          onClick={toggleRulerUnit}
          title={`Unit: ${rulerUnit} (click to toggle)`}
        />
      </RibbonGroup>
    </div>
  );
}

/* ── Style Panel ──────────────────────────────────────────── */

function StylePanel({ active }: { active: boolean }) {
  const { darkMode, currentTheme, themes, setDarkMode, switchTheme } =
    useEditorStore();

  return (
    <div className={`ribbon-panel${active ? " active" : ""}`}>
      <RibbonGroup label="Theme">
        <select
          className="ribbon-select"
          value={currentTheme}
          onChange={(e) => switchTheme(e.target.value)}
        >
          {themes.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </RibbonGroup>

      <RibbonGroup label="Appearance" separator={false}>
        <RibbonButton
          icon={darkMode ? "fas fa-moon" : "fas fa-sun"}
          label={darkMode ? "Dark" : "Light"}
          onClick={() => setDarkMode(!darkMode)}
          active={darkMode}
          title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
        />
      </RibbonGroup>
    </div>
  );
}

/* ── View Panel ───────────────────────────────────────────── */

function ViewPanel({ active }: { active: boolean }) {
  const { zoomControls, showHitmap, toggleHitmap } = useEditorStore();

  return (
    <div className={`ribbon-panel${active ? " active" : ""}`}>
      <RibbonGroup label="Zoom">
        <RibbonButton
          icon="fas fa-search-minus"
          label="Out"
          onClick={zoomControls?.zoomOut}
        />
        <RibbonButton
          icon="fas fa-compress-arrows-alt"
          label="Fit"
          onClick={zoomControls?.zoomToFit}
        />
        <RibbonButton
          icon="fas fa-search-plus"
          label="In"
          onClick={zoomControls?.zoomIn}
        />
        <RibbonButton
          icon="fas fa-undo-alt"
          label="Reset"
          onClick={zoomControls?.resetView}
        />
      </RibbonGroup>

      <RibbonGroup label="Debug" separator={false}>
        <RibbonButton
          icon="fas fa-bullseye"
          label="Hitmap"
          onClick={toggleHitmap}
          active={showHitmap}
          title="Toggle hit regions"
        />
      </RibbonGroup>
    </div>
  );
}
