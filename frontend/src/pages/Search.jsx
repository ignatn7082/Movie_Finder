import { useState } from "react";
import Navbar from "../components/Navbar";

function Search() {
  const [tab, setTab] = useState("image"); // tab hiện tại: "image" | "text"
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [results, setResults] = useState([]); // luôn là mảng phim để render list
  const [actorInfo, setActorInfo] = useState(null); // lưu kết quả actor (nếu có)
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
      let res, data;
      if (tab === "image" && file) {
        const formData = new FormData();
        formData.append("file", file);
        res = await fetch(`http://localhost:8000/search/image?model=${model}`, {
          method: "POST",
          body: formData
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

      // Normalize backend response:
      // - If backend returns an object with actor/movies => extract actorInfo and set movies array
      // - If backend returns an array => treat as movies list
      if (data && typeof data === "object" && !Array.isArray(data)) {
        if (data.actor || data.movies) {
          setActorInfo({ actor: data.actor ?? null, similarity: data.similarity ?? null, message: data.message ?? null });
          setResults(Array.isArray(data.movies) ? data.movies : []);
        } else {
          // unknown object shape -> try to find movies array or keep empty
          if (Array.isArray(data.results)) setResults(data.results);
          else setResults([]);
        }
      } else if (Array.isArray(data)) {
        setResults(data);
      } else {
        setResults([]);
      }

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
            <select onChange={(e) => setModel(e.target.value)} value={model}>
  <option value="clip">CLIP (tổng quát)</option>
  <option value="arcface">ArcFace (nhận diện mặt)</option>
</select>
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

          {/* === KẾT QUẢ TÌM KIẾM — TỰ ĐỘNG PHÂN BIỆT DIỄN VIÊN / PHIM === */}
{(Array.isArray(results) && results.length > 0) || actorInfo ? (
  <div className="space-y-6">

    {/* === NẾU LÀ KẾT QUẢ DIỄN VIÊN (tìm theo ảnh) === */}
    {actorInfo && actorInfo.actor && (
      <div className="bg-gray-800 p-5 rounded-xl shadow-lg">
        <h3 className="text-2xl font-bold text-yellow-400 text-center">
          🎭 Nhận diện diễn viên: {actorInfo.actor}
        </h3>

        <p className="text-gray-300 text-center mt-1">
          Độ chính xác: {actorInfo.similarity ? (actorInfo.similarity * 100).toFixed(2) + "%" : "N/A"}
        </p>

        {/* ẢNH PREVIEW */}
        <div className="flex justify-center mt-4">
          {preview && (
            <img
              src={preview}
              className="w-40 h-40 object-cover rounded-full border-4 border-blue-500 shadow-lg"
            />
          )}
        </div>

        {/* DANH SÁCH PHIM */}
        <h4 className="text-xl mt-6 font-semibold text-blue-400">
          🎬 Danh sách phim đã tham gia
        </h4>

        {results.length === 0 && (
           <p className="text-gray-400 italic">Không tìm thấy phim.</p>
         )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3">
          {results.map((movie, idx) => (
            <div
              key={idx}
              className="bg-gray-900 rounded-lg p-3 shadow-lg hover:scale-105 transition cursor-pointer"
              onClick={() => setSelected(movie)}
            >
              <img
                src={BaseURL + movie.poster}
                alt={movie.title}
                className="w-full h-48 object-cover rounded-lg mb-2"
              />

              <p className="text-white font-semibold">{movie.title}</p>
              <p className="text-gray-400 text-sm">🎭 Vai: {movie.role_name}</p>
              <p className="text-gray-500 text-xs mt-1">
                📅 {movie.release_date}
              </p>
            </div>
          ))}
        </div>
      </div>
    )}

    {/* === NẾU LÀ KẾT QUẢ PHIM (tìm theo mô tả) === */}
    {!actorInfo && results.length > 0 && (
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {results.map((item, idx) => (
          <div
            key={idx}
            className="relative group cursor-pointer"
            onClick={() => setSelected(item)}
          >
            <img
              src={BaseURL + item.poster}
              alt={item.original_title}
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
 ) : (
  <p className="text-center text-gray-500 italic">
    Hãy nhập mô tả hoặc tải ảnh để tìm kiếm phim.
  </p>
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
            {console.log("Selected poster in modal:", selected.poster)}
<img
  src={BaseURL + selected.poster}
  alt={selected.original_title}
  className="w-full h-64 object-cover rounded-lg shadow-md group-hover:scale-105 transition-transform duration-300"
  style={{ width: "auto", height: "auto", maxWidth: "100%", maxHeight: "80vh" }}
  onError={(e) => {
    console.warn("Ảnh bị lỗi, thử lấy poster từ original_title…");

    // Tạo filename từ original_title
    const fallbackName = selected.original_title
      .normalize("NFD")                     // bỏ dấu tiếng Việt
      .replace(/[\u0300-\u036f]/g, "")      // remove accents
      .toLowerCase()
      .replace(/\s+/g, "_")                 // dấu cách → _
      + ".jpg";

    const newPoster = "posters/" + fallbackName;

    console.log("Thử fallback:", BaseURL + newPoster);

    // Thử load ảnh từ /static/posters/
    e.target.src = BaseURL + newPoster;

    // Nếu fallback cũng sai → fallback cuối
    e.target.onerror = () => {
      e.target.src = BaseURL + "posters/default_poster.jpg";
    };
  }}
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
