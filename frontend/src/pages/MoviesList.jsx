// import { useEffect, useState, useMemo } from "react";
// import { Search, Film, ChevronLeft, ChevronRight, SortAsc, SortDesc } from "lucide-react";
// import { API_ENDPOINTS } from "../config/api";
// import MovieModal from "../components/MoviesModal";



// export default function MoviesList() {
//   const [selectedMovie, setSelectedMovie] = useState(null);
//   const [movies, setMovies] = useState([]);
//   const [filtered, setFiltered] = useState([]);
//   const [query, setQuery] = useState("");
//   const [page, setPage] = useState(1);
//   const [sortAsc, setSortAsc] = useState(true);
//   const perPage = 8;

//   useEffect(() => {
//     fetchMovies();
//   }, []);

//   const fetchMovies = async () => {
//     try {
//       // Try to page through API until we've fetched all movies.
//       const pageSize = 100;
//       let page = 1;
//       let all = [];

//       while (true) {
//         const url = `${API_ENDPOINTS.movies}?page=${page}&per_page=${pageSize}`;
//         const res = await fetch(url);
//         const data = await res.json();

//         // Support two shapes: { movies, total, page, per_page } or plain array
//         const pageMovies = Array.isArray(data)
//           ? data
//           : Array.isArray(data.movies)
//           ? data.movies
//           : [];

//         all = all.concat(pageMovies);

//         // If API provided total, stop when we've got all
//         if (!Array.isArray(data) && typeof data.total === "number") {
//           if (all.length >= data.total) break;
//         }

//         // If this page returned fewer than pageSize, assume last page
//         if (pageMovies.length < pageSize) break;

//         page += 1;
//         // safety cap to avoid infinite loop
//         if (page > 1000) break;
//       }

//       setMovies(all);
//       setFiltered(all);
//     } catch (err) {
//       console.error("Failed to load movies:", err);
//     }
//   };

//   const BaseURL = "http://localhost:8000/static/";

//   // Tìm kiếm phim
//   const handleSearch = (e) => {
//     const q = e.target.value.toLowerCase();
//     setQuery(q);
//     const filteredList = movies.filter(
//       (m) =>
//         m.original_title.toLowerCase().includes(q) ||
//         m.title.toLowerCase().includes(q) ||
//         m.director.toLowerCase().includes(q) ||
//         m.genres_vn.toLowerCase().includes(q)
//     );
//     setFiltered(filteredList);
//     setPage(1);
//   };

//   //  Sắp xếp theo tên phim
//   const toggleSort = () => {
//     const sorted = [...filtered].sort((a, b) =>
//       sortAsc ? b.title.localeCompare(a.title) : a.title.localeCompare(b.title)
//     );
//     setFiltered(sorted);
//     setSortAsc(!sortAsc);
//   };

//   //  Tính dữ liệu cho trang hiện tại
//   const totalPages = Math.ceil(filtered.length / perPage);
//   const currentMovies = useMemo(() => {
//     const start = (page - 1) * perPage;
//     return filtered.slice(start, start + perPage);
//   }, [filtered, page]);

//   return (
//     <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-6">
//       {/* Header */}
//       <div className="flex flex-wrap items-center justify-between mb-6 gap-3">
//         <h1 className="text-3xl font-bold text-blue-600 flex items-center gap-2">
//           <Film className="w-8 h-8" /> Danh sách phim 
//         </h1>
//         <div className="flex items-center gap-2">
//           <div className="flex items-center border rounded-lg px-3 py-1 bg-white dark:bg-gray-800">
//             <Search className="w-4 h-4 text-gray-500" />
//             <input
//               type="text"
//               placeholder="Tìm kiếm theo tên, đạo diễn, thể loại..."
//               value={query}
//               onChange={handleSearch}
//               className="bg-transparent outline-none px-2 text-base w-64"
//             />
//           </div>

//           <button
//             onClick={toggleSort}
//             className="flex items-center gap-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
//             title="Sắp xếp theo tên phim"
//           >
//             {sortAsc ? <SortAsc size={16} /> : <SortDesc size={16} />}
//             Sắp xếp
//           </button>
//         </div>
//       </div>

