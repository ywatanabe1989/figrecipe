/** Gallery panel — template selector modal.
 * Shows categories + thumbnail grid. Click to add template to canvas.
 */

import { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";

interface GalleryTemplate {
  name: string;
  label: string;
  icon: string;
  path: string;
  has_thumbnail: boolean;
}

interface GalleryData {
  categories: Record<string, GalleryTemplate[]>;
}

const CATEGORY_LABELS: Record<string, { label: string; icon: string }> = {
  line: { label: "Line", icon: "fa-chart-line" },
  scatter: { label: "Scatter", icon: "fa-braille" },
  categorical: { label: "Categorical", icon: "fa-chart-bar" },
  distribution: { label: "Distribution", icon: "fa-chart-column" },
  statistical: { label: "Statistical", icon: "fa-square-root-variable" },
  grid: { label: "Grid", icon: "fa-th" },
  area: { label: "Area", icon: "fa-chart-area" },
  contour: { label: "Contour", icon: "fa-layer-group" },
  special: { label: "Special", icon: "fa-shapes" },
};

interface Props {
  onClose: () => void;
  initialCategory?: string;
}

export function GalleryPanel({ onClose, initialCategory }: Props) {
  const [data, setData] = useState<GalleryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState(
    initialCategory || "all",
  );
  const [thumbnails, setThumbnails] = useState<Record<string, string>>({});
  const { addFigure, showToast } = useEditorStore();

  // Load gallery data
  useEffect(() => {
    api
      .get<GalleryData>("api/gallery")
      .then((d) => {
        setData(d);
        // Auto-select first category if initial not found
        if (initialCategory && !d.categories[initialCategory]) {
          setActiveCategory("all");
        }
      })
      .catch((e) => {
        console.error("[Gallery] Failed to load:", e);
        showToast("Failed to load gallery", "error");
      })
      .finally(() => setLoading(false));
  }, [initialCategory, showToast]);

  // Load thumbnails for visible templates
  useEffect(() => {
    if (!data) return;
    const templates = Object.values(data.categories).flat();
    for (const tmpl of templates) {
      if (tmpl.has_thumbnail && !thumbnails[tmpl.name]) {
        api
          .get<{ image: string }>(`api/gallery/thumbnail/${tmpl.name}`)
          .then((d) => {
            setThumbnails((prev) => ({ ...prev, [tmpl.name]: d.image }));
          })
          .catch(() => {
            /* thumbnail load failure is non-critical */
          });
      }
    }
  }, [data, thumbnails]);

  const handleAdd = useCallback(
    async (tmpl: GalleryTemplate) => {
      try {
        // Copy template to working dir
        const result = await api.post<{ recipe_path: string }>(
          "api/gallery/add",
          { template: tmpl.name },
        );
        // Add the copied recipe to canvas
        await addFigure(result.recipe_path);
        onClose();
      } catch (e) {
        showToast(`Failed to add template: ${e}`, "error");
      }
    },
    [addFigure, onClose, showToast],
  );

  // Close on Escape
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  // Get filtered templates
  const getTemplates = (): GalleryTemplate[] => {
    if (!data) return [];
    if (activeCategory === "all") {
      // Deduplicate by name
      const seen = new Set<string>();
      const all: GalleryTemplate[] = [];
      for (const items of Object.values(data.categories)) {
        for (const item of items) {
          if (!seen.has(item.name)) {
            seen.add(item.name);
            all.push(item);
          }
        }
      }
      return all;
    }
    return data.categories[activeCategory] || [];
  };

  const templates = getTemplates();
  const categoryKeys = data ? Object.keys(data.categories) : [];

  return (
    <div className="gallery-overlay" onMouseDown={onClose}>
      <div className="gallery-panel" onMouseDown={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="gallery-header">
          <h3>
            <i className="fas fa-shapes" /> Template Gallery
          </h3>
          <button className="gallery-close" onClick={onClose} type="button">
            <i className="fas fa-times" />
          </button>
        </div>

        {/* Category tabs */}
        <div className="gallery-categories-bar">
          <button
            className={`gallery-cat-btn${activeCategory === "all" ? " active" : ""}`}
            onClick={() => setActiveCategory("all")}
            type="button"
          >
            All
          </button>
          {categoryKeys.map((key) => {
            const cat = CATEGORY_LABELS[key];
            return (
              <button
                key={key}
                className={`gallery-cat-btn${activeCategory === key ? " active" : ""}`}
                onClick={() => setActiveCategory(key)}
                type="button"
              >
                {cat && <i className={`fas ${cat.icon}`} />}
                {cat?.label || key}
              </button>
            );
          })}
        </div>

        {/* Content */}
        {loading ? (
          <div className="gallery-loading">
            <i className="fas fa-spinner fa-spin" /> Loading templates...
          </div>
        ) : templates.length === 0 ? (
          <div className="gallery-empty">
            <i className="fas fa-inbox" />
            No templates available for this category
          </div>
        ) : (
          <div className="gallery-grid">
            {templates.map((tmpl) => (
              <div
                key={tmpl.name}
                className="gallery-item"
                onClick={() => handleAdd(tmpl)}
                title={`Add ${tmpl.label} to canvas`}
              >
                <div className="gallery-item-thumb">
                  {thumbnails[tmpl.name] ? (
                    <img src={thumbnails[tmpl.name]} alt={tmpl.label} />
                  ) : (
                    <i
                      className={`fas ${tmpl.icon} gallery-icon-placeholder`}
                    />
                  )}
                </div>
                <div className="gallery-item-label">{tmpl.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
