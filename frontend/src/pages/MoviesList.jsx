import { useEffect, useState, useMemo } from "react";
import { Search, Film, ChevronLeft, ChevronRight, SortAsc, SortDesc } from "lucide-react";
import { API_ENDPOINTS } from "../config/api";
import MovieModal from "../components/MoviesModal";



export default function MoviesList() {
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [movies, setMovies] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [sortAsc, setSortAsc] = useState(true);
  const perPage = 8;

  useEffect(() => {
    fetchMovies();
  }, []);

  const fetchMovies = async () => {
    try {
      const res = await fetch(API_ENDPOINTS.movies);
      const data = await res.json();
      setMovies(data.movies || []);
      setFiltered(data.movies || []);
    } catch (err) {
      console.error("Failed to load movies:", err);
    }
  };

  // Tìm kiếm phim
  const handleSearch = (e) => {
    const q = e.target.value.toLowerCase();
    setQuery(q);
    const filteredList = movies.filter(
      (m) =>
        m.title.toLowerCase().includes(q) ||
        m.director.toLowerCase().includes(q) ||
        m.genres.toLowerCase().includes(q)
    );
    setFiltered(filteredList);
    setPage(1);
  };

  //  Sắp xếp theo tên phim
  const toggleSort = () => {
    const sorted = [...filtered].sort((a, b) =>
      sortAsc ? b.title.localeCompare(a.title) : a.title.localeCompare(b.title)
    );
    setFiltered(sorted);
    setSortAsc(!sortAsc);
  };

  //  Tính dữ liệu cho trang hiện tại
  const totalPages = Math.ceil(filtered.length / perPage);
  const currentMovies = useMemo(() => {
    const start = (page - 1) * perPage;
    return filtered.slice(start, start + perPage);
  }, [filtered, page]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between mb-6 gap-3">
        <h1 className="text-3xl font-bold text-blue-600 flex items-center gap-2">
          <Film className="w-8 h-8" /> Danh sách phim trong CSDL
        </h1>
        <div className="flex items-center gap-2">
          <div className="flex items-center border rounded-lg px-3 py-1 bg-white dark:bg-gray-800">
            <Search className="w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Tìm kiếm theo tên, đạo diễn, thể loại..."
              value={query}
              onChange={handleSearch}
              className="bg-transparent outline-none px-2 text-sm w-64"
            />
          </div>

          <button
            onClick={toggleSort}
            className="flex items-center gap-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            title="Sắp xếp theo tên phim"
          >
            {sortAsc ? <SortAsc size={16} /> : <SortDesc size={16} />}
            Sắp xếp
          </button>
        </div>
      </div>

      {/* Danh sách phim */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {currentMovies.length > 0 ? (
          currentMovies.map((movie) => (
            <div
              key={movie.id}
              onClick={() => setSelectedMovie(movie)}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300"
            >
              <img
                src={movie.poster ? movie.poster : "http://localhost:8000/static/posters/default_poster.jpg"}
                alt={movie.title}
                
                className="w-full h-64 object-cover"
                onError={(e) => (e.target.src = "http://localhost:8000/static/posters/default_poster.jpg")}
              />
              <div className="p-4">
                <h2 className="font-semibold text-lg text-blue-600 truncate">
                  {movie.title}
                </h2>
                <p className="text-sm text-gray-500 mb-1">{movie.release_date}</p>
                <p className="text-sm">
                  🎬 <b>Đạo diễn:</b> {movie.director || "—"}
                </p>
                <p className="text-xs italic text-gray-500">{movie.genres}</p>
                <p className="text-sm mt-2 text-gray-700 dark:text-gray-300">
                  {movie.overview}
                </p>
              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-500 italic col-span-full text-center">
            Không có phim nào được tìm thấy.
          </p>
        )}
      </div>

      {/* Single modal rendered once */}
      {selectedMovie && (
        <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
      )}

      {/* Pagination */}
      {filtered.length > perPage && (
        <div className="flex items-center justify-center gap-4 mt-8">
          <button
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
            className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-40"
          >
            <ChevronLeft />
          </button>

          <span className="text-sm">
            Trang <b>{page}</b> / {totalPages}
          </span>

          <button
            disabled={page === totalPages}
            onClick={() => setPage(page + 1)}
            className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-40"
          >
            <ChevronRight />
          </button>
        </div>
      )}
    </div>
  );
}
