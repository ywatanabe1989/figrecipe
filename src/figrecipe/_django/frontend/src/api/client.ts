/** API client for communicating with the Django backend. */

const BASE = import.meta.env.VITE_API_BASE || "";

/** Read the recipe query param from the page URL. */
function getRecipeParam(): string {
  const params = new URLSearchParams(window.location.search);
  return params.get("recipe") || "";
}

/** Append recipe= to endpoint URL so Django can identify the editor session. */
function buildUrl(endpoint: string): string {
  const recipe = getRecipeParam();
  const sep = endpoint.includes("?") ? "&" : "?";
  return `${BASE}/${endpoint}${recipe ? `${sep}recipe=${encodeURIComponent(recipe)}` : ""}`;
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
