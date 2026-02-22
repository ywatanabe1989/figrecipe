import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  base: "/static/figrecipe/",
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
