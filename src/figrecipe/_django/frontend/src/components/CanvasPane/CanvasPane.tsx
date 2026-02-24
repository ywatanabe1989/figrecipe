/** Center pane — Canvas with figure dropdown + gallery categories.
 * Controls moved to Ribbon: save, download, align, snap, hitmap, dark mode.
 */

import { useState } from "react";
import { useEditorStore } from "../../store/useEditorStore";
import { Canvas } from "../Canvas/Canvas";
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
  const { placedFigures, selectedFigureId } = useEditorStore();
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [galleryCategory, setGalleryCategory] = useState<string | undefined>();

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
      {/* vis_app pane-header for canvas */}
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

        {/* WIP badge */}
        <span className="badge badge-wip">WIP</span>

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
    </>
  );
}
