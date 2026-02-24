/** Listen for postMessage from parent frame (scitex-cloud integration).
 *
 * Messages:
 *   { type: "figrecipe:switchFile", path: "01_line.yaml" }
 *   { type: "figrecipe:setDarkMode", dark: true }
 */

import { useEffect } from "react";
import { useEditorStore } from "../store/useEditorStore";

export function useEmbeddedMessages(enabled: boolean) {
  useEffect(() => {
    if (!enabled) return;

    const handler = (e: MessageEvent) => {
      const data = e.data;
      if (!data?.type?.startsWith("figrecipe:")) return;

      switch (data.type) {
        case "figrecipe:switchFile":
          if (typeof data.path === "string") {
            useEditorStore.getState().addFigure(data.path);
          }
          break;
        case "figrecipe:setDarkMode":
          if (typeof data.dark === "boolean") {
            useEditorStore.setState({ darkMode: data.dark });
          }
          break;
      }
    };

    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, [enabled]);
}
