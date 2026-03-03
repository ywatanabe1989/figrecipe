/** Properties panel — orchestrator for element property editing. */

import { useCallback, useState } from "react";
import { api } from "../../api/client";
import { useEditorStore } from "../../store/useEditorStore";
import { StatsOverlay } from "../StatsOverlay/StatsOverlay";
import { AxesPositionSection } from "./AxesPositionSection";
import { LabelsSection } from "./LabelsSection";
import { LegendSection } from "./LegendSection";
import { PropRow } from "./PropRow";
import { PropSection } from "./PropSection";

export function Properties() {
  const {
    selectedElement,
    selectedBbox,
    calls: callsMap,
    showToast,
    refreshAfterMutation,
  } = useEditorStore();
  const [activeTab, setActiveTab] = useState<"current" | "preset">("current");

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
      </div>

      <div className="properties-content">
        {!selectedElement ? null : activeTab === "current" ? (
          <>
            {axIndex !== undefined && <LabelsSection axIndex={axIndex} />}
            {axIndex !== undefined && <AxesPositionSection axIndex={axIndex} />}

            {/* Style — from matched call kwargs */}
            {matchedCall && Object.keys(matchedCall.kwargs).length > 0 && (
              <PropSection title="Style">
                {Object.entries(matchedCall.kwargs).map(([key, val]) => {
                  if (val === null || val === undefined) return null;
                  const isColor =
                    typeof val === "string" && /^#[0-9a-fA-F]{3,8}$/.test(val);
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
        ) : (
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
      </div>
    </div>
  );
}
