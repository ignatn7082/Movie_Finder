// components/search/MovieDetailModal.jsx
import { X } from "lucide-react";

export default function MovieDetailModal({ movie, onClose, getPosterUrl }) {
  if (!movie) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-6" onClick={onClose}>
      <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-3xl max-w-5xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <button onClick={onClose} className="absolute -top-4 -right-4 bg-red-600 text-white p-4 rounded-full shadow-2xl hover:bg-red-700 z-10">
          <X className="w-6 h-6" />
        </button>
        <div className="grid md:grid-cols-2">
          <div className="p-8">
            <img src={getPosterUrl(movie)} alt={movie.title} className="w-full rounded-2xl shadow-2xl border-8 border-white dark:border-gray-700" />
          </div>
          <div className="p-10 space-y-6">
            <h2 className="text-4xl font-extrabold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {movie.title}
            </h2>
            <p className="text-2xl text-gray-600 dark:text-gray-400">{movie.original_title}</p>
            <div className="space-y-4 text-lg">
              <p><strong className="text-indigo-600">Đạo diễn:</strong> {movie.director}</p>
              <p><strong className="text-purple-600">Thể loại:</strong> {movie.genres_vn}</p>
              {/* <p><strong className="text-green-600">Diễn viên:</strong> {movie.stars}</p> */}
            </div>
            <div className="pt-6 border-t-2 border-gray-200 dark:border-gray-700">
              <h3 className="text-2xl font-bold mb-4 text-indigo-600">Tóm tắt nội dung</h3>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
                {movie.overview || "Đang cập nhật..."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}