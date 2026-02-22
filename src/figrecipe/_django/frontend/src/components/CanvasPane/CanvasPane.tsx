/** Center pane — Canvas with vis_app pane-header (figure dropdown, gallery categories, actions). */

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";
import { Canvas } from "../Canvas/Canvas";

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
    darkMode,
    showHitmap,
    snapEnabled,
    setDarkMode,
    toggleHitmap,
    toggleSnap,
    alignFigures,
    distributeFigures,
    save,
    showToast,
  } = useEditorStore();

  const [downloadOpen, setDownloadOpen] = useState(false);
  const [alignOpen, setAlignOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const alignRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on outside click
  useEffect(() => {
    const close = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setDownloadOpen(false);
      }
      if (alignRef.current && !alignRef.current.contains(e.target as Node)) {
        setAlignOpen(false);
      }
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  const handleDownload = useCallback(
    async (fmt: string) => {
      setDownloadOpen(false);
      try {
        const blob = await api.getBlob(`download/${fmt}`);
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `figure.${fmt}`;
        a.click();
        URL.revokeObjectURL(url);
      } catch (e) {
        showToast(`Download failed: ${e}`, "error");
      }
    },
    [showToast],
  );

  // Figure label: selected figure name or count
  const selectedFig = placedFigures.find((f) => f.id === selectedFigureId);
  const figLabel = selectedFig
    ? (selectedFig.path.split("/").pop() ?? "figure")
    : placedFigures.length > 0
      ? `${placedFigures.length} figure${placedFigures.length > 1 ? "s" : ""}`
      : "No figures";

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
            title="New figure"
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
            >
              <i className={`fas ${cat.icon}`} />
            </button>
          ))}
        </div>

        {/* Right-side action buttons */}
        <div className="pane-header-buttons pane-header-right">
          {/* Snap toggle */}
          <button
            className={`pane-header-btn${snapEnabled ? " pane-header-btn--active" : ""}`}
            onClick={toggleSnap}
            title={`Snap: ${snapEnabled ? "ON" : "OFF"} (Alt to bypass)`}
            type="button"
          >
            <i className="fas fa-magnet" />
          </button>

          {/* Alignment dropdown */}
          <div className="dropdown-container" ref={alignRef}>
            <button
              className="pane-header-btn"
              onClick={() => setAlignOpen(!alignOpen)}
              title="Align & distribute"
              type="button"
            >
              <i className="fas fa-align-left" />
            </button>
            <div
              className={`dropdown-menu dropdown-menu--wide${alignOpen ? " open" : ""}`}
            >
              <div className="dropdown-section-label">Figure edges</div>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("left");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-align-left" /> Align Left
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("right");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-align-right" /> Align Right
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("top");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-arrow-up" /> Align Top
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("bottom");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-arrow-down" /> Align Bottom
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("center-h");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-arrows-alt-h" /> Center Horizontal
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("center-v");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-arrows-alt-v" /> Center Vertical
              </button>
              <div className="dropdown-divider" />
              <div className="dropdown-section-label">Axes edges</div>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("axes-left");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-align-left" style={{ color: "#00bcd4" }} />{" "}
                Axes Left
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("axes-right");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i
                  className="fas fa-align-right"
                  style={{ color: "#00bcd4" }}
                />{" "}
                Axes Right
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("axes-top");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-arrow-up" style={{ color: "#00bcd4" }} />{" "}
                Axes Top
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  alignFigures("axes-bottom");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-arrow-down" style={{ color: "#00bcd4" }} />{" "}
                Axes Bottom
              </button>
              <div className="dropdown-divider" />
              <div className="dropdown-section-label">Distribute</div>
              <button
                className="dropdown-item"
                onClick={() => {
                  distributeFigures("horizontal");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-grip-lines-vertical" /> Distribute H
              </button>
              <button
                className="dropdown-item"
                onClick={() => {
                  distributeFigures("vertical");
                  setAlignOpen(false);
                }}
                type="button"
              >
                <i className="fas fa-grip-lines" /> Distribute V
              </button>
            </div>
          </div>

          {/* Hitmap toggle */}
          <button
            className={`pane-header-btn${showHitmap ? " pane-header-btn--active" : ""}`}
            onClick={toggleHitmap}
            title="Toggle hit regions"
            type="button"
          >
            <i className="fas fa-bullseye" />
          </button>

          {/* Download dropdown */}
          <div className="dropdown-container" ref={dropdownRef}>
            <button
              className="pane-header-btn"
              onClick={() => setDownloadOpen(!downloadOpen)}
              title="Download"
              type="button"
            >
              <i className="fas fa-download" />
            </button>
            <div className={`dropdown-menu${downloadOpen ? " open" : ""}`}>
              <button
                className="dropdown-item"
                onClick={() => handleDownload("png")}
                type="button"
              >
                <i className="fas fa-file-image" /> PNG
                <span className="format-hint">(300 DPI)</span>
              </button>
              <button
                className="dropdown-item"
                onClick={() => handleDownload("svg")}
                type="button"
              >
                <i className="fas fa-file-code" /> SVG
              </button>
              <div className="dropdown-divider" />
              <button
                className="dropdown-item"
                onClick={() => handleDownload("pdf")}
                type="button"
              >
                <i className="fas fa-file-pdf" /> PDF
              </button>
            </div>
          </div>

          {/* Save */}
          <button
            className="pane-header-btn"
            onClick={save}
            title="Save (Ctrl+S)"
            type="button"
          >
            <i className="fas fa-cloud-upload-alt" />
          </button>

          {/* Theme toggle */}
          <button
            className="pane-header-btn"
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? "Switch to light" : "Switch to dark"}
            type="button"
          >
            <span className="theme-icon">🌓</span>
          </button>

          {/* Keyboard shortcuts */}
          <button
            className="pane-header-btn"
            title="Keyboard shortcuts"
            type="button"
          >
            <i className="fas fa-keyboard" />
          </button>
        </div>
      </div>

      {/* Canvas content */}
      <div className="pane-content canvas-content">
        <Canvas />
      </div>
    </>
  );
}
