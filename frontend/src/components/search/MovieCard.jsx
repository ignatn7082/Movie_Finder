// components/search/MovieCard.jsx
import { Calendar, Clapperboard, Users } from "lucide-react";
import ActorSimilarityTable from "./ActorSimilarityTable";

export default function MovieCard({ movie, onClick, getPosterUrl, BaseURL }) {
  return (
    <div onClick={() => onClick(movie)} className="group bg-white dark:bg-gray-800 rounded-3xl shadow-xl hover:shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden transform hover:scale-[1.02] transition-all duration-500 cursor-pointer">
      <div className="flex flex-col lg:flex-row">
        <div className="lg:w-64 flex-shrink-0 relative overflow-hidden">
          <img
            src={getPosterUrl(movie)}
            alt={movie.title}
            className="w-full h-96 lg:h-full object-cover group-hover:scale-110 transition-transform duration-700"
            onError={(e) => { e.target.src = BaseURL + "300x450/1a1a1a/ffffff?text=No+Poster"; }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-end p-6">
            <p className="text-white font-bold text-lg">Xem chi tiết</p>
          </div>
        </div>

        <div className="p-8 flex-grow flex flex-col lg:flex-row gap-8">
          <div className="flex-1 space-y-5">
            <h4 className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">{movie.title}</h4>
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <span className="flex items-center text-gray-600 dark:text-gray-400">
                <Calendar className="w-5 h-5 mr-2" />
                {movie.release_date?.split('-')[0] || "N/A"}
              </span>
              {movie.similarity && (
                <span className="px-4 py-2 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full font-bold">
                  {(movie.similarity * 100).toFixed(1)}% khớp
                </span>
              )}
            </div>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed line-clamp-4">
              {movie.overview || "Chưa có tóm tắt."}
            </p>
            <div className="flex flex-wrap gap-6 text-sm">
              <div className="flex items-center text-gray-600 dark:text-gray-400">
                <Clapperboard className="w-5 h-5 mr-2 text-indigo-600" />
                <span className="font-medium">Đạo diễn:</span> {movie.director || "Đang cập nhật"}
              </div>
              <div className="flex items-center text-gray-600 dark:text-gray-400">
                <Users className="w-5 h-5 mr-2 text-purple-600" />
                <span className="font-medium">Diễn viên:</span> {movie.stars?.split(',')[0] || "Nhiều diễn viên"}
              </div>
            </div>
          </div>

          {movie.actors && movie.actors.length > 0 && (
            <ActorSimilarityTable actors={movie.actors} />
          )}
        </div>
      </div>
    </div>
  );
}