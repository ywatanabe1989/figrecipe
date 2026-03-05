/** Session persistence — auto-save/restore canvas layout to localStorage.
 * Saves: figure positions, groups, captions, zoom level.
 * Auto-saves every 30s. Restores on mount.
 */

import { useEffect, useRef } from "react";
import { useEditorStore } from "../store/useEditorStore";

const STORAGE_KEY = "figrecipe-session";
const AUTO_SAVE_INTERVAL = 30_000; // 30s

interface SessionData {
  timestamp: number;
  figures: Array<{
    id: string;
    path: string;
    x: number;
    y: number;
    groupId?: string;
  }>;
  selectedFigureId: string | null;
  overrides: Record<string, unknown>;
  darkMode: boolean;
  snapEnabled: boolean;
  showRulers: boolean;
  rulerUnit: "mm" | "inch";
}

function buildSessionData(): SessionData {
  const state = useEditorStore.getState();
  return {
    timestamp: Date.now(),
    figures: state.placedFigures.map((f) => ({
      id: f.id,
      path: f.path,
      x: f.x,
      y: f.y,
      groupId: f.groupId,
    })),
    selectedFigureId: state.selectedFigureId,
    overrides: state.overrides,
    darkMode: state.darkMode,
    snapEnabled: state.snapEnabled,
    showRulers: state.showRulers,
    rulerUnit: state.rulerUnit,
  };
}

function saveSession(): void {
  try {
    const data = buildSessionData();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    // localStorage full or unavailable — non-critical
  }
}

function loadSession(): SessionData | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as SessionData;
  } catch {
    return null;
  }
}

export function clearSession(): void {
  localStorage.removeItem(STORAGE_KEY);
}

export function useSessionPersistence() {
  const initialized = useRef(false);

  // Restore session on mount (only applies UI preferences, not figures)
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const session = loadSession();
    if (!session) return;

    // Restore UI preferences
    const state = useEditorStore.getState();
    if (session.darkMode !== state.darkMode) {
      state.setDarkMode(session.darkMode);
    }
    if (session.snapEnabled !== state.snapEnabled) {
      state.toggleSnap();
    }
    if (session.showRulers !== state.showRulers) {
      state.toggleRulers();
    }
  }, []);

  // Auto-save interval
  useEffect(() => {
    const timer = setInterval(saveSession, AUTO_SAVE_INTERVAL);
    return () => clearInterval(timer);
  }, []);

  // Save on beforeunload
  useEffect(() => {
    const handleUnload = () => saveSession();
    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, []);
}
