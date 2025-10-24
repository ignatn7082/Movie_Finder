
import { useState } from "react";
import Navbar from "../components/Navbar";

function Search() {
  const [tab, setTab] = useState("image"); // tab hiện tại: "image" | "text"
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);

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
    setLoading(true);

    try {
      let res, data;
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

      data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error("Search failed:", err);
      alert("Lỗi khi tìm kiếm, vui lòng thử lại!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-200 dark:from-gray-900 dark:to-gray-950 text-gray-900 dark:text-gray-200">
      <Navbar />

      <div className="pt-24 px-6 max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* === BÊN TRÁI: KHỐI CÔNG CỤ === */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6 flex flex-col justify-start">
          <h2 className="text-2xl font-bold text-blue-600 mb-4 text-center">
            🔍 Công cụ tìm kiếm
          </h2>

          {/* === TAB CHUYỂN === */}
          <div className="flex justify-center mb-6">
            <button
              onClick={() => setTab("image")}
              className={`px-5 py-2 rounded-l-lg font-semibold ${
                tab === "image"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 dark:bg-gray-800 hover:bg-gray-300"
              }`}
            >
              📸 Tìm theo ảnh
            </button>
            <button
              onClick={() => setTab("text")}
              className={`px-5 py-2 rounded-r-lg font-semibold ${
                tab === "text"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 dark:bg-gray-800 hover:bg-gray-300"
              }`}
            >
              📝 Tìm theo mô tả
            </button>
          </div>

          {/* === KHỐI TÌM KIẾM ẢNH === */}
          {tab === "image" && (
            <div className="flex flex-col items-center w-full">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="border border-gray-300 rounded-lg px-3 py-2 mb-3 w-full"
              />

              {preview && (
                <div className="relative mb-3">
                  <img
                    src={preview}
                    alt="Preview"
                    className="w-64 h-auto rounded-lg shadow-lg object-contain"
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
                className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 mt-2"
              >
                {loading ? "Đang tìm..." : "Tìm theo ảnh"}
              </button>
            </div>
          )}

          {/* === KHỐI TÌM KIẾM MÔ TẢ === */}
          {tab === "text" && (
            <form
              onSubmit={handleSearch}
              className="flex flex-col items-center w-full"
            >
              <textarea
                placeholder="Nhập mô tả hoặc tên phim..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows="4"
                className="border border-gray-300 rounded-lg px-3 py-2 w-full mb-3 dark:bg-gray-800 resize-none"
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? "Đang tìm..." : "Tìm theo mô tả"}
              </button>
            </form>
          )}
        </div>

        {/* === BÊN PHẢI: KẾT QUẢ === */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-bold text-blue-600 mb-4 text-center">
            🎬 Kết quả tìm kiếm
          </h2>

          {loading && (
            <p className="text-center text-gray-500 animate-pulse">
              Đang tải kết quả...
            </p>
          )}

          {!loading && results.length === 0 && (
            <p className="text-center text-gray-500 italic">
              Hãy nhập mô tả hoặc tải ảnh để tìm kiếm phim.
            </p>
          )}

          {results.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {results.map((item, idx) => (
                <div
                  key={idx}
                  className="relative group cursor-pointer"
                  onClick={() => setSelected(item)}
                >
                  <img
                    src={item.poster}
                    alt={item.title}
                    className="w-full h-64 object-cover rounded-lg shadow-md group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute bottom-0 bg-black/60 text-white text-sm w-full px-2 py-1 rounded-b-lg opacity-0 group-hover:opacity-100 transition">
                    {item.title}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* === MODAL CHI TIẾT PHIM === */}
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
              src={selected.poster}
              alt={selected.title}
              className="w-full rounded-lg mb-4 object-contain"
            />
            <h2 className="text-2xl font-bold text-blue-600 mb-2">
              {selected.title}
            </h2>
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              <b>Tên gốc:</b> {selected.original_title}
            </p>
            <p><b>Ngày công chiếu:</b> {selected.release_date}</p>
            <p><b>Đạo diễn:</b> {selected.director}</p>
            <p><b>Diễn viên:</b> {selected.stars}</p>
            <p><b>Thể loại:</b> {selected.genres}</p>
            <p className="mt-3 text-gray-700 dark:text-gray-400 italic">
              {selected.overview}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Search;
