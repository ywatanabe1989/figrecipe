/** Central Zustand store — single source of truth for the editor. */

import { create } from "zustand";
import { api } from "../api/client";
import type { SnapGuide } from "../hooks/useSnap";
import type {
  BBox,
  ColumnDef,
  FileTreeItem,
  FilesResponse,
  HitmapResponse,
  PlacedFigure,
  PreviewResponse,
  StyleOverrides,
  TabData,
  ThemeInfo,
} from "../types/editor";
import { createFigureActions } from "./figureActions";

interface ZoomControls {
  zoomIn: () => void;
  zoomOut: () => void;
  zoomToFit: () => void;
  resetView: () => void;
}

interface EditorState {
  // ── Canvas figures ──────────────────────────────────────
  placedFigures: PlacedFigure[];
  selectedFigureId: string | null;

  // ── Legacy ──────────────────────────────────────────────
  hitmapImage: string | null;
  colorMap: Record<string, unknown>;
  loading: boolean;

  // ── Selection ───────────────────────────────────────────
  selectedElement: string | null;
  selectedBbox: BBox | null;

  // ── Files ───────────────────────────────────────────────
  files: FileTreeItem[];
  currentFile: string | null;
  workingDir: string | null;

  // ── Data ────────────────────────────────────────────────
  datatableTabs: Record<string, TabData>;
  activeTabId: string | null;

  // ── Style ───────────────────────────────────────────────
  darkMode: boolean;
  currentTheme: string;
  themes: string[];
  overrides: StyleOverrides;

  // ── Panel positions (mm) ────────────────────────────────
  panelPositions: Record<
    string,
    { left: number; top: number; width: number; height: number }
  >;
  figSizeMm: { width: number; height: number } | null;

  // ── Snap ───────────────────────────────────────────────
  snapEnabled: boolean;
  activeSnapGuides: SnapGuide[];

  // ── Zoom / Debug / Rulers / Toast ──────────────────────
  zoomControls: ZoomControls | null;
  showHitmap: boolean;
  showRulers: boolean;
  rulerUnit: "mm" | "inch";
  toast: { message: string; type: "info" | "success" | "error" } | null;

  // ── Actions ─────────────────────────────────────────────
  loadPreview: () => Promise<void>;
  loadHitmap: () => Promise<void>;
  loadFiles: () => Promise<void>;
  loadThemes: () => Promise<void>;
  loadDatatable: () => Promise<void>;
  loadPanelPositions: () => Promise<void>;

  addFigure: (path: string) => Promise<void>;
  removeFigure: (id: string) => void;
  selectFigure: (id: string | null) => void;
  moveFigure: (id: string, x: number, y: number) => void;
  alignFigures: (
    mode:
      | "left"
      | "right"
      | "top"
      | "bottom"
      | "center-h"
      | "center-v"
      | "axes-left"
      | "axes-right"
      | "axes-top"
      | "axes-bottom",
  ) => void;
  distributeFigures: (direction: "horizontal" | "vertical") => void;
  groupFigures: (ids: string[]) => void;
  ungroupFigures: (groupId: string) => void;

  selectElement: (id: string | null, bbox?: BBox, figureId?: string) => void;
  switchFile: (path: string) => Promise<void>;
  switchTheme: (theme: string) => Promise<void>;
  updateOverrides: (overrides: StyleOverrides) => Promise<void>;
  save: () => Promise<void>;
  restore: () => Promise<void>;

  setDarkMode: (dark: boolean) => void;
  toggleHitmap: () => void;
  toggleSnap: () => void;
  toggleRulers: () => void;
  toggleRulerUnit: () => void;
  showToast: (msg: string, type?: "info" | "success" | "error") => void;
  clearToast: () => void;
}

