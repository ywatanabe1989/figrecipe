/**
 * Element Inspector — Visual debugging tool for the figrecipe editor.
 * Port of scitex-cloud's ElementInspector.
 *
 * Shortcuts:
 *   Alt+I         — Toggle inspector overlay (colored rectangles over all elements)
 *   Alt+Shift+I   — Copy debug info for element under cursor
 *   Escape        — Deactivate inspector
 *   Right-click   — Copy hovered element's debug info (when active)
 */

import { useEffect, useRef } from "react";

// ── Color palette by DOM depth ────────────────────────────
const DEPTH_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#EC4899"];

function colorForDepth(depth: number): string {
  return DEPTH_COLORS[Math.min(Math.floor(depth / 3), DEPTH_COLORS.length - 1)];
}

function getDepth(el: Element): number {
  let d = 0;
  let cur: Element | null = el;
  while (cur && cur !== document.body) {
    d++;
    cur = cur.parentElement;
  }
  return d;
}

// ── CSS selector builder ──────────────────────────────────
function buildSelector(el: Element): string {
  const tag = el.tagName.toLowerCase();
  const id = el.id ? `#${el.id}` : "";
  const cls =
    typeof el.className === "string" && el.className.trim()
      ? `.${el.className.trim().split(/\s+/).join(".")}`
      : "";
  return `${tag}${id}${cls}`;
}

function getXPath(el: Element): string {
  if (el.id) return `//*[@id="${el.id}"]`;
  const parts: string[] = [];
  let cur: Element | null = el;
  while (cur && cur.nodeType === Node.ELEMENT_NODE) {
    let idx = 0;
    let sib = cur.previousSibling;
    while (sib) {
      if (sib.nodeType === Node.ELEMENT_NODE && sib.nodeName === cur.nodeName)
        idx++;
      sib = sib.previousSibling;
    }
    parts.unshift(cur.nodeName.toLowerCase() + (idx > 0 ? `[${idx + 1}]` : ""));
    cur = cur.parentElement;
  }
  return "/" + parts.join("/");
}

// ── Debug info collector ──────────────────────────────────
function gatherDebugInfo(el: Element): string {
  const tag = el.tagName.toLowerCase();
  const rect = el.getBoundingClientRect();
  const computed =
    el instanceof HTMLElement ? window.getComputedStyle(el) : null;

  const attrs: string[] = [];
  for (let i = 0; i < el.attributes.length; i++) {
    const a = el.attributes[i];
    attrs.push(`- ${a.name}: ${a.value}`);
  }

  const styles = computed
    ? [
        "display",
        "position",
        "width",
        "height",
        "margin",
        "padding",
        "backgroundColor",
        "color",
        "fontSize",
        "fontFamily",
        "zIndex",
        "opacity",
        "visibility",
        "overflow",
      ]
        .map(
          (k) =>
            `- ${k}: ${computed.getPropertyValue(k.replace(/[A-Z]/g, (m) => "-" + m.toLowerCase())) || (computed as any)[k]}`,
        )
        .join("\n")
    : "N/A";

  const parents: string[] = [];
  let p = el.parentElement;
  let depth = 0;
  while (p && depth < 5) {
    parents.push(`${depth + 1}. ${buildSelector(p)}`);
    p = p.parentElement;
    depth++;
  }

  const sheets: string[] = [];
  for (let i = 0; i < Math.min(document.styleSheets.length, 10); i++) {
    try {
      sheets.push(`${i + 1}. ${document.styleSheets[i].href || "<inline>"}`);
    } catch {
      sheets.push(`${i + 1}. <cross-origin>`);
    }
  }

  const rules: string[] = [];
  for (let i = 0; i < document.styleSheets.length; i++) {
    try {
      const sheet = document.styleSheets[i];
      if (!sheet.cssRules) continue;
      for (let j = 0; j < sheet.cssRules.length; j++) {
        const rule = sheet.cssRules[j];
        if (rule instanceof CSSStyleRule) {
          try {
            if (el.matches(rule.selectorText)) {
              const css =
                rule.cssText.length > 200
                  ? rule.cssText.substring(0, 200) + "..."
                  : rule.cssText;
              rules.push(
                `\n### ${rules.length + 1}. ${rule.selectorText}\n` +
                  `- Source: ${sheet.href || "<inline style>"}\n` +
                  `- Rule Index: ${j}\n` +
                  `- CSS: ${css}\n`,
              );
            }
          } catch {
            /* invalid selector */
          }
        }
      }
    } catch {
      /* CORS */
    }
  }

  const content =
    el instanceof HTMLElement
      ? (el.textContent?.substring(0, 200) || "").trim()
      : "";

  return `# Element Debug Information

## Page Context
- URL: ${window.location.href}
- Timestamp: ${new Date().toISOString()}

## Element Identification
- Tag: <${tag}>
- ID: ${el.id || "none"}
- Classes: ${typeof el.className === "string" ? el.className || "none" : "none"}
- CSS Selector: ${buildSelector(el)}
- XPath: ${getXPath(el)}

## Attributes
${attrs.length > 0 ? attrs.join("\n") : "none"}

## Computed Styles
${styles}

## Dimensions & Position
- Width: ${rect.width}
- Height: ${rect.height}
- Top: ${rect.top}
- Left: ${rect.left}

## Scroll State
- scrollTop: ${el instanceof HTMLElement ? el.scrollTop : 0}
- scrollLeft: ${el instanceof HTMLElement ? el.scrollLeft : 0}

## Content (truncated)
${content || "none"}

## Event Listeners
none detected

## Parent Chain
${parents.join("\n")}

## Applied Stylesheets
${sheets.join("\n")}

## Matching CSS Rules (${rules.length} rules)
${rules.length > 0 ? rules.join("\n") : "No matching rules found"}

---
This debug information was captured by Element Inspector and can be used for AI-assisted debugging.
Note: Exact CSS line numbers require browser DevTools API access.
`;
}

