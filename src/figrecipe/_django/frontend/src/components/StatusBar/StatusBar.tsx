/** Status bar — bottom bar with canvas info, zoom %, selection info. */

import { useEditorStore } from "../../store/useEditorStore";

export function StatusBar() {
  const {
    placedFigures,
    selectedFigureId,
    snapEnabled,
    showRulers,
    rulerUnit,
    figSizeMm,
  } = useEditorStore();

  const selectedFig = placedFigures.find((f) => f.id === selectedFigureId);

  return (
    <div className="status-bar">
      {/* Left: canvas info */}
      <div className="status-bar-left">
        <span className="status-item">
          <i className="fas fa-images" />
          {placedFigures.length} figure
          {placedFigures.length !== 1 ? "s" : ""}
        </span>
        {figSizeMm && (
          <span className="status-item">
            <i className="fas fa-expand-alt" />
            {figSizeMm.width.toFixed(0)} x {figSizeMm.height.toFixed(0)} mm
          </span>
        )}
      </div>

      {/* Center: selection info */}
      <div className="status-bar-center">
        {selectedFig ? (
          <span className="status-item status-selected">
            <i className="fas fa-mouse-pointer" />
            {selectedFig.path.split("/").pop()}
            {selectedFig.groupId && (
              <span className="status-group-badge">grouped</span>
            )}
          </span>
        ) : (
          <span className="status-item status-hint">No selection</span>
        )}
      </div>

      {/* Right: toggles + position */}
      <div className="status-bar-right">
        <span
          className={`status-item status-toggle${snapEnabled ? " active" : ""}`}
        >
          <i className="fas fa-magnet" /> Snap
        </span>
        <span
          className={`status-item status-toggle${showRulers ? " active" : ""}`}
        >
          <i className="fas fa-ruler" /> {rulerUnit}
        </span>
        {selectedFig && (
          <span className="status-item">
            x:{selectedFig.x.toFixed(0)} y:{selectedFig.y.toFixed(0)}
          </span>
        )}
      </div>
    </div>
  );
}
