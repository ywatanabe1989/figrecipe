/** Core type definitions for the figrecipe editor. */

export interface BBox {
  x: number;
  y: number;
  width: number;
  height: number;
  type: string;
  label: string;
  ax_index?: number;
  call_id?: string;
}

export interface ImgSize {
  width: number;
  height: number;
}

export interface FileTreeItem {
  name: string;
  path: string;
  type: "file" | "directory";
  is_current?: boolean;
  has_image?: boolean;
  children?: FileTreeItem[];
}

export interface TabData {
  id: string;
  label: string;
  columns: ColumnDef[];
  rows: (string | number)[][];
}

export interface ColumnDef {
  name: string;
  dtype: string;
}

export interface StyleOverrides {
  [key: string]: unknown;
}

export interface CallRecord {
  call_id: string;
  method: string;
  ax_index: number;
  kwargs: Record<string, unknown>;
}

export interface PreviewResponse {
  image: string;
  bboxes: Record<string, BBox>;
  img_size: ImgSize;
}

export interface HitmapResponse {
  image: string;
  color_map: Record<string, unknown>;
}

export interface FilesResponse {
  tree: FileTreeItem[];
  files: string[];
  current_file: string | null;
  working_dir: string | null;
}

export interface ThemeInfo {
  themes: string[];
  current: string;
}
