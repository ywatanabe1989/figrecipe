import { execSync } from "child_process";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/**
 * Discover scitex-ui static directory from the Python environment.
 * Works for both pip-installed packages and editable (dev) installs.
 * Falls back to SCITEX_UI_STATIC env var if Python discovery fails.
 */
function discoverScitexUiStatic(): string {
  // 1. Environment variable override (for CI, Docker, custom setups)
  if (process.env.SCITEX_UI_STATIC) {
    return process.env.SCITEX_UI_STATIC;
  }

  // 2. Auto-discover via scitex_ui.get_static_dir() (pip-installed or editable)
  try {
    const pkgPath = execSync(
      'python3 -c "import scitex_ui; print(scitex_ui.get_static_dir())"',
      { encoding: "utf-8", timeout: 5000 },
    ).trim();
    if (pkgPath) return pkgPath;
  } catch {
    // scitex_ui not installed — fall through
  }

  throw new Error(
    "scitex-ui not found. Install it (pip install scitex-ui) or set SCITEX_UI_STATIC env var.",
  );
}

const SCITEX_UI_STATIC = discoverScitexUiStatic();

export default defineConfig({
  plugins: [react()],
  base: "/static/figrecipe/",
  resolve: {
    alias: {
      "scitex-ui": SCITEX_UI_STATIC,
    },
  },
  build: {
    outDir: "../static/figrecipe",
    emptyOutDir: true,
    sourcemap: true,
  },
  server: {
    port: 3000,
    proxy: {
      // Proxy API calls to Django backend during development
      "/preview": "http://127.0.0.1:8050",
      "/update": "http://127.0.0.1:8050",
      "/hitmap": "http://127.0.0.1:8050",
      "/ping": "http://127.0.0.1:8050",
      "/style": "http://127.0.0.1:8050",
      "/overrides": "http://127.0.0.1:8050",
      "/theme": "http://127.0.0.1:8050",
      "/list_themes": "http://127.0.0.1:8050",
      "/switch_theme": "http://127.0.0.1:8050",
      "/save": "http://127.0.0.1:8050",
      "/restore": "http://127.0.0.1:8050",
      "/diff": "http://127.0.0.1:8050",
      "/get_labels": "http://127.0.0.1:8050",
      "/update_label": "http://127.0.0.1:8050",
      "/update_axis_type": "http://127.0.0.1:8050",
      "/get_axis_info": "http://127.0.0.1:8050",
      "/get_legend_info": "http://127.0.0.1:8050",
      "/update_legend_position": "http://127.0.0.1:8050",
      "/get_axes_positions": "http://127.0.0.1:8050",
      "/update_axes_position": "http://127.0.0.1:8050",
      "/calls": "http://127.0.0.1:8050",
      "/call": "http://127.0.0.1:8050",
      "/update_call": "http://127.0.0.1:8050",
      "/update_annotation_position": "http://127.0.0.1:8050",
      "/get_captions": "http://127.0.0.1:8050",
      "/update_caption": "http://127.0.0.1:8050",
      "/datatable": "http://127.0.0.1:8050",
      "/download": "http://127.0.0.1:8050",
      "/add_image_panel": "http://127.0.0.1:8050",
      "/load_recipe": "http://127.0.0.1:8050",
      "/api": "http://127.0.0.1:8050",
    },
  },
});
