/** Invisible hitmap overlay for element selection via color lookup. */

import { useCallback, useEffect, useMemo, useRef } from "react";
import { useEditorStore } from "../../store/useEditorStore";

interface Props {
  onElementClick: (elementId: string) => void;
}

export function HitmapOverlay({ onElementClick }: Props) {
  const { hitmapImage, colorMap } = useEditorStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const ctxRef = useRef<CanvasRenderingContext2D | null>(null);

  // Build reverse lookup: hex color string → element key
  // colorMap is { elementKey: { rgb: [r, g, b], label, type, ... } }
  const hexToElementKey = useMemo(() => {
    const map: Record<string, string> = {};
    for (const [key, info] of Object.entries(colorMap)) {
      const rgb = (info as { rgb?: number[] }).rgb;
      if (rgb && rgb.length >= 3) {
        const hex = `#${rgb[0].toString(16).padStart(2, "0")}${rgb[1].toString(16).padStart(2, "0")}${rgb[2].toString(16).padStart(2, "0")}`;
        map[hex] = key;
      }
    }
    return map;
  }, [colorMap]);

  // Draw hitmap onto hidden canvas for pixel color lookup
  useEffect(() => {
    if (!hitmapImage || !canvasRef.current) return;

    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) return;
      ctx.drawImage(img, 0, 0);
      ctxRef.current = ctx;
    };
    img.src = `data:image/png;base64,${hitmapImage}`;
  }, [hitmapImage]);

  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!ctxRef.current) return;

      const rect = e.currentTarget.getBoundingClientRect();
      const canvas = canvasRef.current;
      if (!canvas) return;

      // Map click position to canvas coordinates
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const x = Math.floor((e.clientX - rect.left) * scaleX);
      const y = Math.floor((e.clientY - rect.top) * scaleY);

      const pixel = ctxRef.current.getImageData(x, y, 1, 1).data;
      const hexColor = `#${pixel[0].toString(16).padStart(2, "0")}${pixel[1].toString(16).padStart(2, "0")}${pixel[2].toString(16).padStart(2, "0")}`;

      // Look up element key from hex color reverse map
      const elementKey = hexToElementKey[hexColor];
      if (elementKey) {
        onElementClick(elementKey);
      }
    },
    [hexToElementKey, onElementClick],
  );

  return (
    <>
      <canvas ref={canvasRef} style={{ display: "none" }} />
      <div className="hitmap-overlay" onClick={handleClick} />
    </>
  );
}