//       {/* Danh sách phim */}
//       <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
//         {currentMovies.length > 0 ? (
//           currentMovies.map((movie) => (
//             <div
//               key={movie.id}
//               onClick={() => setSelectedMovie(movie)}
//               className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300"
//             >
//               <div className="flex items-center justify-center bg-gray-50 dark:bg-gray-900" style={{ minHeight: "12rem" }}>
//                 <img
//                   src={ movie.poster ? BaseURL + movie.poster : BaseURL + "posters/default_poster.jpg" }
//                   alt={movie.original_title}
//                   className="rounded-md"
//                   // giữ nguyên kích thước gốc (tỉ lệ), nhưng không vượt quá khung
//                   style={{ width: "auto", height: "auto", maxWidth: "100%", maxHeight: "40vh" }}
//                   onError={(e) => { e.target.onerror = null; e.target.src = BaseURL + "posters/default_poster.jpg"; }}
//                 />
//               </div>
//               <div className="p-4">
//                 <h2 className="font-semibold text-lg text-blue-600 truncate">
//                   {movie.original_title}
//                 </h2>
//                 <p className="text-base">🎬 <b>Ngày khởi chiếu:</b> {movie.release_date}</p>
//                 <p className="text-base">
//                   🎬 <b>Đạo diễn:</b> {movie.director || "—"}
//                 </p>
//                 <p className="text-base">🎬 <b>Thể loại:</b> {movie.genres_vn}</p>
//                 <p className="text-base mt-2 text-gray-700 dark:text-gray-300">
//                   {/* {movie.overview} */}
//                 </p>
//               </div>
//             </div>
//           ))
//         ) : (
//           <p className="text-gray-500 italic col-span-full text-center">
//             Không có phim nào được tìm thấy.
//           </p>
//         )}
//       </div>

//       {/* Single modal rendered once */}
//       {selectedMovie && (
//         <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
//       )}

//       {/* Pagination */}
//       {filtered.length > perPage && (
//         <div className="flex items-center justify-center gap-4 mt-8">
//           <button
//             disabled={page === 1}
//             onClick={() => setPage(page - 1)}
//             className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-40"
//           >
//             <ChevronLeft />
//           </button>

//           <span className="text-base">
//             Trang <b>{page}</b> / {totalPages}
//           </span>

//           <button
//             disabled={page === totalPages}
//             onClick={() => setPage(page + 1)}
//             className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-40"
//           >
//             <ChevronRight />
//           </button>
//         </div>
//       )}
//     </div>
//   );
// }

// Định nghĩa danh sách các thể loại duy nhất để hiển thị sidebar
// const GENRES = [
//   "Hành Động", "Lãng Mạn", "Chính Kịch", "Hài", 
//   "Tội Phạm", "Kinh Dị", "Giả Tưởng", "Khoa Học Viễn Tưởng",
//   "Gia Đình", "Hoạt Hình", "Chiến Tranh", "Bí Ẩn",
//   "Âm Nhạc","Phiêu Lưu","Tội Phạm"
// ];
import { useEffect, useState, useMemo } from "react";
import { Search, Film, ChevronLeft, ChevronRight, SortAsc, SortDesc, X } from "lucide-react";
import { API_ENDPOINTS } from "../config/api";
import MoviesModals from "../components/MoviesModal";

// Định nghĩa danh sách các thể loại duy nhất để hiển thị sidebar
const GENRES = [
  "Hành Động", "Lãng Mạn", "Chính Kịch", "Hài", 
  "Tội Phạm", "Kinh Dị", "Giả Tưởng", "Khoa Học Viễn Tưởng",
  "Gia Đình", "Hoạt Hình", "Chiến Tranh", "Bí Ẩn",
  "Âm Nhạc","Phiêu Lưu"
];

