/** Central Zustand store — single source of truth for the editor. */

import { create } from "zustand";
import { api } from "../api/client";
import type {
  BBox,
  ColumnDef,
  FileTreeItem,
  FilesResponse,
  HitmapResponse,
  ImgSize,
  PreviewResponse,
  StyleOverrides,
  TabData,
  ThemeInfo,
} from "../types/editor";

interface ZoomControls {
  zoomIn: () => void;
  zoomOut: () => void;
  zoomToFit: () => void;
  resetView: () => void;
}

interface EditorState {
  // ── Core ──────────────────────────────────────────────────
  previewImage: string | null;
  hitmapImage: string | null;
  colorMap: Record<string, unknown>;
  bboxes: Record<string, BBox>;
  imgSize: ImgSize | null;
  loading: boolean;

  // ── Selection ─────────────────────────────────────────────
  selectedElement: string | null;
  selectedBbox: BBox | null;

  // ── Files ─────────────────────────────────────────────────
  files: FileTreeItem[];
  currentFile: string | null;
  workingDir: string | null;

  // ── Data ──────────────────────────────────────────────────
  datatableTabs: Record<string, TabData>;
  activeTabId: string | null;

  // ── Style ─────────────────────────────────────────────────
  darkMode: boolean;
  currentTheme: string;
  themes: string[];
  overrides: StyleOverrides;

  // ── Panel positions (mm) ─────────────────────────────────
  panelPositions: Record<
    string,
    { left: number; top: number; width: number; height: number }
  >;
  figSizeMm: { width: number; height: number } | null;

  // ── Zoom ────────────────────────────────────────────────
  zoomControls: ZoomControls | null;

  // ── Debug ─────────────────────────────────────────────────
  showHitmap: boolean;
  showRulers: boolean;

  // ── Rulers ──────────────────────────────────────────────
  rulerUnit: "mm" | "inch";

  // ── Toast ─────────────────────────────────────────────────
  toast: { message: string; type: "info" | "success" | "error" } | null;

  // ── Actions ───────────────────────────────────────────────
  loadPreview: () => Promise<void>;
  loadHitmap: () => Promise<void>;
  loadFiles: () => Promise<void>;
  loadThemes: () => Promise<void>;
  loadDatatable: () => Promise<void>;
  loadPanelPositions: () => Promise<void>;

  selectElement: (elementId: string | null, bbox?: BBox) => void;
  switchFile: (path: string) => Promise<void>;
  switchTheme: (theme: string) => Promise<void>;

  updateOverrides: (overrides: StyleOverrides) => Promise<void>;
  save: () => Promise<void>;
  restore: () => Promise<void>;

  setDarkMode: (dark: boolean) => void;
  toggleHitmap: () => void;
  toggleRulers: () => void;
  toggleRulerUnit: () => void;
  showToast: (message: string, type?: "info" | "success" | "error") => void;
  clearToast: () => void;
}

export const useEditorStore = create<EditorState>((set, get) => ({
  // ── Initial state ─────────────────────────────────────────
  previewImage: null,
  hitmapImage: null,
  colorMap: {},
  bboxes: {},
  imgSize: null,
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

  zoomControls: null,

  showHitmap: false,
  showRulers: true,
  rulerUnit:
    (localStorage.getItem("figrecipe-ruler-unit") as "mm" | "inch") || "mm",

  toast: null,

  // ── Actions ───────────────────────────────────────────────

  loadPreview: async () => {
    set({ loading: true });
    try {
      const data = await api.get<PreviewResponse>("preview");
      set({
        previewImage: data.image,
        bboxes: data.bboxes,
        imgSize: data.img_size,
      });
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
      set({
        hitmapImage: data.image,
        colorMap: data.color_map,
      });
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
      set({
        themes: data.themes,
        currentTheme: data.current,
      });
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
      const data = await api.get<
        Record<
          string,
          | {
              index: number;
              left: number;
              top: number;
              width: number;
              height: number;
            }
          | { width_mm: number; height_mm: number }
        >
      >("get_axes_positions");
      const figsize = data._figsize as
        | { width_mm: number; height_mm: number }
        | undefined;
      const positions: Record<
        string,
        { left: number; top: number; width: number; height: number }
      > = {};
      for (const [key, val] of Object.entries(data)) {
        if (key !== "_figsize" && val && "left" in val) {
          positions[key] = val;
        }
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

  selectElement: (elementId, bbox) => {
    set({
      selectedElement: elementId,
      selectedBbox: bbox ?? null,
    });
  },

  switchFile: async (path) => {
    // If no recipe is currently loaded, navigate to the recipe URL
    const params = new URLSearchParams(window.location.search);
    if (!params.get("recipe")) {
      // Compute the full recipe path relative to the working dir
      const workingDir = get().workingDir;
      const fullPath = workingDir ? `${workingDir}/${path}` : path;
      params.set("recipe", fullPath);
      window.location.search = params.toString();
      return;
    }

    set({ loading: true });
    try {
      const data = await api.post<
        PreviewResponse & { color_map?: Record<string, unknown> }
      >("api/switch", { path });
      set({
        previewImage: data.image,
        bboxes: data.bboxes,
        imgSize: data.img_size,
        currentFile: path,
        selectedElement: null,
        selectedBbox: null,
      });
      if (data.color_map) {
        set({ colorMap: data.color_map });
      }
      get().showToast(`Loaded: ${path}`, "success");
      get().loadFiles();
    } catch (e) {
      console.error("[Editor] Failed to switch file:", e);
      get().showToast(`Error: ${e}`, "error");
    } finally {
      set({ loading: false });
    }
  },

  switchTheme: async (theme) => {
    set({ loading: true });
    try {
      const data = await api.post<PreviewResponse & { theme: string }>(
        "switch_theme",
        { theme },
      );
      set({
        previewImage: data.image,
        bboxes: data.bboxes,
        imgSize: data.img_size,
        currentTheme: theme,
      });
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
      set({
        previewImage: data.image,
        bboxes: data.bboxes,
        imgSize: data.img_size,
        overrides: { ...get().overrides, ...overrides },
      });
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
      set({
        previewImage: data.image,
        bboxes: data.bboxes,
        imgSize: data.img_size,
        overrides: {},
        selectedElement: null,
        selectedBbox: null,
      });
      get().showToast("Restored to original", "success");
    } catch (e) {
      console.error("[Editor] Failed to restore:", e);
      get().showToast(`Error: ${e}`, "error");
    } finally {
      set({ loading: false });
    }
  },

  setDarkMode: (dark) => {
    set({ darkMode: dark });
    // Sync with backend
    api.post("update", { dark_mode: dark }).catch(console.error);
  },

  toggleHitmap: () => {
    set((s) => ({ showHitmap: !s.showHitmap }));
  },

  toggleRulers: () => {
    set((s) => ({ showRulers: !s.showRulers }));
  },

  toggleRulerUnit: () => {
    set((s) => {
      const next = s.rulerUnit === "mm" ? "inch" : "mm";
      localStorage.setItem("figrecipe-ruler-unit", next);
      return { rulerUnit: next };
    });
  },

  showToast: (message, type = "info") => {
    set({ toast: { message, type } });
    setTimeout(() => set({ toast: null }), 3000);
  },

  clearToast: () => set({ toast: null }),
}));
