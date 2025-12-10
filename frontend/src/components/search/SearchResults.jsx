// components/search/SearchResults.jsx
import { Loader2, Film, User, Clapperboard, Sparkles } from "lucide-react";
import MovieCard from "./MovieCard";

export default function SearchResults({ 
  loading, 
  results, 
  actorInfo, 
  onSelectMovie, 
  getPosterUrl, 
  BaseURL,
  searchMode = "actor"
}) {
  // Hỗ trợ mọi cấu trúc backend (cũ + mới)
  const detectedActor = actorInfo?.detected_actor || 
                       actorInfo?.raw_results?.detected_actor || 
                       (actorInfo?.actor ? { name: actorInfo.actor, similarity: actorInfo.similarity } : null);

  const actorFilmography = actorInfo?.actor_filmography || 
                          actorInfo?.raw_results?.actor_filmography || 
                          [];

  const hasActorDetected = !!detectedActor;

  if (loading) {
    return (
      <div className="flex flex-col items-center py-24">
        <div className="relative">
          <Loader2 className="w-24 h-24 text-indigo-600 animate-spin" />
          <Sparkles className="w-12 h-12 text-purple-600 absolute -top-2 -right-2 animate-pulse" />
        </div>
        <p className="mt-8 text-2xl font-bold text-gray-700 dark:text-gray-300">
          Đang phân tích...
        </p>
      </div>
    );
  }

  // ƯU TIÊN: Tìm diễn viên + có nhận diện thành công
  if (searchMode === "actor" && hasActorDetected) {
    const totalMovies = actorFilmography.length;

 return (
<div className="space-y-10">
  {/* Ô DIỄN VIÊN – SIÊU NHỎ GỌN, HIỆN ĐẠI NHƯ APPLE */}
  <div className="max-w-3xl mx-auto">
    <div className="backdrop-blur-xl bg-white/70 dark:bg-gray-900/80 rounded-3xl border border-white/20 dark:border-gray-700/50 shadow-2xl p-5 flex items-center gap-5 overflow-hidden">
      {/* Avatar + hiệu ứng glow */}
      <div className="relative flex-shrink-0">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-400 to-red-600 rounded-full blur-xl opacity-70 scale-125 animate-pulse"></div>
        <div className="relative w-20 h-20 bg-gradient-to-br from-orange-500 to-red-600 rounded-full flex items-center justify-center shadow-2xl ring-4 ring-white/50">
          <User className="w-10 h-10 text-white" />
        </div>
      </div>

      {/* Thông tin chính */}
      <div className="flex-1 min-w-0">
        <h2 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-red-600 dark:from-orange-400 dark:to-red-400 truncate">
          {detectedActor.name}
        </h2>
        <div className="flex items-center gap-4 mt-2">
          <span className="text-lg font-bold text-green-600 flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            {(detectedActor.similarity * 100).toFixed(1)}% khớp
          </span>
          <span className="text-gray-600 dark:text-gray-400 text-sm font-medium">
            • Tham gia <span className="text-purple-600 font-bold">{totalMovies}</span> phim
          </span>
        </div>
      </div>

      {/* Badge trạng thái */}
      <div className="flex-shrink-0">
        <div className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full text-white font-bold text-sm shadow-lg">
          ĐÃ XÁC NHẬN
        </div>
      </div>
    </div>
  </div>

  {/* DANH SÁCH PHIM – POSTER SIÊU LỚN, ĐẸP NHƯ NETFLIX */}
        {/* PHẦN DANH SÁCH PHIM */}
        {totalMovies > 0 ? (
          <div>
            <h3 className="text-3xl font-bold text-center mb-10 text-gray-800 dark:text-gray-100 
                           flex items-center justify-center gap-4">
              <Clapperboard className="w-10 h-10 text-purple-600" />
              Tất cả phim đã tham gia
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
              {actorFilmography.map((movie, i) => (
                <div
                  key={i}
                  onClick={() => onSelectMovie(movie)}
                  className="group cursor-pointer transform hover:scale-105 transition-all duration-300"
                >
                  <div className="relative overflow-hidden rounded-2xl shadow-xl bg-gray-200 dark:bg-gray-800">
                    <img
                      src={getPosterUrl(movie)}
                      alt={movie.title}
                      className="w-full h-72 object-cover group-hover:scale-110 transition-transform duration-500"
                      onError={(e) => {
                        e.target.src = BaseURL + "300x450/1a1a1a/ffffff?text=No+Poster";
                      }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent 
                                    opacity-0 group-hover:opacity-100 transition-opacity duration-300 
                                    flex flex-col justify-end p-4">
                      <p className="text-white font-bold text-sm line-clamp-2">{movie.title}</p>
                      <p className="text-amber-400 text-xs mt-1 font-medium">
                        Vai: {movie.role_name || "Không rõ"}
                      </p>
                      <p className="text-gray-300 text-xs mt-1">{movie.year}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          // Khi nhận diện được nhưng chưa có phim trong DB
          <div className="text-center py-20 bg-gradient-to-br from-gray-100 to-gray-200 
                          dark:from-gray-800 dark:to-gray-900 rounded-3xl border-2 border-dashed border-gray-400">
            <User className="w-20 h-20 mx-auto text-gray-500 mb-6" />
            <p className="text-2xl font-bold text-gray-700 dark:text-gray-300">
              Diễn viên <span className="text-orange-600">{detectedActor.name}</span> đã được nhận diện thành công!
            </p>
            <p className="text-lg text-gray-600 dark:text-gray-400 mt-4">
              Hiện tại chưa có phim của diễn viên này trong hệ thống.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-6">
              Chúng tôi sẽ cập nhật sớm nhất có thể
            </p>
          </div>
        )}



        
        {/* Phim gợi ý từ nội dung */}
        {results.length > 0 && (
          <div className="mt-16 pt-12 border-t-4 border-dashed border-gray-300 dark:border-gray-700">
            <h3 className="text-2xl font-bold text-center mb-8 text-gray-700 dark:text-gray-300">
              Phim tương tự từ nội dung ảnh
            </h3>
            <div className="grid gap-10">
              {results.map((movie, idx) => (
                <MovieCard key={idx} movie={movie} onClick={onSelectMovie} getPosterUrl={getPosterUrl} BaseURL={BaseURL} />
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Không có kết quả
  if (results.length === 0) {
    return (
      <div className="text-center py-24">
        <Film className="w-28 h-28 mx-auto text-gray-300 dark:text-gray-700 mb-8" />
        <p className="text-2xl font-semibold text-gray-600 dark:text-gray-400">
          {searchMode === "actor" 
            ? "Không nhận diện được diễn viên. Hãy thử ảnh rõ khuôn mặt hơn!" 
            : "Không tìm thấy phim tương tự. Hãy thử ảnh khác nhé!"}
        </p>
      </div>
    );
  }

  //==============================================================================================================
  // Kết quả tìm nội dung
  return (
    <div className="mt-10">
      <h3 className="text-4xl font-extrabold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 
                     bg-clip-text text-transparent text-center mb-12">
        Kết Quả Tìm Kiếm ({results.length} phim)
      </h3>
      <div className="grid gap-12">
        {results.map((movie, idx) => (
          <MovieCard key={idx} movie={movie} onClick={onSelectMovie} getPosterUrl={getPosterUrl} BaseURL={BaseURL} />
        ))}
      </div>
    </div>
  );
}