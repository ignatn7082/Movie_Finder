import { useState } from "react";
import Navbar from "../components/Navbar";

function Search() {
  const [tab, setTab] = useState("image");
  const [selectedImageModel, setSelectedImageModel] = useState("clip");

  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]);
  const [actorInfo, setActorInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);

  const BaseURL = "http://localhost:8000/static/";

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
    } else {
      setFile(null);
      setPreview(null);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setResults([]);
    setActorInfo(null);
    setLoading(true);

    try {
      let res;

      if (tab === "image" && file) {
        const formData = new FormData();
        formData.append("file", file);
        res = await fetch("http://localhost:8000/search/image", {
          method: "POST",
          body: formData,
        });
      } else if (tab === "text" && query.trim()) {
        res = await fetch(
          `http://localhost:8000/search/text?query=${encodeURIComponent(query)}`
        );
      } else {
        alert("Hãy nhập mô tả hoặc chọn ảnh để tìm kiếm!");
        setLoading(false);
        return;
      }

      const data = await res.json();
      console.debug("Search response:", data);

      // --- FIX QUAN TRỌNG: Ưu tiên đọc {results: [...] } ---
      if (data.results && Array.isArray(data.results)) {
        setResults(data.results);
        return;
      }

      // Nếu có movies (truy vấn ảnh diễn viên)
      if (data.movies && Array.isArray(data.movies)) {
        setActorInfo({
          actor: data.actor,
          similarity: data.similarity,
          message: data.message,
        });
        setResults(data.movies);
        return;
      }

      // Nếu backend trả về 1 item duy nhất
      if (data.title && !Array.isArray(data)) {
        setResults([data]);
        return;
      }

      setResults([]);
    } catch (err) {
      console.error("Search failed:", err);
      alert("Lỗi khi tìm kiếm, vui lòng thử lại!");
    } finally {
      setLoading(false);
    }
  };

  const fallbackPoster = (title) => {
    if (!title) return BaseURL + "posters/default_poster.jpg";
    const fallbackName = title
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/\s+/g, "_")
      + ".jpg";
    return BaseURL + "posters/" + fallbackName;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-200 dark:from-gray-900 dark:to-gray-950 text-gray-900 dark:text-gray-200">
      <Navbar />

      <div className="pt-24 px-6 max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* LEFT SIDEBAR */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-bold text-blue-600 mb-4 text-center">
            🔍 Công cụ tìm kiếm
          </h2>

          <div className="flex justify-center mb-6">
            <button
              onClick={() => setTab("image")}
              className={`px-5 py-2 rounded-l-lg font-semibold ${
                tab === "image"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 dark:bg-gray-800"
              }`}
            >
              📸 Tìm theo ảnh
            </button>
            <button
              onClick={() => setTab("text")}
              className={`px-5 py-2 rounded-r-lg font-semibold ${
                tab === "text"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 dark:bg-gray-800"
              }`}
            >
              📝 Tìm theo mô tả
            </button>
          </div>

          {tab === "image" && (
            <div className="flex flex-col items-center">
              <label className="text-gray-600 mb-1">Chọn mô hình:</label>
              <select
                value={selectedImageModel}
                onChange={(e) => setSelectedImageModel(e.target.value)}
                className="border rounded-lg px-3 py-2 mb-3 w-full dark:bg-gray-800"
              >
                <option value="clip">CLIP</option>
                <option value="resnet50">ResNet50</option>
              </select>

              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="border rounded-lg px-3 py-2 mb-3 w-full"
              />

              {preview && (
                <div className="relative mb-3">
                  <img
                    src={preview}
                    className="w-64 rounded-lg shadow-lg"
                    alt="Preview"
                  />
                  <button
                    onClick={() => {
                      setFile(null);
                      setPreview(null);
                    }}
                    className="absolute top-2 right-2 bg-red-600 text-white px-2 py-1 rounded-md text-xs"
                  >
                    ✕
                  </button>
                </div>
              )}

              <button
                onClick={handleSearch}
                disabled={loading}
                className="bg-blue-600 text-white px-5 py-2 rounded-lg"
              >
                {loading ? "Đang tìm..." : "Tìm theo ảnh"}
              </button>
            </div>
          )}

          {tab === "text" && (
            <form onSubmit={handleSearch} className="flex flex-col items-center">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Nhập mô tả hoặc tên phim..."
                className="border rounded-lg px-3 py-2 w-full mb-3 dark:bg-gray-800"
                rows="4"
              />

              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-5 py-2 rounded-lg"
              >
                {loading ? "Đang tìm..." : "Tìm theo mô tả"}
              </button>
            </form>
          )}
        </div>

        {/* RIGHT: RESULTS LIST */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-bold text-blue-600 mb-4 text-center">
            🎬 Kết quả tìm kiếm
          </h2>

          {loading && (
            <p className="text-center text-gray-500 animate-pulse">
              Đang tải kết quả...
            </p>
          )}

          {!loading && results.length === 0 && !actorInfo && (
            <p className="text-center text-gray-500 italic">
              Hãy nhập mô tả hoặc tải ảnh để tìm kiếm phim.
            </p>
          )}

          {/* ACTOR RESULTS */}
          {actorInfo && actorInfo.actor && (
            <div className="bg-gray-800 p-5 rounded-xl mb-6">
              <h3 className="text-2xl font-bold text-yellow-400 text-center">
                🎭 Nhận diện diễn viên: {actorInfo.actor}
              </h3>
              <p className="text-gray-300 text-center">
                Độ chính xác:{" "}
                {actorInfo.similarity
                  ? (actorInfo.similarity * 100).toFixed(2) + "%"
                  : "N/A"}
              </p>

              <div className="flex justify-center mt-4">
                {preview && (
                  <img
                    src={preview}
                    className="w-40 h-40 object-cover rounded-full border-4 border-blue-500 shadow-lg"
                  />
                )}
              </div>

              <h4 className="text-xl mt-6 font-semibold text-blue-400">
                🎬 Danh sách phim đã tham gia
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3">
                {results.map((movie, idx) => (
                  <div
                    key={idx}
                    onClick={() => setSelected(movie)}
                    className="bg-gray-900 rounded-lg p-3 shadow-lg hover:scale-105 transition cursor-pointer"
                  >
                    <img
                      src={BaseURL + movie.poster}
                      onError={(e) => (e.target.src = fallbackPoster(movie.title))}
                      className="w-full h-48 object-cover rounded-lg mb-2"
                    />
                    <p className="text-white font-semibold">{movie.title}</p>
                    <p className="text-gray-400 text-sm">🎭 Vai: {movie.role_name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* MOVIE RESULTS */}
          {!actorInfo && results.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {results.map((item, idx) => (
                <div
                  key={idx}
                  className="group cursor-pointer"
                  onClick={() => setSelected(item)}
                >
                  <img
                    src={BaseURL + item.poster}
                    onError={(e) =>
                      (e.target.src = fallbackPoster(item.original_title))
                    }
                    className="w-full h-64 object-cover rounded-lg shadow-md group-hover:scale-105 transition-transform"
                  />
                  <div className="absolute bottom-0 bg-black/60 text-white text-sm w-full px-2 py-1 rounded-b-lg opacity-0 group-hover:opacity-100">
                    {item.title}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* MOVIE MODAL */}
      {selected && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-[600px] max-h-[90vh] overflow-y-auto p-6 relative">
            <button
              onClick={() => setSelected(null)}
              className="absolute top-3 right-3 text-gray-500 hover:text-red-600 text-xl"
            >
              ✕
            </button>

            <img
              src={BaseURL + selected.poster}
              onError={(e) =>
                (e.target.src = fallbackPoster(selected.original_title))
              }
              className="w-full rounded-lg shadow-md mb-3"
            />

            <h2 className="text-2xl font-bold text-blue-600 mb-2">
              {selected.title}
            </h2>
            <p><b>Tên gốc:</b> {selected.original_title}</p>
            <p><b>Ngày công chiếu:</b> {selected.release_date}</p>
            <p><b>Đạo diễn:</b> {selected.director}</p>
            <p><b>Diễn viên:</b> {selected.stars}</p>
            <p><b>Thể loại:</b> {selected.genres_vn}</p>
            <p className="mt-3 italic">{selected.overview}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Search;