/* eslint-disable @typescript-eslint/no-explicit-any */
export const useEditorStore = create<EditorState>((set, get) => ({
  // ── Initial state ───────────────────────────────────────
  placedFigures: [],
  selectedFigureId: null,
  hitmapImage: null,
  colorMap: {},
  loading: false,
  selectedElement: null,
  selectedBbox: null,
  files: [],
  currentFile: null,
  workingDir: null,
  datatableTabs: {},
  activeTabId: null,
  panelPositions: {},
  figSizeMm: null,
  darkMode: false,
  currentTheme: "SCITEX",
  themes: [],
  overrides: {},
  snapEnabled: true,
  activeSnapGuides: [],
  zoomControls: null,
  showHitmap: false,
  showRulers: true,
  rulerUnit:
    (localStorage.getItem("figrecipe-ruler-unit") as "mm" | "inch") || "mm",
  toast: null,

  // ── Figure actions (from slice) ─────────────────────────
  ...createFigureActions(set as any, get as any),

  // ── Load actions ────────────────────────────────────────
  loadPreview: async () => {
    set({ loading: true });
    try {
      const dark = get().darkMode;
      const data = await api.get<PreviewResponse>(`preview?dark_mode=${dark}`);
      // Sync dark mode from backend on first load
      if (data.dark_mode !== undefined) {
        set({ darkMode: data.dark_mode });
      }
      const { placedFigures, selectedFigureId, currentFile } = get();
      if (placedFigures.length === 0) {
        const fig: PlacedFigure = {
          id: crypto.randomUUID(),
          path: currentFile ?? "preview",
          x: 0,
          y: 0,
          previewImage: data.image,
          bboxes: data.bboxes,
          imgSize: data.img_size,
        };
        set({ placedFigures: [fig], selectedFigureId: fig.id });
      } else if (selectedFigureId) {
        set((s) => ({
          placedFigures: s.placedFigures.map((f) =>
            f.id === selectedFigureId
              ? {
                  ...f,
                  previewImage: data.image,
                  bboxes: data.bboxes,
                  imgSize: data.img_size,
                }
              : f,
          ),
        }));
      }
    } catch (e) {
      console.error("[Editor] Failed to load preview:", e);
      get().showToast("Failed to load preview", "error");
    } finally {
      set({ loading: false });
    }
  },

  loadHitmap: async () => {
    try {
      const data = await api.get<HitmapResponse>("hitmap");
      set({ hitmapImage: data.image, colorMap: data.color_map });
    } catch (e) {
      console.error("[Editor] Failed to load hitmap:", e);
    }
  },

  loadFiles: async () => {
    try {
      const data = await api.get<FilesResponse>("api/files");
      set({
        files: data.tree,
        currentFile: data.current_file,
        workingDir: data.working_dir ?? null,
      });
    } catch (e) {
      console.error("[Editor] Failed to load files:", e);
    }
  },

  loadThemes: async () => {
    try {
      const data = await api.get<ThemeInfo>("list_themes");
      set({ themes: data.themes, currentTheme: data.current });
    } catch (e) {
      console.error("[Editor] Failed to load themes:", e);
    }
  },

  loadDatatable: async () => {
    try {
      const data = await api.get<{
        columns: ColumnDef[];
        rows: (string | number)[][];
      }>("datatable/data");
      const tab: TabData = {
        id: "main",
        label: "Data",
        columns: data.columns ?? [],
        rows: data.rows ?? [],
      };
      set({ datatableTabs: { main: tab }, activeTabId: "main" });
    } catch (e) {
      console.warn("[Editor] No datatable data available:", e);
    }
  },

  loadPanelPositions: async () => {
    try {
      const data = await api.get<Record<string, any>>("get_axes_positions");
      const figsize = data._figsize as
        | { width_mm: number; height_mm: number }
        | undefined;
      const positions: Record<
        string,
        { left: number; top: number; width: number; height: number }
      > = {};
      for (const [key, val] of Object.entries(data)) {
        if (key !== "_figsize" && val && "left" in val) positions[key] = val;
      }
      set({
        panelPositions: positions,
        figSizeMm: figsize
          ? { width: figsize.width_mm, height: figsize.height_mm }
          : null,
      });
    } catch (e) {
      console.warn("[Editor] No panel positions available:", e);
    }
  },

  // ── Selection ───────────────────────────────────────────
  selectElement: (elementId, bbox, figureId) => {
    set({
      selectedElement: elementId,
      selectedBbox: bbox ?? null,
      selectedFigureId: figureId ?? get().selectedFigureId,
    });
  },

  switchFile: async (path) => get().addFigure(path),

  // ── Style actions ───────────────────────────────────────
  switchTheme: async (theme) => {
    set({ loading: true });
    try {
      const data = await api.post<PreviewResponse & { theme: string }>(
        "switch_theme",
        { theme },
      );
      const selId = get().selectedFigureId;
      if (selId) {
        set((s) => ({
          placedFigures: s.placedFigures.map((f) =>
            f.id === selId
              ? {
                  ...f,
                  previewImage: data.image,
                  bboxes: data.bboxes,
                  imgSize: data.img_size,
                }
              : f,
          ),
          currentTheme: theme,
        }));
      } else {
        set({ currentTheme: theme });
      }
      get().showToast(`Theme: ${theme}`, "success");
    } catch (e) {
      console.error("[Editor] Failed to switch theme:", e);
      get().showToast(`Error: ${e}`, "error");
    } finally {
      set({ loading: false });
    }
  },

  updateOverrides: async (overrides) => {
    set({ loading: true });
    try {
      const data = await api.post<PreviewResponse>("update", { overrides });
      const selId = get().selectedFigureId;
      if (selId) {
        set((s) => ({
          placedFigures: s.placedFigures.map((f) =>
            f.id === selId
              ? {
                  ...f,
                  previewImage: data.image,
                  bboxes: data.bboxes,
                  imgSize: data.img_size,
                }
              : f,
          ),
          overrides: { ...get().overrides, ...overrides },
        }));
      }
    } catch (e) {
      console.error("[Editor] Failed to update:", e);
      get().showToast(`Error: ${e}`, "error");
    } finally {
      set({ loading: false });
    }
  },

  save: async () => {
    try {
      await api.post("save", { overrides: get().overrides });
      get().showToast("Saved", "success");
    } catch (e) {
      console.error("[Editor] Failed to save:", e);
      get().showToast(`Error: ${e}`, "error");
    }
  },

  restore: async () => {
    set({ loading: true });
    try {
      const data = await api.post<PreviewResponse>("restore");
      const selId = get().selectedFigureId;
      if (selId) {
        set((s) => ({
          placedFigures: s.placedFigures.map((f) =>
            f.id === selId
              ? {
                  ...f,
                  previewImage: data.image,
                  bboxes: data.bboxes,
                  imgSize: data.img_size,
                }
              : f,
          ),
          overrides: {},
          selectedElement: null,
          selectedBbox: null,
        }));
      }
      get().showToast("Restored to original", "success");
    } catch (e) {
      console.error("[Editor] Failed to restore:", e);
      get().showToast(`Error: ${e}`, "error");
    } finally {
      set({ loading: false });
    }
  },

  // ── UI toggles ──────────────────────────────────────────
  setDarkMode: async (dark) => {
    set({ darkMode: dark });
    // Update backend and re-render with correct text colors
    const data = await api.post<PreviewResponse>("update", { dark_mode: dark });
    if (data?.image) {
      const { selectedFigureId } = get();
      if (selectedFigureId) {
        set((s) => ({
          placedFigures: s.placedFigures.map((f) =>
            f.id === selectedFigureId
              ? {
                  ...f,
                  previewImage: data.image,
                  bboxes: data.bboxes,
                  imgSize: data.img_size,
                }
              : f,
          ),
        }));
      }
    }
  },
  toggleHitmap: () => set((s) => ({ showHitmap: !s.showHitmap })),
  toggleSnap: () => set((s) => ({ snapEnabled: !s.snapEnabled })),
  toggleRulers: () => set((s) => ({ showRulers: !s.showRulers })),
  toggleRulerUnit: () =>
    set((s) => {
      const next = s.rulerUnit === "mm" ? "inch" : "mm";
      localStorage.setItem("figrecipe-ruler-unit", next);
      return { rulerUnit: next };
    }),
  showToast: (message, type = "info") => {
    set({ toast: { message, type } });
    setTimeout(() => set({ toast: null }), 3000);
  },
  clearToast: () => set({ toast: null }),
}));
