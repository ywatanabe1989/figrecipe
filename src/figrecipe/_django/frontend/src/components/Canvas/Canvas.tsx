/**
 * Main canvas — vis_app architecture.
 *
 * Outer container captures zoom/pan events.
 * Inner .vis-rulers-area (3x3 grid) gets CSS transform.
 * Rulers and canvas move as one object.
 */

import { useCallback, useEffect, useRef } from "react";
import { useContextMenu } from "../../hooks/useContextMenu";
import { CANVAS_H, CANVAS_W, DPI } from "../../hooks/useSnap";
import { useEditorStore } from "../../store/useEditorStore";
import { ContextMenu } from "../ContextMenu/ContextMenu";
import { PlacedFigure } from "./PlacedFigure";
import { HorizontalRuler, VerticalRuler } from "./Rulers";
import { SnapGuides } from "./SnapGuides";
import { useZoomPan } from "./useZoomPan";

// ── Main Canvas ──────────────────────────────────────────────
export function Canvas() {
  const {
    placedFigures,
    rulerUnit,
    toggleRulerUnit,
    selectFigure,
    darkMode,
    activeSnapGuides,
  } = useEditorStore();

  const {
    menu,
    show: showContextMenu,
    hide: hideContextMenu,
  } = useContextMenu();

  const outerRef = useRef<HTMLDivElement>(null);
  const {
    zoom,
    zoomIn,
    zoomOut,
    zoomToFit,
    resetView,
    transformStyle,
    isPanning,
    handleRulerMouseDown,
    handleRulerDoubleClick,
  } = useZoomPan(outerRef);

  // Expose zoom controls to store for toolbar access
  const fitCanvas = useCallback(() => {
    zoomToFit(CANVAS_W, CANVAS_H);
  }, [zoomToFit]);

  useEffect(() => {
    useEditorStore.setState({
      zoomControls: { zoomIn, zoomOut, zoomToFit: fitCanvas, resetView },
    });
  }, [zoomIn, zoomOut, fitCanvas, resetView]);

  // Auto-fit only on first figure load — don't reset view when adding more
  const didAutoFit = useRef(false);
  useEffect(() => {
    if (!didAutoFit.current && placedFigures.length > 0) {
      didAutoFit.current = true;
      zoomToFit(CANVAS_W, CANVAS_H);
    }
  }, [placedFigures.length, zoomToFit]);

  // Click on empty canvas background → deselect
  const handleCanvasClick = useCallback(() => {
    selectFigure(null);
  }, [selectFigure]);

  // Right-click on canvas → context menu (no figure selected)
  const handleCanvasContextMenu = useCallback(
    (e: React.MouseEvent) => {
      showContextMenu(e, null);
    },
    [showContextMenu],
  );

  // Right-click on figure → context menu with figure ID
  const handleFigureContextMenu = useCallback(
    (e: React.MouseEvent, figureId: string) => {
      showContextMenu(e, figureId);
    },
    [showContextMenu],
  );

  return (
    <div
      className={`canvas-outer${isPanning ? " panning" : ""}`}
      ref={outerRef}
    >
      {/* The entire rulers-area transforms together (vis_app architecture) */}
      <div className="vis-rulers-area" style={transformStyle}>
        {/* Top row: corner-tl | ruler-h | corner-tr */}
        <div
          className="ruler-corner ruler-corner--tl"
          onClick={toggleRulerUnit}
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
          title={`Units: ${rulerUnit} (click to toggle)`}
        >
          {rulerUnit}
        </div>
        <HorizontalRuler
          canvasWidth={CANVAS_W}
          dpi={DPI}
          gridArea="ruler-h"
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
        />
        <div
          className="ruler-corner ruler-corner--tr"
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
        />

        {/* Middle row: ruler-v | canvas | ruler-r */}
        <VerticalRuler
          canvasHeight={CANVAS_H}
          dpi={DPI}
          gridArea="ruler-v"
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
        />
        <div
          className="vis-canvas-container"
          data-canvas-theme={darkMode ? "dark" : "light"}
          style={{ width: CANVAS_W, height: CANVAS_H }}
          onClick={handleCanvasClick}
          onContextMenu={handleCanvasContextMenu}
        >
          {placedFigures.length === 0 ? (
            <div className="canvas-empty">
              <p>No figure loaded</p>
              <p className="canvas-empty__hint">
                Select a file from the browser or create a new figure
              </p>
            </div>
          ) : (
            <>
              {placedFigures.map((fig, idx) => (
                <PlacedFigure
                  key={fig.id}
                  figure={fig}
                  zoom={zoom}
                  figureIndex={idx}
                  onContextMenu={handleFigureContextMenu}
                />
              ))}
              <SnapGuides
                guides={activeSnapGuides}
                canvasWidth={CANVAS_W}
                canvasHeight={CANVAS_H}
              />
            </>
          )}
        </div>
        <VerticalRuler
          canvasHeight={CANVAS_H}
          dpi={DPI}
          gridArea="ruler-r"
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
        />

        {/* Bottom row: corner-bl | ruler-b | corner-br */}
        <div
          className="ruler-corner ruler-corner--bl"
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
        />
        <HorizontalRuler
          canvasWidth={CANVAS_W}
          dpi={DPI}
          gridArea="ruler-b"
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
        />
        <div
          className="ruler-corner ruler-corner--br"
          onMouseDown={handleRulerMouseDown}
          onDoubleClick={handleRulerDoubleClick}
        />
      </div>

      {/* Zoom indicator — fixed in outer container */}
      <div className="canvas-zoom-indicator visible">
        {Math.round(zoom * 100)}%
      </div>

      {/* Context menu overlay */}
      {menu.visible && (
        <ContextMenu
          x={menu.x}
          y={menu.y}
          figureId={menu.figureId}
          onClose={hideContextMenu}
        />
      )}
    </div>
  );
}
