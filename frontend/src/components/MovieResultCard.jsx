// import React from 'react';

// // Component Movie Result Card
// const MovieResultCard = ({ movie, BaseURL, setSelected }) => {
//     // Xử lý poster URL
//     const posterUrl = movie.poster && movie.poster.startsWith('http') ? movie.poster : `${BaseURL}${movie.poster}`;
    
//     // Xử lý tên phim chính (Ưu tiên original_title)
//     const displayTitle = movie.original_title || movie.title || "Không rõ tên";

//     return (
//         <div 
//             onClick={() => setSelected(movie)}
//             className="flex bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 dark:border-gray-700 p-3"
//         >
//             <img 
//                 src={posterUrl} 
//                 alt={displayTitle} 
//                 className="w-16 h-24 object-cover rounded-md flex-shrink-0 mr-3"
//                 onError={(e) => { e.target.onerror = null; e.target.src = "placeholder.jpg"; }} // Fallback
//             />
//             <div className="flex-grow min-w-0">
//                 <h4 className="text-md font-bold text-gray-900 dark:text-white truncate" title={displayTitle}>
//                     {displayTitle}
//                 </h4>
//                 <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
//                     {movie.release_date ? `(${movie.release_date.split('-')[0]})` : 'N/A'}
//                 </p>
//                 {movie.similarity !== undefined && (
//                     <p className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 mt-1">
//                         Độ tương đồng: **{(movie.similarity * 100).toFixed(2)}%**
//                     </p>
//                 )}
//             </div>
//         </div>
//     );
// };

// export default MovieResultCard;


import React from "react";

const MovieResultCard = ({ movie, onClick, getPosterUrl, BaseURL = "/static/", mainActor }) => {
  // Poster URL resolution: prefer getPosterUrl if provided
  const posterUrl = typeof getPosterUrl === "function" ? getPosterUrl(movie) : (movie.poster && movie.poster.startsWith("http") ? movie.poster : `${BaseURL}${movie.poster || ""}`);

  const displayTitle = movie.original_title || movie.title || "Không rõ tên";

  const handleCardClick = () => {
    if (typeof onClick === "function") return onClick(movie);
    if (typeof movie.setSelected === "function") return movie.setSelected(movie);
  };

  // --- Normalize actor similarities from multiple possible shapes ---
  let actorSimsRaw = movie.actor_similarities || movie.actor_matches || movie.actors || movie.actor_similarity_list || [];
  // If backend returned object (single) or string, wrap into array
  if (!Array.isArray(actorSimsRaw) && actorSimsRaw) {
    actorSimsRaw = [actorSimsRaw];
  }
  const actorSims = Array.isArray(actorSimsRaw) ? actorSimsRaw : [];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-lg p-4 space-y-4">
      <div
        onClick={handleCardClick}
        className="flex cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition rounded-lg p-2"
      >
        <img
          src={posterUrl}
          alt={displayTitle}
          className="w-20 h-28 object-cover rounded-md shadow mr-4"
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = BaseURL + "posters/default_poster.jpg";
          }}
        />

        <div className="flex-grow min-w-0">
          <h4 className="text-lg font-bold text-gray-900 dark:text-white truncate" title={displayTitle}>
            {displayTitle}
          </h4>

          <p className="text-sm text-gray-600 dark:text-gray-400">
            {movie.release_date ? `(${movie.release_date.split("-")[0]})` : "N/A"}
          </p>

          {movie.similarity !== undefined && (
            <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 mt-1">
              Độ tương đồng: {(movie.similarity * 100).toFixed(2)}%
            </p>
          )}

          {movie.role_name && (
            <p className="text-sm text-indigo-600 dark:text-indigo-400 mt-1">Vai diễn: {movie.role_name}</p>
          )}
        </div>
      </div>

      {actorSims.length > 0 ? (
        <div className="mt-2">
          <h5 className="font-semibold text-gray-900 dark:text-white mb-2 text-sm border-b border-gray-300 dark:border-gray-600 pb-1">
            Độ Tương Đồng Diễn Viên
          </h5>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Diễn Viên
                  </th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Tương Đồng
                  </th>
                </tr>
              </thead>

              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {actorSims.map((item, i) => {
                   // support both shapes: [actor_name, sim] or {actor_name, similarity, role}
                   let actor_name = "";
                   let role = "";
                   let sim = 0;
                   if (Array.isArray(item) && item.length >= 2) {
                     actor_name = item[0];
                     sim = Number(item[1]) || 0;
                   } else if (typeof item === "object" && item !== null) {
                     actor_name = item.actor_name || item.name || "";
                     role = item.role || item.role_name || "";
                     sim = Number(item.similarity ?? item.sim) || 0;
                   } else {
                     actor_name = String(item);
                     sim = 0;
                   }

                   return (
                     <tr key={i} className={mainActor && actor_name === mainActor ? "bg-yellow-50 dark:bg-yellow-900/30 font-semibold" : ""}>
                       <td className="px-3 py-2 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap">
                         {actor_name}
                         {role ? (
                           <span className="text-xs text-gray-500 dark:text-gray-400 ml-1 italic"> ({role})</span>
                         ) : null}
                       </td>

                       <td className="px-3 py-2 text-sm text-right">
                         <span className="text-blue-600 dark:text-blue-400">{(sim * 100).toFixed(2)}%</span>
                       </td>
                     </tr>
                   );
                 })}
               </tbody>
             </table>
           </div>
         </div>
      ) : (
        <div className="mt-2 text-sm text-gray-500 dark:text-gray-400 italic">Không có dữ liệu so sánh độ tương đồng diễn viên cho phim này.</div>
      )}
    </div>
  );
};

export default MovieResultCard;
