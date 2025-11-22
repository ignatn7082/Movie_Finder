export default function MovieModal({ movie, onClose }) {
  const BaseURL = "http://localhost:8000/static/";
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-[600px] max-h-[90vh] overflow-y-auto p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-red-600 text-xl"
        >
          ✕
        </button>

        <img
  src={BaseURL + item.poster}
  alt={item.original_title}
  className="w-full h-64 object-cover rounded-lg shadow-md group-hover:scale-105 transition-transform duration-300"
  onError={(e) => {
    console.warn("Ảnh bị lỗi, thử lấy poster từ original_title…");

    // Tạo filename từ original_title
    const fallbackName = item.original_title
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
          {movie.title}
        </h2>
        <p><b>Tên gốc:</b> {movie.original_title}</p>
        <p><b>Ngày công chiếu:</b> {movie.release_date}</p>
        <p><b>Đạo diễn:</b> {movie.director}</p>
        <p><b>Diễn viên:</b> {movie.stars}</p>
        <p><b>Thể loại:</b> {movie.genres_vn}</p>
        <p className="mt-3 text-gray-700 dark:text-gray-400 italic">
          {movie.overview}
        </p>
      </div>
    </div>
  );
}
