/** Properties panel — orchestrator for element property editing.
 * Tabs: Current | Preset | Layout | View
 */

import { useCallback, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";
import { StatsOverlay } from "../StatsOverlay/StatsOverlay";
import { AxesPositionSection } from "./AxesPositionSection";
import { LabelsSection } from "./LabelsSection";
import { LegendSection } from "./LegendSection";
import { PropRow } from "./PropRow";
import { PropSection } from "./PropSection";

type TabId = "current" | "preset" | "layout" | "view";

export function Properties() {
  const {
    selectedElement,
    selectedBbox,
    calls: callsMap,
    showToast,
    refreshAfterMutation,
  } = useEditorStore();
  const [activeTab, setActiveTab] = useState<TabId>("current");

  // Read calls from centralized store (loaded by selectElement action)
  const axKey =
    selectedBbox?.ax_index !== undefined ? String(selectedBbox.ax_index) : null;
  const calls = axKey ? (callsMap[axKey] ?? []) : [];

  const matchedCall = calls.find(
    (c) => c.call_id === selectedBbox?.call_id || c.call_id === selectedElement,
  );

  const handleParamUpdate = useCallback(
    async (callId: string, param: string, value: unknown) => {
      try {
        await api.post("update_call", { call_id: callId, param, value });
        refreshAfterMutation();
      } catch (e) {
        showToast(`Update failed: ${e}`, "error");
      }
    },
    [showToast, refreshAfterMutation],
  );

  const axIndex = selectedBbox?.ax_index;

  return (
    <div className="properties-panel">
      {/* Selected element info — or empty state */}
      {selectedElement ? (
        <div className="selected-item-info">
          <div className="selected-item-header">{selectedElement}</div>
          {selectedBbox?.label && selectedBbox.label !== selectedElement && (
            <div className="selected-item-label">{selectedBbox.label}</div>
          )}
        </div>
      ) : (
        <div className="selected-item-info">
          <div className="selected-item-header">
            <i className="fas fa-info-circle" style={{ opacity: 0.5 }} /> No
            selection
          </div>
          <div className="selected-item-label">
            Select an item from the tree to view properties
          </div>
        </div>
      )}

      {/* Tabs — always visible (vis_app pattern) */}
      <div className="properties-tabs">
        <button
          className={`properties-tab${activeTab === "current" ? " active" : ""}`}
          onClick={() => setActiveTab("current")}
          type="button"
        >
          <i className="fas fa-edit" /> Current
        </button>
        <button
          className={`properties-tab${activeTab === "preset" ? " active" : ""}`}
          onClick={() => setActiveTab("preset")}
          type="button"
        >
          <i className="fas fa-palette" /> Preset
        </button>
        <button
          className={`properties-tab${activeTab === "layout" ? " active" : ""}`}
          onClick={() => setActiveTab("layout")}
          type="button"
        >
          <i className="fas fa-th-large" /> Layout
        </button>
        <button
          className={`properties-tab${activeTab === "view" ? " active" : ""}`}
          onClick={() => setActiveTab("view")}
          type="button"
        >
          <i className="fas fa-eye" /> View
        </button>
      </div>

      <div className="properties-content">
        {activeTab === "current" && (
          <>
            {!selectedElement ? null : (
              <>
                {axIndex !== undefined && <LabelsSection axIndex={axIndex} />}
                {axIndex !== undefined && (
                  <AxesPositionSection axIndex={axIndex} />
                )}

                {/* Style — from matched call kwargs */}
                {matchedCall && Object.keys(matchedCall.kwargs).length > 0 && (
                  <PropSection title="Style">
                    {Object.entries(matchedCall.kwargs).map(([key, val]) => {
                      if (val === null || val === undefined) return null;
                      const isColor =
                        typeof val === "string" &&
                        /^#[0-9a-fA-F]{3,8}$/.test(val);
                      const isNumber = typeof val === "number";
                      const isBool = typeof val === "boolean";
                      return (
                        <PropRow
                          key={key}
                          label={key}
                          value={val as string | number | boolean}
                          editable
                          type={
                            isColor
                              ? "color"
                              : isNumber
                                ? "number"
                                : isBool
                                  ? "checkbox"
                                  : "text"
                          }
                          onChange={(v) =>
                            handleParamUpdate(matchedCall.call_id, key, v)
                          }
                        />
                      );
                    })}
                  </PropSection>
                )}

                {axIndex !== undefined && <LegendSection axIndex={axIndex} />}
                {axIndex !== undefined && <StatsOverlay axIndex={axIndex} />}

                {calls.length > 0 && (
                  <PropSection title="Traces" defaultOpen={false}>
                    {calls.map((c) => (
                      <div key={c.call_id} className="trace-item">
                        <span className="trace-label">
                          {c.method} — {c.call_id}
                        </span>
                      </div>
                    ))}
                  </PropSection>
                )}
              </>
            )}
          </>
        )}

        {activeTab === "preset" && selectedElement && (
          <PropSection title="Element Info">
            <PropRow label="ID" value={selectedElement} />
            <PropRow label="Type" value={selectedBbox?.type ?? "unknown"} />
            {selectedBbox?.call_id && (
              <PropRow label="Call ID" value={selectedBbox.call_id} />
            )}
            {axIndex !== undefined && (
              <PropRow label="Panel" value={`Axes ${axIndex}`} />
            )}
          </PropSection>
        )}

        {activeTab === "layout" && <LayoutTab />}
        {activeTab === "view" && <ViewTab />}
      </div>
    </div>
  );
}

/* ── Layout Tab — align, distribute, panels ──────────────── */

function LayoutTab() {
  const {
    alignFigures,
    distributeFigures,
    reorderPanelLetters,
    groupFigures,
    ungroupFigures,
    placedFigures,
    selectedFigureId,
  } = useEditorStore();

  const selectedFig = placedFigures.find((f) => f.id === selectedFigureId);

  return (
    <>
      <PropSection title="Figure Align">
        <div className="details-btn-grid">
          <button
            className="details-btn"
            type="button"
            title="Align left"
            onClick={() => alignFigures("left")}
          >
            <i className="fas fa-align-left" /> Left
          </button>
          <button
            className="details-btn"
            type="button"
            title="Align right"
            onClick={() => alignFigures("right")}
          >
            <i className="fas fa-align-right" /> Right
          </button>
          <button
            className="details-btn"
            type="button"
            title="Align top"
            onClick={() => alignFigures("top")}
          >
            <i className="fas fa-arrow-up" /> Top
          </button>
          <button
            className="details-btn"
            type="button"
            title="Align bottom"
            onClick={() => alignFigures("bottom")}
          >
            <i className="fas fa-arrow-down" /> Bottom
          </button>
          <button
            className="details-btn"
            type="button"
            title="Center horizontal"
            onClick={() => alignFigures("center-h")}
          >
            <i className="fas fa-arrows-alt-h" /> Ctr H
          </button>
          <button
            className="details-btn"
            type="button"
            title="Center vertical"
            onClick={() => alignFigures("center-v")}
          >
            <i className="fas fa-arrows-alt-v" /> Ctr V
          </button>
        </div>
      </PropSection>

      <PropSection title="Axes Align">
        <div className="details-btn-grid">
          <button
            className="details-btn"
            type="button"
            onClick={() => alignFigures("axes-left")}
          >
            <i className="fas fa-align-left" /> Ax Left
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={() => alignFigures("axes-right")}
          >
            <i className="fas fa-align-right" /> Ax Right
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={() => alignFigures("axes-top")}
          >
            <i className="fas fa-arrow-up" /> Ax Top
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={() => alignFigures("axes-bottom")}
          >
            <i className="fas fa-arrow-down" /> Ax Bot
          </button>
        </div>
      </PropSection>

      <PropSection title="Distribute">
        <div className="details-btn-grid">
          <button
            className="details-btn"
            type="button"
            onClick={() => distributeFigures("horizontal")}
          >
            <i className="fas fa-grip-lines-vertical" /> Horizontal
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={() => distributeFigures("vertical")}
          >
            <i className="fas fa-grip-lines" /> Vertical
          </button>
        </div>
      </PropSection>

      <PropSection title="Panels">
        <div className="details-btn-grid">
          <button
            className="details-btn"
            type="button"
            title="Reorder panel letters by position"
            onClick={reorderPanelLetters}
          >
            <i className="fas fa-sort-alpha-down" /> Reorder
          </button>
          <button
            className="details-btn"
            type="button"
            title="Group all figures"
            disabled={placedFigures.length < 2}
            onClick={() => {
              const ids = placedFigures.map((f) => f.id);
              if (ids.length >= 2) groupFigures(ids);
            }}
          >
            <i className="fas fa-object-group" /> Group
          </button>
          <button
            className="details-btn"
            type="button"
            title="Ungroup selected"
            disabled={!selectedFig?.groupId}
            onClick={() => {
              if (selectedFig?.groupId) ungroupFigures(selectedFig.groupId);
            }}
          >
            <i className="fas fa-object-ungroup" /> Ungroup
          </button>
        </div>
      </PropSection>
    </>
  );
}

/* ── View Tab — theme, zoom, guides ──────────────────────── */

function ViewTab() {
  const {
    darkMode,
    currentTheme,
    themes,
    setDarkMode,
    switchTheme,
    snapEnabled,
    showRulers,
    rulerUnit,
    toggleSnap,
    toggleRulers,
    toggleRulerUnit,
    zoomControls,
    showHitmap,
    toggleHitmap,
  } = useEditorStore();

  return (
    <>
      <PropSection title="Theme">
        <div className="property-group" style={{ marginBottom: 12 }}>
          <label className="property-label">Matplotlib Theme</label>
          <select
            className="property-select"
            value={currentTheme}
            onChange={(e) => switchTheme(e.target.value)}
          >
            {themes.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div className="details-btn-grid">
          <button
            className={`details-btn${darkMode ? " details-btn--active" : ""}`}
            type="button"
            onClick={() => setDarkMode(!darkMode)}
          >
            <i className={darkMode ? "fas fa-moon" : "fas fa-sun"} />
            {darkMode ? "Dark" : "Light"}
          </button>
        </div>
      </PropSection>

      <PropSection title="Zoom">
        <div className="details-btn-grid">
          <button
            className="details-btn"
            type="button"
            onClick={zoomControls?.zoomOut}
          >
            <i className="fas fa-search-minus" /> Out
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={zoomControls?.zoomToFit}
          >
            <i className="fas fa-compress-arrows-alt" /> Fit
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={zoomControls?.zoomIn}
          >
            <i className="fas fa-search-plus" /> In
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={zoomControls?.resetView}
          >
            <i className="fas fa-undo-alt" /> Reset
          </button>
        </div>
      </PropSection>

      <PropSection title="Guides">
        <div className="details-btn-grid">
          <button
            className={`details-btn${snapEnabled ? " details-btn--active" : ""}`}
            type="button"
            onClick={toggleSnap}
          >
            <i className="fas fa-magnet" /> Snap {snapEnabled ? "ON" : "OFF"}
          </button>
          <button
            className={`details-btn${showRulers ? " details-btn--active" : ""}`}
            type="button"
            onClick={toggleRulers}
          >
            <i className="fas fa-ruler-combined" /> Rulers
          </button>
          <button
            className="details-btn"
            type="button"
            onClick={toggleRulerUnit}
          >
            <i className="fas fa-ruler" /> {rulerUnit}
          </button>
          <button
            className={`details-btn${showHitmap ? " details-btn--active" : ""}`}
            type="button"
            onClick={toggleHitmap}
          >
            <i className="fas fa-bullseye" /> Hitmap
          </button>
        </div>
      </PropSection>
    </>
  );
}
