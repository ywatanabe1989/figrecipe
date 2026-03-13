/** Vertical plot-type selector nav — fixed width, never collapses.
 * Sits between DataTable and Canvas panes, matching scitex-cloud app selector pattern.
 */

import { useState } from "react";
import { useEditorStore } from "../../store/useEditorStore";
import { GalleryPanel } from "../Gallery/GalleryPanel";

const PLOT_TYPES = [
  { key: "line", icon: "fa-chart-line", label: "Line" },
  { key: "scatter", icon: "fa-braille", label: "Scatter" },
  { key: "categorical", icon: "fa-chart-bar", label: "Bar" },
  { key: "distribution", icon: "fa-chart-column", label: "Dist" },
  { key: "statistical", icon: "fa-square-root-variable", label: "Stats" },
  { key: "grid", icon: "fa-th", label: "Grid" },
  { key: "area", icon: "fa-chart-area", label: "Area" },
  { key: "contour", icon: "fa-layer-group", label: "Contour" },
  { key: "vector", icon: "fa-arrows-alt", label: "Vector" },
  { key: "special", icon: "fa-shapes", label: "Special" },
] as const;

export function PlotTypeNav() {
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [galleryCategory, setGalleryCategory] = useState<string | undefined>();
  const { placedFigures } = useEditorStore();

  const openGallery = (category: string) => {
    setGalleryCategory(category);
    setGalleryOpen(true);
  };

  return (
    <>
      <nav className="plot-type-nav">
        <div className="plot-type-nav__header">
          <i className="fas fa-plus" />
        </div>

        <div className="plot-type-nav__items">
          {PLOT_TYPES.map((pt) => (
            <button
              key={pt.key}
              className="plot-type-nav__item"
              type="button"
              title={pt.label}
              onClick={() => openGallery(pt.key)}
            >
              <i className={`fas ${pt.icon}`} />
              <span className="plot-type-nav__label">{pt.label}</span>
            </button>
          ))}
        </div>

        <div className="plot-type-nav__footer">
          <span className="plot-type-nav__count">{placedFigures.length}</span>
        </div>
      </nav>

      {galleryOpen && (
        <GalleryPanel
          onClose={() => setGalleryOpen(false)}
          initialCategory={galleryCategory}
        />
      )}
    </>
  );
}
