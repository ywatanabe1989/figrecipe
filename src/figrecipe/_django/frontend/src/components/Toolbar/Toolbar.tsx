/** Top toolbar — theme, zoom, save/restore, download, keyboard shortcuts. */

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";

export function Toolbar() {
  const {
    darkMode,
    currentTheme,
    themes,
    zoomControls,
    showHitmap,
    rulerUnit,
    setDarkMode,
    switchTheme,
    toggleHitmap,
    toggleRulerUnit,
    save,
    restore,
    showToast,
  } = useEditorStore();

  const [downloadOpen, setDownloadOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const close = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setDownloadOpen(false);
      }
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const mod = e.ctrlKey || e.metaKey;

      // Ctrl+S — save
      if (mod && e.key === "s") {
        e.preventDefault();
        save();
        return;
      }

      // Ctrl+Z — restore (undo all)
      if (mod && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        restore();
        return;
      }

      // Escape — deselect
      if (e.key === "Escape") {
        useEditorStore.getState().selectElement(null);
        return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [save, restore]);

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

  return (
    <div className="toolbar">
      <div className="toolbar__left">
        <span className="toolbar__title">FigRecipe Editor</span>
      </div>

      <div className="toolbar__center">
        {/* Theme selector */}
        <select
          className="toolbar__select"
          value={currentTheme}
          onChange={(e) => switchTheme(e.target.value)}
        >
          {themes.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>

        {/* Zoom controls */}
        <div className="toolbar__zoom">
          <button
            className="toolbar__btn"
            onClick={zoomControls?.zoomOut}
            title="Zoom out"
          >
            -
          </button>
          <button
            className="toolbar__btn"
            onClick={zoomControls?.zoomToFit}
            title="Fit to screen"
          >
            Fit
          </button>
          <button
            className="toolbar__btn"
            onClick={zoomControls?.zoomIn}
            title="Zoom in"
          >
            +
          </button>
        </div>

        <label className="toolbar__toggle">
          <input
            type="checkbox"
            checked={darkMode}
            onChange={(e) => setDarkMode(e.target.checked)}
          />
          <span>Dark</span>
        </label>

        <button
          className="toolbar__btn"
          onClick={toggleRulerUnit}
          title={`Ruler unit: ${rulerUnit} (click to toggle)`}
        >
          {rulerUnit === "mm" ? "mm" : "inch"}
        </button>

        <button
          className={`toolbar__btn${showHitmap ? " toolbar__btn--active" : ""}`}
          onClick={toggleHitmap}
          title="Show hitmap areas (debug)"
        >
          Hitmap
        </button>
      </div>

      <div className="toolbar__right">
        <button
          className="toolbar__btn"
          onClick={save}
          title="Save overrides (Ctrl+S)"
        >
          Save
        </button>
        <button
          className="toolbar__btn"
          onClick={restore}
          title="Restore original (Ctrl+Z)"
        >
          Restore
        </button>

        {/* Download dropdown */}
        <div className="dropdown-container" ref={dropdownRef}>
          <button
            className="toolbar__btn"
            onClick={() => setDownloadOpen(!downloadOpen)}
            title="Download"
          >
            Download
          </button>
          <div className={`dropdown-menu ${downloadOpen ? "open" : ""}`}>
            <button
              className="dropdown-item"
              onClick={() => handleDownload("png")}
            >
              PNG
            </button>
            <button
              className="dropdown-item"
              onClick={() => handleDownload("svg")}
            >
              SVG
            </button>
            <div className="dropdown-divider" />
            <button
              className="dropdown-item"
              onClick={() => handleDownload("pdf")}
            >
              PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
