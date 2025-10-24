// src/config/api.js
export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Helper: sinh URL ảnh poster / file static
export const getPosterUrl = (path) => {
  if (!path) return null;
  return `${API_BASE}/static/${path.replace(/^\/?static\//, "")}`;
};

// endpoint
export const API_ENDPOINTS = {
  searchText: (query) => `${API_BASE}/api/search/text?query=${encodeURIComponent(query)}`,
  searchImage: `${API_BASE}/search/image`,
  chat: `${API_BASE}/api/chat`,
  dataset: `${API_BASE}/api/dataset`,
  stats: `${API_BASE}/api/movies/stats`,
  movies: `${API_BASE}/api/movies/list`,
};
