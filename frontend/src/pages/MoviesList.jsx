// src/pages/MoviesList.jsx
import { useEffect, useState, useMemo } from "react";
import { 
  Search, 
  Filter, 
  X, 
  SortAsc, 
  SortDesc, 
  ChevronLeft, 
  ChevronRight,
  Film,
  Calendar,
  Clapperboard
} from "lucide-react";
import { API_ENDPOINTS } from "../config/api";
import MoviesModal from "../components/MoviesModal";

const GENRES = [
  "Hành Động", "Lãng Mạn", "Chính Kịch", "Hài",  "Kinh Dị",
   "Khoa Học Viễn Tưởng", "Gia Đình",  "Chiến Tranh",
   "Âm Nhạc", "Phiêu Lưu"
];

const BaseURL = "http://localhost:8000/static/";

// HÀM HỖ TRỢ: chuyển genres_vn thành mảng chuẩn (dù là string hay array)
const normalizeGenres = (genres) => {
  if (!genres) return [];
  if (Array.isArray(genres)) return genres.map(g => g.trim());
  if (typeof genres === "string") {
    return genres.split(",").map(g => g.trim()).filter(g => g);
  }
  return [];
};

export default function MoviesList() {
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [movies, setMovies] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("Tất cả");
  const [page, setPage] = useState(1);
  const [sortAsc, setSortAsc] = useState(true);
  const [loading, setLoading] = useState(true);

  const perPage = 10;

  // Đảm bảo genres_vn luôn là mảng → dùng để đếm và lọc
  const processedMovies = useMemo(() => {
    return movies.map(movie => ({
      ...movie,
      _genresArray: normalizeGenres(movie.genres_vn)
    }));
  }, [movies]);

  // Đếm số lượng phim theo thể loại
  const genreCounts = useMemo(() => {
    const counts = { "Tất cả": processedMovies.length };
    GENRES.forEach(g => {
      counts[g] = processedMovies.filter(m => m._genresArray.includes(g)).length;
    });
    return counts;
  }, [processedMovies]);

  // Fetch phim
  useEffect(() => {
    const fetchMovies = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_ENDPOINTS.movies}?per_page=100`);
        const data = await res.json();
        const list = Array.isArray(data) ? data : data.movies || [];
        setMovies(list);
      } catch (err) {
        console.error("Load phim lỗi:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMovies();
  }, []);

  // Lọc + tìm kiếm + sắp xếp
  const filteredList = useMemo(() => {
    let list = [...processedMovies];

    // Lọc thể loại
    if (selectedGenre && selectedGenre !== "Tất cả") {
      list = list.filter(m => m._genresArray.includes(selectedGenre));
    }

    // Tìm kiếm
    if (query.trim()) {
      const q = query.toLowerCase();
      list = list.filter(m => {
        const searchText = [
          m.original_title,
          m.title,
          m.director,
          m.stars,
          m.description,
          m._genresArray.join(" ")
        ].join(" ").toLowerCase();
        return searchText.includes(q);
      });
    }

    // Sắp xếp
    list.sort((a, b) => 
      sortAsc 
        ? a.original_title.localeCompare(b.original_title)
        : b.original_title.localeCompare(a.original_title)
    );

    return list;
  }, [processedMovies, selectedGenre, query, sortAsc]);

  const totalPages = Math.ceil(filteredList.length / perPage);
  const currentMovies = filteredList.slice((page - 1) * perPage, page * perPage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-purple-950 to-pink-950 text-white">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-80 bg-black/40 backdrop-blur-2xl border-r border-white/10 z-50 overflow-y-auto pt-24 pb-32">
        <div className="p-8">
          <div className="flex items-center gap-4 mb-10">
            <div className="p-4 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl shadow-2xl">
              <Filter className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Bộ lọc thể loại
            </h2>
          </div>

          <div className="space-y-3">
            {["Tất cả", ...GENRES].map((genre) => (
              <button
                key={genre}
                onClick={() => setSelectedGenre(genre)}
                className={`w-full flex items-center justify-between px-6 py-5 rounded-2xl font-bold text-lg transition-all duration-300 shadow-lg ${
                  selectedGenre === genre
                    ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-purple-500/50 scale-105"
                    : "bg-white/10 hover:bg-white/20 text-gray-300 backdrop-blur-md"
                }`}
              >
                <span>{genre}</span>
                <span className="px-4 py-2 bg-white/20 rounded-full text-sm">
                  {genreCounts[genre] || 0}
                </span>
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="ml-80 min-h-screen">
        <header className="fixed top-0 left-80 right-0 bg-black/60 backdrop-blur-3xl z-40 border-b border-white/10">
          <div className="px-10 py-8">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-5xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 bg-clip-text text-transparent">
                  Kho Phim Việt Nam
                </h1>
                <p className="text-xl text-gray-300 mt-3">
                  {filteredList.length} bộ phim • Trang {page} / {totalPages}
                </p>
              </div>
              <button
                onClick={() => setSortAsc(!sortAsc)}
                className="flex items-center gap-4 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl font-bold text-white shadow-2xl hover:scale-105 transition-all"
              >
                {sortAsc ? <SortAsc className="w-6 h-6" /> : <SortDesc className="w-6 h-6" />}
                {sortAsc ? "A → Z" : "Z → A"}
              </button>
            </div>

            <div className="flex items-center gap-6">
              <div className="relative flex-1 max-w-2xl">
                <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400" />
                <input
                  type="text"
                  placeholder="Tìm tên phim, đạo diễn, diễn viên..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full pl-16 pr-12 py-5 bg-white/10 backdrop-blur-xl border border-white/20 rounded-full text-white placeholder-gray-400 text-lg focus:outline-none focus:ring-4 focus:ring-purple-500/50"
                />
                {query && (
                  <button onClick={() => setQuery("")} className="absolute right-5 top-1/2 -translate-y-1/2">
                    <X className="w-6 h-6 text-gray-400 hover:text-white" />
                  </button>
                )}
              </div>

              {selectedGenre && selectedGenre !== "Tất cả" && (
                <div className="flex items-center gap-4 px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full font-bold shadow-xl">
                  <Clapperboard className="w-6 h-6" />
                  {selectedGenre}
                  <button onClick={() => setSelectedGenre("Tất cả")}>
                    <X className="w-6 h-6" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Grid phim */}
        <div className="pt-48 px-10 pb-32">
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5 gap-8">
              {[...Array(20)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="aspect-[2/3] bg-white/10 rounded-3xl" />
                  <div className="mt-4 h-6 bg-white/10 rounded-full" />
                </div>
              ))}
            </div>
          ) : currentMovies.length === 0 ? (
            <div className="text-center py-32">
              <Film className="w-32 h-32 mx-auto text-gray-600 mb-8" />
              <h3 className="text-4xl font-bold text-gray-400">Không tìm thấy phim nào</h3>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5 gap-8">
                {currentMovies.map((movie) => (
                  <div
                    key={movie.id}
                    onClick={() => setSelectedMovie(movie)}
                    className="group relative rounded-3xl overflow-hidden shadow-2xl cursor-pointer transform transition-all duration-500 hover:scale-105 hover:-translate-y-4"
                  >
                    <div className="aspect-[2/3]">
                      <img
                        src={movie.poster ? `${BaseURL}${movie.poster}` : `${BaseURL}posters/default_poster.jpg`}
                        alt={movie.original_title}
                        className="w-full h-full object-cover"
                        onError={(e) => { e.target.src = `${BaseURL}posters/default_poster.jpg`; }}
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                      <div className="absolute bottom-0 left-0 right-0 p-6 translate-y-16 group-hover:translate-y-0 transition-transform duration-500">
                        <h3 className="font-black text-xl line-clamp-2 text-white drop-shadow-2xl">
                          {movie.original_title}
                        </h3>
                        <div className="flex items-center gap-3 mt-2 text-sm opacity-90">
                          <Calendar className="w-4 h-4" />
                          <span>{movie.release_date || "Chưa rõ"}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center gap-4 mt-20">
                  <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                    className="p-4 rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-50">
                    <ChevronLeft className="w-7 h-7" />
                  </button>
                  <div className="flex gap-3">
                    {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
                      const num = totalPages <= 7 ? i + 1 : page <= 4 ? i + 1 : page >= totalPages - 3 ? totalPages - 6 + i : page - 3 + i;
                      if (num > totalPages) return null;
                      return (
                        <button key={num} onClick={() => setPage(num)}
                          className={`w-14 h-14 rounded-full font-black text-lg ${page === num ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white scale-110" : "bg-white/10 hover:bg-white/20"}`}>
                          {num}
                        </button>
                      );
                    })}
                  </div>
                  <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                    className="p-4 rounded-full bg-white/10 hover:bg-white/20 disabled:opacity-50">
                    <ChevronRight className="w-7 h-7" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {selectedMovie && <MoviesModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />}
    </div>
  );
}