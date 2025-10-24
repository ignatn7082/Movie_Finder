import { X } from "lucide-react";

export default function MovieModal({ movie, onClose }) {
  if (!movie) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex justify-center items-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-2xl w-full p-6 relative animate-fadeIn">
        {/* Nút đóng */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-red-500"
        >
          <X size={24} />
        </button>

        {/* Nội dung */}
        <div className="flex flex-col md:flex-row gap-6">
          {/* Poster */}
          <img
            src={movie.poster}
            alt={movie.title}
            onError={(e) => (e.target.src = "/static/default_poster.jpg")}
            className="w-full md:w-1/3 h-72 object-cover rounded-lg shadow-md"
          />

          {/* Thông tin chi tiết */}
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-blue-600 mb-2">{movie.title}</h2>
            <p className="text-gray-500 text-sm mb-4">
              {movie.release_date} · {movie.genres}
            </p>

            <p className="text-gray-700 dark:text-gray-300 mb-2">
              🎬 <b>Đạo diễn:</b> {movie.director || "—"}
            </p>

            <p className="text-gray-700 dark:text-gray-300 mb-2">
              🌎 <b>Quốc gia:</b> {movie.production_countries || "—"}
            </p>

            <p className="text-gray-700 dark:text-gray-300 mb-2">
              🕒 <b>Thời lượng:</b> {movie.runtime ? `${movie.runtime} phút` : "—"}
            </p>

            <p className="text-gray-700 dark:text-gray-300 mb-2">
              ⭐ <b>Điểm đánh giá:</b> {movie.vote_average || "—"} ({movie.vote_count || 0} bình chọn)
            </p>

            <p className="text-gray-700 dark:text-gray-300 mb-4">
              🌟 <b>Diễn viên:</b> {movie.stars || "—"}
            </p>

            <div className="text-gray-800 dark:text-gray-200 text-sm leading-relaxed">
              {movie.overview || "Không có mô tả chi tiết cho phim này."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
