import React, { useState, useEffect } from "react";

export default function MoviesPanel() {
  const [movies, setMovies] = useState([]);
  const [newMovie, setNewMovie] = useState({ title: "", description: "", poster: null });
  const [editingMovie, setEditingMovie] = useState(null);
  const [editingPosterFile, setEditingPosterFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const adminToken = localStorage.getItem("admin_token");
  const BaseURL = "http://localhost:8000/static/";
  const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  const API_URL = `${API_BASE.replace(/\/$/, "")}/api/movies`;

  const buildPosterUrl = (p) => {
    if (!p) return null;
    if (p.startsWith("http")) return p;
    // try /posters then /static/posters then /static
    return `${API_BASE.replace(/\/$/, "")}/posters/${encodeURIComponent(p.split("/").pop())}`;
  };

  const fetchMovies = async () => {
    setLoading(true);
    setError("");
    try {
      // try API with pagination param; fallback to plain array
      const perPage = 100;
      let page = 1;
      let all = [];
      while (true) {
        const res = await fetch(`${API_URL}?page=${page}&per_page=${perPage}`, {
          headers: adminToken ? { Authorization: `Bearer ${adminToken}` } : {},
        });
        if (!res.ok) {
          const txt = await res.text();
          throw new Error(txt || "Failed to fetch movies");
        }
        const data = await res.json();
        const pageMovies = Array.isArray(data) ? data : Array.isArray(data.movies) ? data.movies : [];
        all = all.concat(pageMovies);
        if (!Array.isArray(data) && typeof data.total === "number") {
          if (all.length >= data.total) break;
        }
        if (pageMovies.length < perPage) break;
        page += 1;
        if (page > 50) break; // safety
      }
      setMovies(all);
    } catch (err) {
      setError(err.message || "Lỗi tải phim");
      console.error("Lỗi tải phim:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAddMovie = async (e) => {
    e.preventDefault();
    if (!newMovie.title.trim()) return alert("Vui lòng nhập tên phim");
    try {
      const fd = new FormData();
      fd.append("title", newMovie.title);
      fd.append("description", newMovie.description);
      if (newMovie.poster) fd.append("poster", newMovie.poster);
      const res = await fetch(`${API_URL}/upload`, {
        method: "POST",
        headers: adminToken ? { Authorization: `Bearer ${adminToken}` } : {},
        body: fd,
      });
      if (!res.ok) throw new Error(await res.text());
      setNewMovie({ title: "", description: "", poster: null });
      await fetchMovies();
    } catch (err) {
      console.error("Lỗi thêm phim:", err);
      alert(err.message || "Thêm phim thất bại");
    }
  };

  const handleEditClick = (movie) => {
    setEditingMovie({ id: movie.id, title: movie.title || "", description: movie.description || "", poster: movie.poster || null });
    setEditingPosterFile(null);
  };

  const handleUpdateMovie = async (e) => {
    e.preventDefault();
    if (!editingMovie.title.trim()) return alert("Vui lòng nhập tên phim");
    try {
      const fd = new FormData();
      fd.append("title", editingMovie.title);
      fd.append("description", editingMovie.description);
      if (editingPosterFile) fd.append("poster", editingPosterFile);
      const res = await fetch(`${API_URL}/${editingMovie.id}`, {
        method: "PUT",
        headers: adminToken ? { Authorization: `Bearer ${adminToken}` } : {},
        body: fd,
      });
      if (!res.ok) throw new Error(await res.text());
      setEditingMovie(null);
      await fetchMovies();
    } catch (err) {
      console.error("Lỗi cập nhật phim:", err);
      alert(err.message || "Cập nhật thất bại");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Xác nhận xoá phim này?")) return;
    try {
      const res = await fetch(`${API_URL}/${id}`, {
        method: "DELETE",
        headers: adminToken ? { Authorization: `Bearer ${adminToken}` } : {},
      });
      if (!res.ok) throw new Error(await res.text());
      await fetchMovies();
    } catch (err) {
      console.error("Lỗi xóa phim:", err);
      alert(err.message || "Xóa thất bại");
    }
  };

  if (loading) return <p className="text-gray-400 p-6">⏳ Đang tải danh sách phim...</p>;
  if (error) return <p className="text-red-500 p-6">❌ {error}</p>;

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100">
      <div className="flex-1 flex flex-col">
        <main className="flex-1 p-6 overflow-y-auto">
          <h2 className="text-2xl font-semibold mb-4 text-blue-400">Thêm Phim Mới</h2>
          <form onSubmit={handleAddMovie} className="bg-gray-800 p-4 rounded-lg mb-8 space-y-4 shadow-md">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Tên phim</label>
              <input type="text" value={newMovie.title} onChange={(e) => setNewMovie({ ...newMovie, title: e.target.value })} className="w-full p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Mô tả</label>
              <textarea value={newMovie.description} onChange={(e) => setNewMovie({ ...newMovie, description: e.target.value })} className="w-full p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600" rows="3" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Ảnh Poster</label>
              <input type="file" accept="image/*" onChange={(e) => setNewMovie({ ...newMovie, poster: e.target.files[0] })} className="w-full text-gray-200" />
            </div>
            <button type="submit" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-white font-medium">➕ Thêm phim</button>
          </form>

          <h2 className="text-2xl font-semibold mb-4 text-white">Danh sách Phim</h2>
          <div className="overflow-x-auto bg-gray-800 rounded-lg shadow-md">
            {movies.length === 0 ? (
              <p className="text-gray-400 text-center py-6">Không có phim nào trong cơ sở dữ liệu</p>
            ) : (
              <table className="min-w-full border-collapse text-sm">
                <thead className="bg-gray-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-gray-300">Tên phim</th>
                    <th className="px-4 py-3 text-left text-gray-300">Mô tả</th>
                    <th className="px-4 py-3 text-left text-gray-300">Poster</th>
                    <th className="px-4 py-3 text-left text-gray-300">Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {movies.map((m) => (
                    <tr key={m.id} className="border-t border-gray-700 hover:bg-gray-800 transition">
                      <td className="px-4 py-2 text-gray-100 font-medium">{m.original_title}</td>
                      <td className="px-4 py-2 text-gray-400 truncate max-w-xs">{m.overview || "—"}</td>
                      <td className="px-4 py-2">
                        {m.poster ? (
                          <img
                          src={m.poster ? BaseURL + m.poster : BaseURL + "posters/default_poster.jpg" }
                          alt={m.original_title} 
                          className="rounded" style={{ width: "auto", height: "4.5rem", maxWidth: "8rem", objectFit: "contain" }} onError={(e) => { e.target.onerror = null; e.target.src = buildPosterUrl(null); }} />
                        ) : (
                          <span className="text-gray-500">Không có</span>
                        )}
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button onClick={() => handleEditClick(m)} className="bg-yellow-600 hover:bg-yellow-700 px-3 py-1 rounded-md text-white text-sm">✍️ Sửa</button>
                          <button onClick={() => handleDelete(m.id)} className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded-md text-white text-sm">🗑️ Xoá</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>

      {editingMovie && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <form onSubmit={handleUpdateMovie} className="bg-gray-800 p-6 rounded-lg w-full max-w-lg space-y-4 shadow-xl">
            <h2 className="text-xl font-bold text-yellow-400">Chỉnh sửa Phim: {editingMovie.title}</h2>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Tên phim</label>
              <input type="text" value={editingMovie.title} onChange={(e) => setEditingMovie({ ...editingMovie, title: e.target.value })} className="w-full p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Mô tả</label>
              <textarea value={editingMovie.description || ""} onChange={(e) => setEditingMovie({ ...editingMovie, description: e.target.value })} className="w-full p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600" rows="3" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Ảnh Poster mới (Để trống nếu không thay đổi)</label>
              <input type="file" accept="image/*" onChange={(e) => setEditingPosterFile(e.target.files[0])} className="w-full text-gray-200" />
            </div>
            <div className="flex justify-end space-x-3 pt-2">
              <button type="button" onClick={() => setEditingMovie(null)} className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-md text-white font-medium">Hủy</button>
              <button type="submit" className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded-md text-white font-medium">💾 Cập nhật</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}