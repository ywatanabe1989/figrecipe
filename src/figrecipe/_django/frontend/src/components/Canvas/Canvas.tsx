/**
 * Main canvas — vis_app architecture.
 *
 * Outer container captures zoom/pan events.
 * Inner .vis-rulers-area (3x3 grid) gets CSS transform.
 * Rulers and canvas move as one object.
 */

import { useCallback, useEffect, useRef } from "react";
import { useEditorStore } from "../../store/useEditorStore";
import { BboxOverlay } from "./BboxOverlay";
import { HorizontalRuler, VerticalRuler } from "./Rulers";
import { useZoomPan } from "./useZoomPan";

// ── Constants ────────────────────────────────────────────────
const DPI = 300;
// Canvas = fixed paper size (A4: 210mm x 297mm @ 300 DPI)
const CANVAS_W = Math.round(210 * (DPI / 25.4)); // 2480px
const CANVAS_H = Math.round(297 * (DPI / 25.4)); // 3508px

// ── Main Canvas ──────────────────────────────────────────────
export function Canvas() {
  const { previewImage, imgSize, showHitmap, rulerUnit, toggleRulerUnit } =
    useEditorStore();

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

  // Auto-fit on mount and when image loads
  const didAutoFit = useRef(false);
  useEffect(() => {
    if (!didAutoFit.current || imgSize) {
      didAutoFit.current = true;
      zoomToFit(CANVAS_W, CANVAS_H);
    }
  }, [imgSize, zoomToFit]);

  const handleElementClick = useCallback((elementId: string) => {
    const { bboxes, selectElement } = useEditorStore.getState();
    const bbox =
      bboxes[elementId] ??
      Object.values(bboxes).find(
        (b) => b.label === elementId || b.call_id === elementId,
      );
    selectElement(elementId, bbox);
  }, []);

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
          data-canvas-theme="dark"
          style={{ width: CANVAS_W, height: CANVAS_H }}
        >
          {previewImage ? (
            <>
              <img
                className="canvas-image"
                src={`data:image/png;base64,${previewImage}`}
                alt="Figure preview"
                draggable={false}
                style={
                  imgSize
                    ? { width: imgSize.width, height: imgSize.height }
                    : undefined
                }
              />
              {imgSize && (
                <BboxOverlay
                  onElementClick={handleElementClick}
                  imgWidth={imgSize.width}
                  imgHeight={imgSize.height}
                  alwaysVisible={showHitmap}
                />
              )}
            </>
          ) : (
            <div className="canvas-empty">
              <p>No figure loaded</p>
              <p className="canvas-empty__hint">
                Select a file from the browser or create a new figure
              </p>
            </div>
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
    </div>
  );
}
