/** Center pane — Canvas with figure dropdown, gallery categories, and toolbar.
 * All actions formerly in the Ribbon are now in the pane header toolbar.
 */

import { useState } from "react";
import { redo, undo } from "../../hooks/useUndoRedo";
import { useEditorStore } from "../../store/useEditorStore";
import { Canvas } from "../Canvas/Canvas";
import { ExportDialog } from "../ExportDialog/ExportDialog";
import { GalleryPanel } from "../Gallery/GalleryPanel";

const GALLERY_CATEGORIES = [
  { key: "line", icon: "fa-chart-line", label: "Line" },
  { key: "scatter", icon: "fa-braille", label: "Scatter" },
  { key: "categorical", icon: "fa-chart-bar", label: "Categorical" },
  { key: "distribution", icon: "fa-chart-column", label: "Distribution" },
  { key: "statistical", icon: "fa-square-root-variable", label: "Statistical" },
  { key: "grid", icon: "fa-th", label: "Grid" },
  { key: "area", icon: "fa-chart-area", label: "Area" },
  { key: "contour", icon: "fa-layer-group", label: "Contour" },
  { key: "vector", icon: "fa-arrows-alt", label: "Vector" },
  { key: "special", icon: "fa-shapes", label: "Special" },
] as const;

export function CanvasPane() {
  const {
    placedFigures,
    selectedFigureId,
    save,
    restore,
    darkMode,
    setDarkMode,
    snapEnabled,
    showRulers,
    toggleSnap,
    toggleRulers,
    zoomControls,
    showHitmap,
    toggleHitmap,
  } = useEditorStore();
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [galleryCategory, setGalleryCategory] = useState<string | undefined>();
  const [exportOpen, setExportOpen] = useState(false);

  // Figure label: selected figure name or count
  const selectedFig = placedFigures.find((f) => f.id === selectedFigureId);
  const figLabel = selectedFig
    ? (selectedFig.path.split("/").pop() ?? "figure")
    : placedFigures.length > 0
      ? `${placedFigures.length} figure${placedFigures.length > 1 ? "s" : ""}`
      : "No figures";

  const openGallery = (category?: string) => {
    setGalleryCategory(category);
    setGalleryOpen(true);
  };

  return (
    <>
      {/* Pane header with figure dropdown + toolbar actions */}
      <div className="pane-header">
        {/* Figure dropdown */}
        <div className="figure-dropdown-container">
          <button className="figure-dropdown-toggle" type="button">
            <i className="fas fa-paint-brush" />
            <span className="figure-dropdown-label">{figLabel}</span>
            <i className="fas fa-chevron-down" />
          </button>
          <button
            className="pane-header-btn figure-new-btn"
            type="button"
            title="New from gallery"
            onClick={() => openGallery()}
          >
            <i className="fas fa-plus" />
          </button>
        </div>

        {/* Gallery category buttons */}
        <div className="gallery-categories">
          {GALLERY_CATEGORIES.map((cat) => (
            <button
              key={cat.key}
              className="category-btn"
              data-category={cat.key}
              type="button"
              title={cat.label}
              onClick={() => openGallery(cat.key)}
            >
              <i className={`fas ${cat.icon}`} />
            </button>
          ))}
        </div>

        {/* Toolbar actions (right-aligned) */}
        <div className="pane-header-buttons pane-header-right">
          {/* Undo / Redo */}
          <button
            className="pane-header-btn"
            type="button"
            title="Undo (Ctrl+Z)"
            onClick={undo}
          >
            <i className="fas fa-undo" />
          </button>
          <button
            className="pane-header-btn"
            type="button"
            title="Redo (Ctrl+Shift+Z)"
            onClick={redo}
          >
            <i className="fas fa-redo" />
          </button>

          <span className="toolbar-sep" />

          {/* Snap / Rulers */}
          <button
            className={`pane-header-btn${snapEnabled ? " pane-header-btn--active" : ""}`}
            type="button"
            title={`Snap: ${snapEnabled ? "ON" : "OFF"}`}
            onClick={toggleSnap}
          >
            <i className="fas fa-magnet" />
          </button>
          <button
            className={`pane-header-btn${showRulers ? " pane-header-btn--active" : ""}`}
            type="button"
            title="Toggle rulers"
            onClick={toggleRulers}
          >
            <i className="fas fa-ruler-combined" />
          </button>

          <span className="toolbar-sep" />

          {/* Zoom */}
          <button
            className="pane-header-btn"
            type="button"
            title="Zoom to fit"
            onClick={zoomControls?.zoomToFit}
          >
            <i className="fas fa-compress-arrows-alt" />
          </button>

          {/* Hitmap */}
          <button
            className={`pane-header-btn${showHitmap ? " pane-header-btn--active" : ""}`}
            type="button"
            title="Toggle hit regions (debug)"
            onClick={toggleHitmap}
          >
            <i className="fas fa-bullseye" />
          </button>

          <span className="toolbar-sep" />

          {/* Save / Restore / Export */}
          <button
            className="pane-header-btn"
            type="button"
            title="Save (Ctrl+S)"
            onClick={save}
          >
            <i className="fas fa-save" />
          </button>
          <button
            className="pane-header-btn"
            type="button"
            title="Restore original"
            onClick={restore}
          >
            <i className="fas fa-undo-alt" />
          </button>
          <button
            className="pane-header-btn"
            type="button"
            title="Export (PNG/SVG/PDF)"
            onClick={() => setExportOpen(true)}
          >
            <i className="fas fa-download" />
          </button>

          <span className="toolbar-sep" />

          {/* Theme toggle */}
          <button
            className="pane-header-btn"
            type="button"
            title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            onClick={() => setDarkMode(!darkMode)}
          >
            <i className={darkMode ? "fas fa-moon" : "fas fa-sun"} />
          </button>
        </div>
      </div>

      {/* Canvas content */}
      <div className="pane-content canvas-content">
        <Canvas />
      </div>

      {/* Gallery modal */}
      {galleryOpen && (
        <GalleryPanel
          onClose={() => setGalleryOpen(false)}
          initialCategory={galleryCategory}
        />
      )}

      {/* Export dialog */}
      {exportOpen && <ExportDialog onClose={() => setExportOpen(false)} />}
    </>
  );
}
