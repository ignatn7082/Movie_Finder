import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Film, Search, Info, Database } from "lucide-react";
import { PieChart, Pie, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { useEffect, useState } from "react";
import { getPosterUrl, API_ENDPOINTS} from "../config/api";   

export default function Home() {
  const [stats, setStats] = useState({
    total_movies: 0,
    directors: 0,
    genres: [],
    top_stars: [],
  });

  // state riêng cho dữ liệu thể loại (dùng trong Pie)
  const [genreData, setGenreData] = useState(stats.genres);
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(API_ENDPOINTS.stats);
        if (!res.ok) throw new Error("API not found");
        const data = await res.json();

        // Kiểm tra kỹ data trước khi set
        if (data) {
          // cập nhật stats tổng quát nếu API trả về
          setStats(prev => ({
            ...prev,
            total_movies: data.total_movies ?? prev.total_movies,
            directors: data.directors ?? prev.directors,
            top_stars: Array.isArray(data.top_stars) ? data.top_stars : prev.top_stars,
          }));
          setGenreData(Array.isArray(data.top_genres) ? data.top_genres : []);
        } else {
          setGenreData([]);
        }
      } catch (err) {
        console.error("Failed to load movie tts:", err);
        //  Dữ liệu tạm khi API lỗi
        setGenreData([
          { name: "Comedy", value: 8 },
          { name: "Drama", value: 6 },
          { name: "Action", value: 5 },
          { name: "Romance", value: 3 },
        ]);
      }
    };

    fetchStats();
  }, []);
  
  const COLORS = ["#60A5FA", "#F87171", "#34D399", "#FBBF24", "#A78BFA"];

  const featuredMovies = [
    {
      title: "Bố Già",
      img: getPosterUrl("posters/Bo_Gia.jpg"), 
      desc: "Câu chuyện cảm động về tình cha con giữa cuộc sống hiện đại.",
    },
    {
      title: "Trạng Quỳnh",
      img: getPosterUrl("posters/Trang_Quynh.jpg"),
      desc: "Phiêu lưu, hài hước và thông minh của chàng Trạng nổi tiếng Việt Nam.",
    },
    {
      title: "The Ideal Squad",
      img: getPosterUrl("posters/Biet_Doi_Rat_On.jpg"),
      desc: "Bộ phim hài hành động về nhóm bạn lập dị và phi vụ bất đắc dĩ.",
    },
  ];


  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:to-gray-800 text-gray-800 dark:text-gray-100">
      {/* 🌟 Hero Section */}
      <div className="relative h-[75vh] flex flex-col items-center justify-center text-center overflow-hidden">
        <img
          src={getPosterUrl("hero_bg.jpg")}
          alt="Cinema background"
          className="absolute inset-0 w-full h-full object-cover opacity-30 dark:opacity-20"
        />
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="relative z-10"
        >
          <h1 className="text-5xl md:text-6xl font-extrabold mb-4 text-blue-700 dark:text-blue-400 flex items-center justify-center gap-3 drop-shadow-lg">
            <Film className="w-12 h-12" /> Film Character Search
          </h1>
          <p className="text-lg md:text-xl max-w-3xl mx-auto text-gray-700 dark:text-gray-300">
            Tìm kiếm, khám phá và trò chuyện về phim yêu thích của bạn với trợ lý AI thông minh 🎬  
          </p>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="mt-8 flex flex-wrap justify-center gap-5 relative z-10"
        >
          <Link
            to="/search"
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl shadow-lg transition-all"
          >
            <Search className="w-5 h-5" /> Tìm kiếm phim
          </Link>

          <Link
            to="/dataset"
            className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-xl shadow-lg transition-all"
          >
            <Database className="w-5 h-5" /> Bộ dữ liệu phim
          </Link>

          <Link
            to="/about"
            className="flex items-center gap-2 px-6 py-3 bg-gray-700 hover:bg-gray-800 text-white font-medium rounded-xl shadow-lg transition-all"
          >
            <Info className="w-5 h-5" /> Giới thiệu hệ thống
          </Link>
        </motion.div>
      </div>

      {/* 🎞️ Carousel “Phim nổi bật” */}
      <motion.section
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        viewport={{ once: true }}
        className="py-12 px-6 md:px-12 bg-white dark:bg-gray-900 shadow-inner"
      >
        <h2 className="text-2xl font-bold text-center mb-8 text-blue-600 dark:text-blue-400">
          🎬 Phim nổi bật
        </h2>

        <div className="flex gap-6 overflow-x-auto no-scrollbar justify-center pb-4">
          {featuredMovies.map((movie, i) => (
            <motion.div
              key={i}
              whileHover={{ scale: 1.05 }}
              className="min-w-[250px] bg-gray-100 dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all"
            >
              <img
                src={movie.img}
                alt={movie.title}
                className="w-full h-60 object-cover"
              />
              <div className="p-4 text-center">
                <h3 className="font-semibold text-lg mb-1">{movie.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{movie.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* 📊 Biểu đồ thống kê */}
      <motion.section
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        viewport={{ once: true }}
        className="py-16 bg-blue-50 dark:bg-gray-800 text-center"
      >
        <h2 className="text-2xl font-bold mb-8 text-blue-600 dark:text-blue-400">
          📊 Thống kê thể loại phim
        </h2>

        <div className="flex flex-col md:flex-row items-center justify-center gap-8">
          <div className="w-72 h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={genreData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={100}
                  label
                >
                  {(Array.isArray(genreData) ? genreData : []).map((entry, index) => (
                     <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                   ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="text-left max-w-sm">
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-2">
              🎞️ Tổng số phim: <b>{stats.total_movies}</b>
            </p>
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-2">
              🎬 Đạo diễn khác nhau: <b>{stats.directors}</b>
            </p>
            <p className="text-lg text-gray-700 dark:text-gray-300">
              🌟 Diễn viên nổi bật:{" "}
              <b>{stats.top_stars.length ? stats.top_stars.join(", ") : "Đang tải..."}</b>
            </p>
          </div>
        </div>
      </motion.section>

      {/* Footer */}
      <footer className="py-6 text-center text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700">
        © 2025 Film Character Search | Built with 💙 CLIP + Gemini AI
      </footer>
    </div>
  );
}
