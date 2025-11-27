// src/config/api.js
export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const getPosterUrl = (movieOrPath) => {
  let path = movieOrPath;

  if (!path) return `${API_BASE}/static/posters/default_poster.jpg`;

  if (typeof movieOrPath === "object" && movieOrPath !== null) {
    path = movieOrPath.poster || movieOrPath.poster_path;
  }

  if (!path) return `${API_BASE}/static/posters/default_poster.jpg`;

  if (typeof path !== "string") {
    console.warn("Poster path không hợp lệ:", path);
    return `${API_BASE}/static/posters/default_poster.jpg`;
  }

  const cleanPath = path.replace(/^\/?static\//, "").trim();
  return `${API_BASE}/static/${cleanPath}`;
};

export const BaseURL = `${API_BASE}/static/`;

export const API_ENDPOINTS = {
  searchText: (query) => `${API_BASE}/api/search/text?query=${encodeURIComponent(query)}`,
  searchImage: `${API_BASE}/search/image`,
  chat: `${API_BASE}/api/chat`,
  dataset: `${API_BASE}/api/dataset`,
  stats: `${API_BASE}/api/movies/stats`,
  movies: `${API_BASE}/api/movies/list`,
};