export default function MoviesList() {
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [movies, setMovies] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [page, setPage] = useState(1);
  const [sortAsc, setSortAsc] = useState(true);
  const perPage = 8;
  const [filteredList, setFilteredList] = useState([]);

  // Hàm helper để kiểm tra mảng (giữ nguyên theo mẫu của bạn)
  const ArrayOfData = (data) => Array.isArray(data);

  // Tính số lượng phim theo từng thể loại
  const genreCounts = useMemo(() => {
    const counts = {};
    const uniqueGenres = [...new Set(GENRES)]; 
    uniqueGenres.forEach(genre => {
        counts[genre] = movies.filter(m => m.genres_vn?.includes(genre)).length;
    });
    return counts;
  }, [movies]);


  useEffect(() => {
    fetchMovies();
  }, []);

  useEffect(() => {
    let list = movies;

    // 1. Lọc theo Genre (Thể loại)
    if (selectedGenre) {
        list = list.filter(m => m.genres_vn?.includes(selectedGenre));
    }
    
    // 2. Lọc theo Query (Tìm kiếm bằng chữ)
    if (query) {
        const q = query.toLowerCase();
        list = list.filter(
            (m) =>
                m.original_title?.toLowerCase().includes(q) ||
                m.title?.toLowerCase().includes(q) ||
                m.director?.toLowerCase().includes(q) ||
                m.genres_vn?.toLowerCase().includes(q) ||
                m.stars?.toLowerCase().includes(q)
        );
    }
    
    // 3. Sắp xếp (Duy trì thứ tự sắp xếp hiện tại)
    const sorted = [...list].sort((a, b) =>
        sortAsc ? a.title.localeCompare(b.title) : b.title.localeCompare(a.title)
    );

    setFilteredList(sorted);
    setPage(1); // Reset về trang 1 sau khi lọc/tìm kiếm
  }, [movies, query, selectedGenre, sortAsc]);
  
  const fetchMovies = async () => { 
    try {
        const pageSize = 100;
        let page = 1;
        let all = [];

        while (true) {
            const url = `${API_ENDPOINTS.movies}?page=${page}&per_page=${pageSize}`;
            const res = await fetch(url);
            const data = await res.json();

            const pageMovies = Array.isArray(data)
                ? data
                : Array.isArray(data.movies)
                ? data.movies
                : [];

            all = all.concat(pageMovies);

            if (!ArrayOfData(data) && typeof data.total === "number") {
                if (all.length >= data.total) break;
            }

            if (pageMovies.length < pageSize) break;

            page += 1;
            if (page > 1000) break;
        }

        setMovies(all);
        setFilteredList(all);
    } catch (err) {
        console.error("Failed to load movies:", err);
    }
  };

  const BaseURL = "http://localhost:8000/static/";

  const handleSearch = (e) => {
    setQuery(e.target.value);
  };
  
  // LOGIC: Thêm/Bỏ thể loại được chọn
  const handleFilterByGenre = (genre) => {
      setSelectedGenre(prevGenre => 
          prevGenre === genre ? null : genre // Nếu click vào cái đang chọn -> null, ngược lại -> chọn cái mới
      );
  };

  const toggleSort = () => {
    setSortAsc(!sortAsc);
  };

  const totalPages = Math.ceil(filteredList.length / perPage);
  const currentMovies = useMemo(() => {
    const start = (page - 1) * perPage;
    return filteredList.slice(start, start + perPage);
  }, [filteredList, page]);

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      
      {/* ⚠️ GIẢ ĐỊNH NAV BAR CÓ CHIỀU CAO h-16 (khoảng 4rem) */}

      {/* CỘT 1: THANH THỂ LOẠI CỐ ĐỊNH BÊN TRÁI */}
      {/* ĐIỀU CHỈNH: fixed top-0 -> fixed top-16 */}
      <div className="w-64 flex-shrink-0 px-4 border-r border-gray-200 dark:border-gray-700 fixed top-16 left-0 h-full overflow-y-auto pb-6">
        <h3 className="text-xl font-semibold mb-3 text-blue-600 mt-2">Thể loại</h3>
        <div className="space-y-0.5"> 
            {/* Nút All/Tất cả */}
            <button
                onClick={() => handleFilterByGenre(null)}
                className={`w-full text-left py-1 px-3 rounded-lg transition flex justify-between items-center ${
                    selectedGenre === null
                        ? 'bg-blue-600 text-white font-bold'
                        : 'hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
            >
                <span>Tất cả</span> 
                <span className={`text-sm font-semibold ${
                    selectedGenre === null
                        ? 'bg-blue-800 text-white px-2 rounded-full'
                        : 'bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-300 px-2 rounded-full'
                }`}>
                    {movies.length}
                </span>
            </button>
            
            {/* Danh sách các thể loại */}
            {[...new Set(GENRES)].map((genre) => (
                <button
                    key={genre}
                    onClick={() => handleFilterByGenre(genre)}
                    className={`w-full text-left py-1 px-3 rounded-lg transition flex justify-between items-center ${
                        selectedGenre === genre
                            ? 'bg-blue-600 text-white font-bold'
                            : 'hover:bg-gray-200 dark:hover:bg-gray-700'
                    }`}
                >
                    <span>{genre}</span>
                    <span className={`text-sm font-semibold ${
                        selectedGenre === genre
                            ? 'bg-blue-800 text-white px-2 rounded-full'
                            : 'bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-300 px-2 rounded-full'
                    }`}>
                        {genreCounts[genre] || 0}
                    </span>
                </button>
            ))}
        </div>
      </div>


      {/* CỘT 2: NỘI DUNG CHÍNH (Header, Search, List) */}
      <div className="flex-1 ml-64 px-4 py-4">
        
        {/* HEADER VÀ THANH TÌM KIẾM - Cố định ở trên */}
        {/* ĐIỀU CHỈNH: fixed top-0 -> fixed top-16 */}
        {/* ĐIỀU CHỈNH: left-64 -> left-64 (Sidebar width) */}
        <div className="fixed top-16 left-64 right-0 bg-gray-50 dark:bg-gray-900 z-10 px-4 py-2 border-b border-gray-200 dark:border-gray-700">
            {/* ROW 1: Tiêu đề và tổng số phim */}
            <div className="flex flex-wrap items-center justify-between gap-2 mb-1"> 
              <h1 className="text-2xl font-bold text-blue-600 flex items-center gap-1"> 
                <Film className="w-6 h-6" /> Danh sách phim ({filteredList.length})
              </h1>
            </div>
            
            {/* ROW 2: Thanh tìm kiếm và Sắp xếp */}
            <div className="flex flex-wrap items-center justify-between gap-2"> 
              <div className="flex items-center gap-2">
                {/* Thanh tìm kiếm */}
                <div className="flex items-center border rounded-lg px-3 py-0.5 bg-white dark:bg-gray-800">
                  <Search className="w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Tìm kiếm theo tên, đạo diễn, thể loại..."
                    value={query}
                    onChange={handleSearch}
                    className="bg-transparent outline-none px-2 text-base w-64"
                  />
                </div>

                {/* Nút Sắp xếp */}
                <button
                  onClick={toggleSort}
                  className="flex items-center gap-1 px-3 py-1 text-base bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  title="Sắp xếp theo tên phim"
                >
                  {sortAsc ? <SortDesc size={16} /> : <SortAsc size={16} />}
                  Sắp xếp
                </button>
              </div>
            </div>
            
            {/* Hiển thị filter đang được áp dụng */}
            {selectedGenre && (
                <div className="mt-0.5 flex items-center gap-2 text-base"> 
                    <span className="text-gray-500 dark:text-gray-400">Đang lọc theo:</span>
                    <span className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300 px-3 py-1 rounded-full flex items-center gap-1 font-medium">
                        {selectedGenre}
                        <button onClick={() => setSelectedGenre(null)}>
                            <X className="w-4 h-4 ml-1 hover:text-blue-600" />
                        </button>
                    </span>
                </div>
            )}
        </div>

        {/* Danh sách phim - ĐIỀU CHỈNH PT LẠI */}
        {/* Khoảng cách cần thiết = (Chiều cao Navbar 4rem) + (Chiều cao Header hiện tại ~ 4.8rem) = ~ 8.8rem */}
        {/* Sử dụng pt-[9rem] (144px) để đảm bảo an toàn */}
        <div className="pt-[9rem]"> 
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"> 
            {currentMovies.length > 0 ? (
              currentMovies.map((movie) => (
                <div
                  key={movie.id}
                  onClick={() => setSelectedMovie(movie)}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer"
                >
                  <div className="flex items-center justify-center bg-gray-50 dark:bg-gray-900" style={{ minHeight: "10rem" }}>
                    <img
                      src={ movie.poster ? BaseURL + movie.poster : BaseURL + "posters/default_poster.jpg" }
                      alt={movie.original_title}
                      className="rounded-md object-contain"
                      style={{ width: "auto", height: "auto", maxWidth: "100%", maxHeight: "30vh" }}
                      onError={(e) => { e.target.onerror = null; e.target.src = BaseURL + "posters/default_poster.jpg"; }}
                    />
                  </div>
                  <div className="p-3"> 
                    <h2 className="font-semibold text-lg text-blue-600 truncate">
                      {movie.original_title}
                    </h2>
                    <p className="text-sm">🎬 <b>Ngày khởi chiếu:</b> {movie.release_date}</p> 
                    <p className="text-sm truncate">
                      🎬 <b>Đạo diễn:</b> {movie.director || "—"}
                    </p>
                    <p className="text-sm truncate">🎬 <b>Thể loại:</b> {movie.genres_vn}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 italic col-span-full text-center text-base">
                Không có phim nào được tìm thấy.
              </p>
            )}
          </div>
          
          {/* PHẦN PHÂN TRANG */}
          {filteredList.length > perPage && (
            <div className="flex items-center justify-center gap-4 mt-6 py-3">
              <button
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
                className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-40 transition"
              >
                <ChevronLeft />
              </button>

              <span className="text-base">
                Trang <b>{page}</b> / {totalPages}
              </span>

              <button
                disabled={page === totalPages}
                onClick={() => setPage(page + 1)}
                className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-40 transition"
              >
                <ChevronRight />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Single modal rendered once */}
      {selectedMovie && (
        <MoviesModals movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
      )}
    </div>
  );
}