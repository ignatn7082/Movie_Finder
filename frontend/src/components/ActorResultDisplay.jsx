import React from "react";
import { User } from "lucide-react";

const ActorResultDisplay = ({ actorInfo, onSelectMovie, getPosterUrl, BaseURL }) => {
  if (!actorInfo || !actorInfo.actor || actorInfo.error) return null;

  return (
    <div className="space-y-6">
      <h4 className="text-2xl font-bold text-yellow-800 dark:text-yellow-200 flex items-center p-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
        <User className="w-6 h-6 mr-3" /> Diễn Viên Được Tìm Thấy: {actorInfo.actor}
      </h4>

      <p className="text-gray-700 dark:text-gray-300">
        Kết quả tìm kiếm khuôn mặt cho thấy sự tương đồng với diễn viên <b>{actorInfo.actor}</b> trong các bộ phim sau:
      </p>

      {actorInfo.movies.map((movie, index) => (
        <div key={movie.id || index} className="p-4 border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 shadow-lg">
          <h5 className="text-xl font-semibold text-blue-600 dark:text-blue-400 mb-4">
            {movie.title} ({movie.release_date?.split("-")[0] || "N/A"})
          </h5>

          <div className="flex flex-col md:flex-row gap-4">
            {/* Poster & Thông Tin */}
            <div className="w-full md:w-1/2 flex flex-col sm:flex-row gap-4">
              <img
                src={getPosterUrl(movie)}
                alt={movie.title}
                className="w-28 h-40 object-cover rounded-lg shadow-md flex-shrink-0 cursor-pointer hover:opacity-90 transition-opacity"
                onClick={() => onSelectMovie(movie)}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = BaseURL + "posters/default_poster.jpg";
                }}
              />

              <div className="min-w-0 flex-grow">
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">
                  <b>Đạo diễn:</b> {movie.director}
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">
                  <b>Thể loại:</b> {movie.genres}
                </p>

                <button
                  onClick={() => onSelectMovie(movie)}
                  className="mt-2 text-blue-500 hover:text-blue-700 dark:text-blue-300 dark:hover:text-blue-500 font-medium text-sm border-b border-dashed border-blue-500"
                >
                  Xem Chi Tiết Phim
                </button>
              </div>
            </div>

            {/* Bảng Similarity */}
            <div className="w-full md:w-1/2">
              <h6 className="font-bold text-md text-gray-900 dark:text-white mb-2 border-b border-gray-300 dark:border-gray-600 pb-1">
                Độ Tương Đồng Diễn Viên (Trong Phim này)
              </h6>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Diễn Viên</th>
                      <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Độ Tương Đồng</th>
                    </tr>
                  </thead>

                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {movie.actor_similarities?.map((item, i) => (
                      <tr
                        key={i}
                        className={item.actor_name === actorInfo.actor ? "bg-yellow-50 dark:bg-yellow-900/30 font-semibold" : ""}
                      >
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                          {item.actor_name} <span className="text-xs text-gray-500 dark:text-gray-400 italic">({item.role})</span>
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-sm text-right">
                          <span className="text-blue-600 dark:text-blue-400">{(item.similarity * 100).toFixed(2)}%</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ActorResultDisplay;
