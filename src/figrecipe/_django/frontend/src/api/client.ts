/** API client for communicating with the Django backend. */

let _base = import.meta.env.VITE_API_BASE || "";
let _workingDir: string | null = null;
let _recipe: string | null = null;

/** Set the API base URL at runtime (used by FigrecipeEditor when embedded). */
export function setApiBase(base: string) {
  _base = base.replace(/\/+$/, ""); // strip trailing slashes
}

/** Set the working directory for all API calls. */
export function setWorkingDir(dir: string) {
  _workingDir = dir;
}

/** Set the recipe path for all API calls. */
export function setRecipe(recipe: string) {
  _recipe = recipe;
}

/** Read the recipe — prefer runtime value, fall back to URL query param. */
function getRecipeParam(): string {
  if (_recipe) return _recipe;
  const params = new URLSearchParams(window.location.search);
  return params.get("recipe") || "";
}

/** Append recipe= and working_dir= to endpoint URL. */
function buildUrl(endpoint: string): string {
  const recipe = getRecipeParam();
  const sep = endpoint.includes("?") ? "&" : "?";
  let url = `${_base}/${endpoint}`;
  const params: string[] = [];
  if (recipe) params.push(`recipe=${encodeURIComponent(recipe)}`);
  if (_workingDir)
    params.push(`working_dir=${encodeURIComponent(_workingDir)}`);
  if (params.length) url += `${sep}${params.join("&")}`;
  return url;
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = buildUrl(endpoint);
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API error: ${res.status}`);
  }
  return res.json();
}

export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint),

  post: <T>(endpoint: string, data?: unknown) =>
    request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  /** Fetch raw bytes (for downloads). */
  getBlob: async (endpoint: string): Promise<Blob> => {
    const url = buildUrl(endpoint);
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Download failed: ${res.status}`);
    return res.blob();
  },

  /** POST JSON and receive raw bytes (for compose export). */
  postBlob: async (endpoint: string, data?: unknown): Promise<Blob> => {
    const url = buildUrl(endpoint);
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: data ? JSON.stringify(data) : undefined,
    });
    if (!res.ok) throw new Error(`Export failed: ${res.status}`);
    return res.blob();
  },
};