// ── Notification helper ───────────────────────────────────
function showNotification(msg: string, type: "success" | "error") {
  const n = document.createElement("div");
  n.textContent = msg;
  n.style.cssText = `
    position:fixed;top:16px;right:16px;padding:10px 20px;
    background:${type === "success" ? "rgba(16,185,129,0.95)" : "rgba(239,68,68,0.95)"};
    color:white;border-radius:6px;font-size:13px;font-weight:600;
    z-index:10000000;box-shadow:0 4px 12px rgba(0,0,0,0.25);
    opacity:0;transform:translateY(-10px) scale(0.95);
    transition:opacity 0.2s ease,transform 0.2s ease;
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  `;
  document.body.appendChild(n);
  requestAnimationFrame(() => {
    n.style.opacity = "1";
    n.style.transform = "translateY(0) scale(1)";
  });
  setTimeout(() => {
    n.style.opacity = "0";
    n.style.transform = "translateY(-10px) scale(0.95)";
    setTimeout(() => n.remove(), 200);
  }, 1200);
}

// ── Main hook ─────────────────────────────────────────────
export function useElementInspector(): void {
  const activeRef = useRef(false);
  const overlayRef = useRef<HTMLDivElement | null>(null);
  const boxMapRef = useRef<Map<HTMLDivElement, Element>>(new Map());

  useEffect(() => {
    const SKIP_TAGS = new Set([
      "script",
      "style",
      "link",
      "meta",
      "head",
      "noscript",
      "br",
      "html",
    ]);

    function scanElements(container: HTMLDivElement) {
      const all = document.querySelectorAll("*");
      let count = 0;
      const maxElements = 512;

      all.forEach((el) => {
        if (count >= maxElements) return;
        if (el.closest("#element-inspector-overlay")) return;
        if (SKIP_TAGS.has(el.tagName.toLowerCase())) return;

        if (el instanceof HTMLElement) {
          const cs = window.getComputedStyle(el);
          if (cs.display === "none" || cs.visibility === "hidden") return;
        }

        const rect = el.getBoundingClientRect();
        if (rect.width < 5 || rect.height < 5) return;

        const depth = getDepth(el);
        const color = colorForDepth(depth);

        const box = document.createElement("div");
        box.className = "ei-box";
        box.style.cssText = `
          position:absolute;
          left:${rect.left + window.scrollX}px;
          top:${rect.top + window.scrollY}px;
          width:${rect.width}px;
          height:${rect.height}px;
          border:2px solid ${color};
          background:rgba(255,255,255,0.01);
          pointer-events:all;
          cursor:crosshair;
          box-sizing:border-box;
          transition:background 0.1s,border-width 0.1s;
        `;

        // Label
        const label = document.createElement("span");
        label.className = "ei-label";
        label.textContent = buildSelector(el).substring(0, 40);
        label.style.cssText = `
          position:absolute;top:-16px;left:0;
          font-size:9px;color:${color};background:rgba(0,0,0,0.8);
          padding:1px 4px;border-radius:2px;white-space:nowrap;
          pointer-events:none;opacity:0;transition:opacity 0.15s;
        `;
        box.appendChild(label);

        // Hover
        box.addEventListener("mouseenter", () => {
          box.style.borderWidth = "3px";
          box.style.background = `${color}22`;
          label.style.opacity = "1";
        });
        box.addEventListener("mouseleave", () => {
          box.style.borderWidth = "2px";
          box.style.background = "rgba(255,255,255,0.01)";
          label.style.opacity = "0";
        });

        // Right-click → copy debug info
        box.addEventListener("contextmenu", async (e) => {
          e.preventDefault();
          e.stopPropagation();
          const info = gatherDebugInfo(el);
          try {
            await navigator.clipboard.writeText(info);
            showNotification("Copied element debug info", "success");
          } catch {
            showNotification("Copy failed", "error");
          }
          deactivate();
        });

        // Left-click → pass through
        box.addEventListener("click", (e) => {
          e.stopPropagation();
          box.style.pointerEvents = "none";
          const target = document.elementFromPoint(e.clientX, e.clientY);
          box.style.pointerEvents = "all";
          if (target && target instanceof HTMLElement) {
            target.click();
          }
        });

        container.appendChild(box);
        boxMapRef.current.set(box, el);
        count++;
      });
    }

    function activate() {
      if (activeRef.current) return;
      activeRef.current = true;

      const docHeight = Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight,
      );

      const overlay = document.createElement("div");
      overlay.id = "element-inspector-overlay";
      overlay.style.cssText = `
        position:absolute;top:0;left:0;width:100%;height:${docHeight}px;
        pointer-events:none;z-index:999999;
      `;
      document.body.appendChild(overlay);
      overlayRef.current = overlay;

      scanElements(overlay);
      showNotification(
        "Inspector ON — right-click to copy, Esc to exit",
        "success",
      );
    }

    function deactivate() {
      if (!activeRef.current) return;
      activeRef.current = false;
      boxMapRef.current.clear();
      if (overlayRef.current) {
        overlayRef.current.remove();
        overlayRef.current = null;
      }
    }

    async function inspectUnderCursor(_e: KeyboardEvent) {
      // Alt+Shift+I: copy debug info for element at last known position
      const els = document.elementsFromPoint(
        (window as any).__eiLastX ?? window.innerWidth / 2,
        (window as any).__eiLastY ?? window.innerHeight / 2,
      );
      // Skip our overlay elements
      const target = els.find(
        (el) =>
          !el.closest("#element-inspector-overlay") &&
          el.tagName !== "HTML" &&
          el.tagName !== "BODY",
      );
      if (target) {
        const info = gatherDebugInfo(target);
        try {
          await navigator.clipboard.writeText(info);
          showNotification("Copied debug info", "success");
        } catch {
          showNotification("Copy failed", "error");
        }
      }
    }

    // Track mouse position for Alt+Shift+I
    function trackMouse(e: MouseEvent) {
      (window as any).__eiLastX = e.clientX;
      (window as any).__eiLastY = e.clientY;
    }

    function onKeyDown(e: KeyboardEvent) {
      const key = e.key.toLowerCase();

      // Alt+Shift+I: Copy debug info for element under cursor
      if (e.altKey && e.shiftKey && !e.ctrlKey && key === "i") {
        e.preventDefault();
        inspectUnderCursor(e);
        return;
      }

      // Alt+I: Toggle inspector
      if (e.altKey && !e.shiftKey && !e.ctrlKey && key === "i") {
        e.preventDefault();
        if (activeRef.current) {
          deactivate();
        } else {
          activate();
        }
        return;
      }

      // Escape: Deactivate
      if (e.key === "Escape" && activeRef.current) {
        e.preventDefault();
        deactivate();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("mousemove", trackMouse);

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousemove", trackMouse);
      deactivate();
    };
  }, []);
}
