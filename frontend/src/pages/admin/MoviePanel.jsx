import React, { useState, useEffect } from "react";

export default function MoviesPanel() {
  const [movies, setMovies] = useState([]);
  const [newMovie, setNewMovie] = useState({
    title: "",
    description: "",
    poster: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const adminToken = localStorage.getItem("admin_token");

  useEffect(() => {
    fetchMovies();
  }, []);

  // 🔹 Lấy danh sách phim
  const fetchMovies = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/movies", {
          headers: { Authorization: `Bearer ${adminToken}` },
        });
      if (!res.ok) throw new Error("Không thể tải danh sách phim");
      const data = await res.json();
      setMovies(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Upload phim mới
  const handleAddMovie = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append("title", newMovie.title);
      formData.append("description", newMovie.description);
      if (newMovie.poster) formData.append("poster", newMovie.poster);

      const res = await fetch("http://localhost:8000/api/movies/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${adminToken}`,
        },
        body: formData,
      });

      if (!res.ok) throw new Error("Thêm phim thất bại!");
      await fetchMovies();
      setNewMovie({ title: "", description: "", poster: null });
    } catch (err) {
      alert(err.message);
    }
  };

  // 🔹 Xoá phim
  const handleDelete = async (id) => {
    if (!window.confirm("Xác nhận xoá phim này?")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      if (!res.ok) throw new Error("Xoá phim thất bại!");
      await fetchMovies();
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <p className="text-gray-500">Đang tải...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-6 bg-gray-900 rounded-xl shadow-lg">
      <h1 className="text-2xl font-bold mb-6 text-gray-100">🎬 Quản lý phim</h1>

      {/* Form thêm phim */}
      <form
        onSubmit={handleAddMovie}
        className="bg-gray-800 p-4 rounded-lg mb-6 space-y-4"
      >
        <div>
          <label className="block text-sm text-gray-400 mb-1">Tên phim</label>
          <input
            type="text"
            value={newMovie.title}
            onChange={(e) =>
              setNewMovie({ ...newMovie, title: e.target.value })
            }
            className="w-full p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">Mô tả</label>
          <textarea
            value={newMovie.description}
            onChange={(e) =>
              setNewMovie({ ...newMovie, description: e.target.value })
            }
            className="w-full p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows="3"
          />
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-1">Ảnh Poster</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) =>
              setNewMovie({ ...newMovie, poster: e.target.files[0] })
            }
            className="w-full text-gray-200"
          />
        </div>

        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md text-white font-medium"
        >
          ➕ Thêm phim
        </button>
      </form>

      {/* Danh sách phim */}
      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-700 text-sm">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-4 py-2 text-left text-gray-400">Tên phim</th>
              <th className="px-4 py-2 text-left text-gray-400">Mô tả</th>
              <th className="px-4 py-2 text-left text-gray-400">Poster</th>
              <th className="px-4 py-2 text-left text-gray-400">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {movies.map((m) => (
              <tr
                key={m.id}
                className="border-t border-gray-700 hover:bg-gray-800 transition"
              >
                <td className="px-4 py-2 text-gray-100">{m.title}</td>
                <td className="px-4 py-2 text-gray-400 truncate max-w-md">
                  {m.description || "—"}
                </td>
                <td className="px-4 py-2">
                  {m.poster ? (
                    <img
                      src={`http://localhost:8000/static/${m.poster}`}
                      alt={m.title}
                      className="w-16 h-20 object-cover rounded"
                    />
                  ) : (
                    <span className="text-gray-500">Không có</span>
                  )}
                </td>
                <td className="px-4 py-2">
                  <button
                    onClick={() => handleDelete(m.id)}
                    className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded-md text-white text-sm"
                  >
                    🗑️ Xoá
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
