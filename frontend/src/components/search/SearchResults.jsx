// components/search/SearchResults.jsx
import { Loader2, Film, User } from "lucide-react";
import MovieCard from "./MovieCard";

export default function SearchResults({ loading, results, actorInfo, onSelectMovie, getPosterUrl, BaseURL }) {
  if (loading) {
    return (
      <div className="flex flex-col items-center py-20">
        <div className="relative">
          <Loader2 className="w-20 h-20 text-indigo-600 animate-spin" />
          <Film className="w-10 h-10 text-purple-600 absolute top-5 left-5 animate-pulse" />
        </div>
        <p className="mt-6 text-xl text-gray-600 dark:text-gray-400">AI đang phân tích...</p>
      </div>
    );
  }

  if (actorInfo?.actor) {
    return (
      <div className="mb-10 p-8 bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-900/30 dark:to-orange-900/30 rounded-3xl border-2 border-yellow-400 dark:border-yellow-700 shadow-2xl">
        <h4 className="text-2xl font-bold text-orange-700 dark:text-orange-400 flex items-center mb-4">
          <User className="w-10 h-10 mr-4" />
          Phát hiện diễn viên: <span className="ml-3 text-3xl">{actorInfo.actor}</span>
        </h4>
        <p className="text-lg font-bold text-green-600 dark:text-green-400">
          Độ tương đồng: {(actorInfo.similarity * 100).toFixed(1)}%
        </p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-20">
        <Film className="w-24 h-24 mx-auto text-gray-300 dark:text-gray-700 mb-6" />
        <p className="text-xl text-gray-500 dark:text-gray-400">
          Chưa có kết quả. Hãy thử tìm kiếm bằng từ khóa hoặc hình ảnh khác nhé!
        </p>
      </div>
    );
  }

  return (
    <div className="mt-10">
      <h3 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-8">
        Kết Quả Tìm Kiếm ({results.length})
      </h3>
      <div className="grid gap-10">
        {results.map((movie, idx) => (
          <MovieCard
            key={idx}
            movie={movie}
            onClick={onSelectMovie}
            getPosterUrl={getPosterUrl}
            BaseURL={BaseURL}
          />
        ))}
      </div>
    </div>
  );
}