import React from "react";
import { Film, User, Percent } from "lucide-react";

/**
 * Component hiển thị kết quả tìm kiếm phim.
 * Được tối ưu để hiển thị độ tương đồng tổng thể và danh sách độ tương đồng diễn viên chi tiết.
 * * @param {object} props
 * @param {object} props.movie Dữ liệu phim, có thể bao gồm similarity, role_name, actor_similarities/actor_matches/actors.
 * @param {function} props.onClick Hàm xử lý khi click vào thẻ phim.
 * @param {function} props.getPosterUrl Hàm tùy chỉnh để lấy URL poster.
 * @param {Array<object|Array>} props.actorSimilarityList Mảng tương đồng diễn viên chi tiết (nếu có).
 * @param {string} props.BaseURL URL cơ sở cho tài nguyên tĩnh (mặc định là "/static/").
 * @param {string} props.mainActor Tên diễn viên chính được truy vấn (dùng để highlight).
 */
const MovieResultCard = ({ movie, onClick, getPosterUrl, BaseURL = "/static/", mainActor,actorSimilarityList }) => {
  // 1. Xử lý Poster URL
  const defaultPosterUrl = `${BaseURL}posters/default_poster.jpg`;
  const posterUrl = typeof getPosterUrl === "function" 
    ? getPosterUrl(movie) 
    : (movie.poster && movie.poster.startsWith("http") 
      ? movie.poster 
      : `${BaseURL}${movie.poster || defaultPosterUrl}`
    );

  const displayTitle = movie.original_title || movie.title || "Không rõ tên";

  const handleCardClick = () => {
    // Ưu tiên onClick prop, sau đó đến setSelected nếu được truyền trong object movie (ít dùng)
    if (typeof onClick === "function") return onClick(movie);
    if (typeof movie.setSelected === "function") return movie.setSelected(movie);
  };

  // 2. Normalize dữ liệu tương đồng diễn viên
let actorSimsRaw = actorSimilarityList 
    || movie.actor_similarities 
    || movie.actor_matches 
    || movie.actors 
    || movie.actor_similarity_list 
    || []; 
  
  if (!Array.isArray(actorSimsRaw) && actorSimsRaw) {
    actorSimsRaw = [actorSimsRaw];
  }
  const actorSims = Array.isArray(actorSimsRaw) ? actorSimsRaw : [];

  const getActorData = (item) => {
    let actor_name = "";
    let role = "";
    let sim = 0;

    if (Array.isArray(item) && item.length >= 2) {
      // Dạng [actor_name, sim]
      actor_name = item[0];
      sim = Number(item[1]) || 0;
    } else if (typeof item === "object" && item !== null) {
      // Dạng {actor_name, similarity, role} hoặc {name, sim}
      actor_name = item.actor_name || item.name || "";
      role = item.role || item.role_name || "";
      sim = Number(item.similarity ?? item.sim) || 0;
    } else if (typeof item === 'string' && item) {
      // Dạng chỉ có tên diễn viên (thường sim = 0 hoặc 1 nếu là match chính xác)
      actor_name = item;
      sim = 0; // Giả sử 0 nếu không có sim đi kèm
    }

    return { actor_name, role, sim };
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-4 space-y-4 w-full">
      
      {/* PHẦN THÔNG TIN PHIM CHÍNH & TƯƠNG ĐỒNG TỔNG THỂ */}
      <div
        onClick={handleCardClick}
        className="flex cursor-pointer p-2 -m-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-gray-700/50 transition-colors"
        title={`Click để xem chi tiết phim ${displayTitle}`}
      >
        <img
          src={posterUrl}
          alt={`Poster phim ${displayTitle}`}
          className="w-20 h-28 object-cover rounded-md shadow-md flex-shrink-0 mr-4 border border-gray-300 dark:border-gray-600"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = defaultPosterUrl;
          }}
        />

        <div className="flex-grow min-w-0 flex flex-col justify-center">
          <h4 className="text-xl font-extrabold text-gray-900 dark:text-white truncate" title={displayTitle}>
            <Film className="inline w-5 h-5 mr-1 text-indigo-500" />
            {displayTitle}
          </h4>

          <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
            {movie.release_date ? `Năm: ${movie.release_date.split("-")[0]}` : "Năm: N/A"}
          </p>

          {/* Độ tương đồng tổng thể (nếu có) */}
          {movie.similarity !== undefined && (
            <p className="text-md font-bold text-indigo-600 dark:text-indigo-400 mt-1 flex items-center">
              <Percent className="w-4 h-4 mr-1" />
              Độ tương đồng: <span className="ml-1 text-lg">{(movie.similarity * 100).toFixed(2)}%</span>
            </p>
          )}

          {/* Vai diễn (chỉ hiển thị nếu là kết quả tìm kiếm Role/Actor) */}
          {movie.role_name && (
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              <User className="w-4 h-4 mr-1 inline" />
              Vai diễn: <span className="font-semibold">{movie.role_name}</span>
            </p>
          )}
        </div>
      </div>

      {/* PHẦN BẢNG ĐỘ TƯƠNG ĐỒNG DIỄN VIÊN */}
      {actorSims.length > 0 && (
        <div className="pt-3 border-t border-gray-100 dark:border-gray-700">
          <h5 className="font-bold text-gray-900 dark:text-white mb-2 text-sm flex items-center">
            <User className="w-4 h-4 mr-1" /> Chi tiết Tương Đồng Diễn Viên
          </h5>

          <div className="overflow-x-auto rounded-lg border border-gray-300 dark:border-gray-600">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-100 dark:bg-gray-700">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                    Diễn Viên
                  </th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider w-1/4">
                    Tương Đồng
                  </th>
                </tr>
              </thead>

              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {actorSims.map((item, i) => {
                   const { actor_name, role, sim } = getActorData(item);

                   // Highlight nếu diễn viên này là diễn viên được truy vấn
                   const isMainActor = mainActor && actor_name && actor_name.toLowerCase().trim() === mainActor.toLowerCase().trim();

                   return (
                     <tr key={i} className={isMainActor ? "bg-yellow-50 dark:bg-yellow-900/30 font-semibold" : "hover:bg-gray-50 dark:hover:bg-gray-700"}>
                       <td className="px-3 py-2 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap">
                         {actor_name}
                         {role ? (
                           <span className="text-xs text-gray-500 dark:text-gray-400 ml-1 italic"> ({role})</span>
                         ) : null}
                       </td>

                       <td className="px-3 py-2 text-sm text-right font-medium">
                         <span className={`px-2 py-0.5 rounded-full text-xs ${sim * 100 >= 80 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'}`}>
                            {(sim * 100).toFixed(2)}%
                         </span>
                       </td>
                     </tr>
                   );
                 })}
               </tbody>
             </table>
           </div>
         </div>
      )}

      {/* THÔNG BÁO KHI KHÔNG CÓ DỮ LIỆU TƯƠNG ĐỒNG */}
      {movie.similarity !== undefined && actorSims.length === 0 && (
         <div className="mt-2 text-sm text-gray-500 dark:text-gray-400 italic pt-2 border-t border-gray-100 dark:border-gray-700">
           Không có dữ liệu so sánh độ tương đồng diễn viên chi tiết.
         </div>
      )}
    </div>
  );
};

export default MovieResultCard;