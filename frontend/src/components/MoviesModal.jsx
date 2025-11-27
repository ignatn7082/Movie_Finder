import { X, Play, Clock, Calendar, MapPin, Star, Users } from "lucide-react";

export default function MoviesModals({ movie, onClose }) {
  const BaseURL = "http://localhost:8000/static/";

  if (!movie) return null;

  return (
    <>
      {/* Overlay + ESC để đóng */}
<div
  className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4"
  onClick={onClose}
  role="button"
  tabIndex={-1}
  onKeyDown={(e) => e.key === "Escape" && onClose()}
>
  <div
    className="relative w-full max-w-5xl max-h-[95vh] overflow-y-auto bg-gradient-to-b from-gray-900 via-gray-800 to-black rounded-3xl shadow-4xl outline-none"
    onClick={(e) => e.stopPropagation()}
  >
          {/* Background poster mờ + gradient */}
          <div className="absolute inset-0 opacity-30">
            <img
              src={movie.poster ? BaseURL + movie.poster : BaseURL + "posters/default_poster.jpg"}
              alt=""
              className="w-full h-full object-cover"
              onError={(e) => (e.target.src = BaseURL + "posters/default_poster.jpg")}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-transparent via-black/50 to-black" />
          </div>

          {/* Nút đóng */}
          <button
            onClick={onClose}
            className="absolute top-6 right-6 z-10 p-3 bg-black/50 backdrop-blur-md rounded-full hover:bg-black/70 transition-all hover:scale-110"
          >
            <X className="w-7 h-7 text-white" />
          </button>

          <div className="relative z-10 p-8 md:p-12 lg:p-16">
            <div className="grid md:grid-cols-3 gap-10">
              {/* Poster chính – to, đẹp */}
              <div className="md:col-span-1">
                <img
                  src={movie.poster ? BaseURL + movie.poster : BaseURL + "posters/default_poster.jpg"}
                  alt={movie.title || movie.original_title}
                  className="w-full rounded-2xl shadow-2xl border-4 border-white/10"
                  onError={(e) => (e.target.src = BaseURL + "posters/default_poster.jpg")}
                />
              </div>

              {/* Thông tin phim – sang trọng */}
              <div className="md:col-span-2 text-white space-y-6">
                {/* Tiêu đề + năm */}
                <div>
                  <h1 className="text-4xl md:text-5xl font-black bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent drop-shadow-lg">
                    {movie.title || movie.original_title}
                  </h1>
                  <div className="flex items-center gap-4 mt-3 text-gray-300">
                    <span className="flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      {movie.release_date || "Chưa rõ năm"}
                    </span>
                    <span className="flex items-center gap-2">
                      <Clock className="w-5 h-5" />
                      {movie.runtime ? `${movie.runtime} phút` : "Đang cập nhật"}
                    </span>
                  </div>
                </div>

                {/* Thể loại – dạng tag đẹp */}
                <div className="flex flex-wrap gap-3">
                  {(movie.genres_vn || "Phim Việt Nam")
                    .split(",")
                    .map((g, i) => (
                      <span
                        key={i}
                        className="px-5 py-2 bg-white/10 backdrop-blur-md rounded-full text-sm font-medium border border-white/20"
                      >
                        {g.trim()}
                      </span>
                    ))}
                </div>

                {/* Thông tin nhanh */}
                <div className="grid grid-cols-2 gap-6 text-lg">
                  <div className="flex items-center gap-3">
                    <Users className="w-6 h-6 text-purple-400" />
                    <div>
                      <p className="text-gray-400 text-sm">Đạo diễn</p>
                      <p className="font-semibold">{movie.director || "Đang cập nhật"}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <MapPin className="w-6 h-6 text-blue-400" />
                    <div>
                      <p className="text-gray-400 text-sm">Quốc gia</p>
                      <p className="font-semibold">{movie.production_countries || "Việt Nam"}</p>
                    </div>
                  </div>
                </div>

                {/* Diễn viên chính */}
                {movie.stars && (
                  <div>
                    <p className="text-gray-400 text-sm mb-2">Diễn viên</p>
                    <p className="font-medium text-lg leading-relaxed">{movie.stars}</p>
                  </div>
                )}

                {/* Mô tả phim */}
                <div>
                  <p className="text-gray-400 text-sm mb-3">Nội dung phim</p>
                  <p className="text-gray-200 leading-relaxed text-justify">
                    {movie.overview || "Chưa có mô tả chi tiết cho bộ phim này."}
                  </p>
                </div>

                {/* Nút xem phim (tùy chọn sau này) */}
                <div className="pt-6">
                  <button className="flex items-center gap-4 px-8 py-5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl font-bold text-xl shadow-2xl hover:scale-105 transition-all duration-300">
                    <Play className="w-8 h-8 fill-white" />
                    Xem ngay
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}