export default function MovieModal({ movie, onClose }) {
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
          src={movie.poster}
          alt={movie.title}
          className="w-full rounded-lg mb-4 object-contain"
        />
        <h2 className="text-2xl font-bold text-blue-600 mb-2">
          {movie.title}
        </h2>
        <p><b>Tên gốc:</b> {movie.original_title}</p>
        <p><b>Ngày công chiếu:</b> {movie.release_date}</p>
        <p><b>Đạo diễn:</b> {movie.director}</p>
        <p><b>Diễn viên:</b> {movie.stars}</p>
        <p><b>Thể loại:</b> {movie.genres}</p>
        <p className="mt-3 text-gray-700 dark:text-gray-400 italic">
          {movie.overview}
        </p>
      </div>
    </div>
  );
}
