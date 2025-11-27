import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Film, Search, Info, Database, PlayCircle, TrendingUp, Users, Sparkles } from "lucide-react";
import { PieChart, Pie, Tooltip, ResponsiveContainer, Cell, Legend } from "recharts";
import { useEffect, useState } from "react";
import { getPosterUrl, API_ENDPOINTS } from "../config/api";

export default function Home() {
  const [stats, setStats] = useState({
    total_movies: 0,
    directors: 0,
    genres_vn: [],
    top_stars: [],
  });

  const [genreData, setGenreData] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(API_ENDPOINTS.stats);
        if (!res.ok) throw new Error("API not found");
        const data = await res.json();

        setStats({
          total_movies: data.total_movies ?? 0,
          directors: data.directors ?? 0,
          top_stars: Array.isArray(data.top_stars) ? data.top_stars.slice(0, 5) : [],
        });

        const genres = Array.isArray(data.top_genres_vn)
          ? data.top_genres_vn.map(g => ({ name: g.name, value: g.value }))
          : [];

        setGenreData(genres.length > 0 ? genres : fallbackGenreData);
      } catch (err) {
        console.error("Failed to load stats:", err);
        setGenreData(fallbackGenreData);
      }
    };

    fetchStats();
  }, []);

  const fallbackGenreData = [
    { name: "Hài", value: 28 },
    { name: "Tình cảm", value: 22 },
    { name: "Hành động", value: 18 },
    { name: "Kinh dị", value: 15 },
    { name: "Tâm lý", value: 17 },
  ];

  const COLORS = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"];

  const featuredMovies = [
    { title: "Bố Già", img: getPosterUrl("posters/bo_gia.jpg"), desc: "Gia đình là nơi tình yêu không bao giờ phai.", year: "2021", rating: 9.2 },
    { title: "Trạng Quỳnh", img: getPosterUrl("posters/trang_quynh.jpg"), desc: "Thông minh, hài hước và đầy bất ngờ.", year: "2019", rating: 8.7 },
    { title: "Biệt Đội Rất Ổn", img: getPosterUrl("posters/biet_doi_rat_on.jpg"), desc: "Khi những kẻ lập dị trở thành anh hùng.", year: "2023", rating: 8.9 },
  ];

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.2 } }
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.8, ease: "easeOut" } }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-gray-900 dark:to-indigo-950 text-gray-900 dark:text-gray-100 overflow-x-hidden">
      {/* Hero Section - Nâng cấp cực mạnh */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={getPosterUrl("hero_bg.jpg")}
            alt="Cinema"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="relative z-10 text-center px-6 max-w-5xl mx-auto"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="inline-flex items-center gap-3 mb-6 px-6 py-3 bg-blue-600/20 backdrop-blur-md border border-blue-400/30 rounded-full"
          >
            <Sparkles className="w-5 h-5 text-blue-400" />
            <span className="text-blue-300 font-medium">Trợ lý AI phim Việt thông minh nhất 2025</span>
          </motion.div>

          <h1 className="text-5xl md:text-7xl font-black mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-200 to-blue-400 drop-shadow-2xl">
            Khám Phá Phim Việt <br /> Cùng AI Siêu Thông Minh
          </h1>

          <p className="text-xl md:text-2xl text-gray-200 mb-10 max-w-3xl mx-auto font-light leading-relaxed">
            Tìm kiếm diễn viên, hỏi nội dung phim, phân tích nhân vật — tất cả chỉ trong tích tắc với công nghệ AI hiện đại nhất.
          </p>

          <div className="flex flex-col sm:flex-row gap-5 justify-center items-center">
            <Link
              to="/search"
              className="group flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-lg font-bold rounded-2xl shadow-2xl transform hover:scale-105 transition-all duration-300"
            >
              <Search className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
              Bắt Đầu Tìm Kiếm Ngay
              <PlayCircle className="w-6 h-6 ml-2 opacity-80" />
            </Link>

            <Link
              to="/chat"
              className="px-8 py-5 bg-white/10 backdrop-blur-md border-2 border-white/30 hover:bg-white/20 text-white font-semibold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration w-300"
            >
              Trò chuyện với AI Phim
            </Link>
          </div>

          <div className="mt-12 flex gap-8 justify-center text-gray-300">
            <div className="text-center">
              <TrendingUp className="w-8 h-8 mx-auto mb-2 text-green-400" />
              <p className="text-3xl font-bold">{stats.total_movies}+</p>
              <p className="text-sm">Phim trong hệ thống</p>
            </div>
            <div className="text-center">
              <Users className="w-8 h-8 mx-auto mb-2 text-yellow-400" />
              <p className="text-3xl font-bold">{stats.directors}+</p>
              <p className="text-sm">Đạo diễn nổi bật</p>
            </div>
          </div>
        </motion.div>

        {/* Wave decoration */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" className="w-full h-32 text-white dark:text-gray-900">
            <path fill="currentColor" d="M0,0 C320,100 1120,20 1440,0 L1440,120 L0,120 Z" />
          </svg>
        </div>
      </section>

      {/* Featured Movies - Grid đẹp hơn */}
      <section className="py-20 px-6 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Phim Nổi Bật Nhất
            </h2>
            <p className="mt-4 text-gray-600 dark:text-gray-400 text-lg">Những tác phẩm được yêu thích nhất mọi thời đại</p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-3 gap-10"
          >
            {featuredMovies.map((movie, i) => (
              <motion.div
                key={i}
                variants={itemVariants}
                whileHover={{ y: -12, scale: 1.03 }}
                className="group relative bg-white dark:bg-gray-800 rounded-3xl shadow-xl overflow-hidden cursor-pointer border border-gray-200 dark:border-gray-700"
              >
                <div className="aspect-w-3 aspect-h-4 overflow-hidden">
                  <img
                    src={movie.img}
                    alt={movie.title}
                    className="w-full h-96 object-cover group-hover:scale-110 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                </div>

                <div className="absolute bottom-0 left-0 right-0 p-6 text-white transform translate-y-8 group-hover:translate-y-0 transition-transform duration-500">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-yellow-400 text-2xl font-bold">{movie.rating}</span>
                    <span className="text-sm opacity-80">/10</span>
                  </div>
                  <h3 className="text-2xl font-bold mb-2">{movie.title}</h3>
                  <p className="text-gray-200 text-sm leading-relaxed">{movie.desc}</p>
                  <span className="inline-block mt-3 px-4 py-1 bg-white/20 backdrop-blur rounded-full text-xs">
                    {movie.year}
                  </span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Stats + Chart - Đẹp và trực quan hơn */}
      <section className="py-24 px-6 bg-gradient-to-r from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-6xl mx-auto">
          <motion.h2
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
          >
            Bộ Sưu Tập Phim Việt Lớn Nhất
          </motion.h2>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="space-y-8"
            >
              {[
                { icon: Film, label: "Tổng số phim", value: stats.total_movies, color: "blue" },
                { icon: Users, label: "Đạo diễn nổi bật", value: stats.directors, color: "green" },
                { icon: Sparkles, label: "Diễn viên hàng đầu", value: stats.top_stars.length, color: "purple" },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-6 p-6 bg-white/70 dark:bg-gray-800/70 backdrop-blur rounded-2xl shadow-lg">
                  <div className={`p-4 rounded-2xl bg-gradient-to-br from-${item.color}-500 to-${item.color}-600 text-white`}>
                    <item.icon className="w-8 h-8" />
                  </div>
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">{item.label}</p>
                    <p className="text-3xl font-bold">{item.value > 0 ? item.value : "..."}</p>
                  </div>
                </div>
              ))}

              <div className="p-6 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl text-white">
                <p className="text-lg font-semibold mb-2">Diễn viên được yêu thích nhất</p>
                <p className="text-2xl">
                  {stats.top_stars.length > 0 ? stats.top_stars.join(" • ") : "Đang tải..."}
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8"
            >
              <h3 className="text-2xl font-bold text-center mb-8">Phân bố thể loại phim</h3>
              <ResponsiveContainer width="100%" height={380}>
                <PieChart>
                  <Pie
                    data={genreData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    innerRadius={60}
                    label={({ name, value }) => `${name}: ${value}`}
                    labelStyle={{ fontWeight: "bold", fill: "#fff" }}
                  >
                    {genreData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value} phim`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-24 px-6 text-center bg-gradient-to-t from-blue-600 to-indigo-700 text-white">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          <h2 className="text-4xl md:text-6xl font-black mb-6">
            Sẵn sàng khám phá thế giới phim Việt?
          </h2>
          <p className="text-xl mb-10 opacity-90">
            Hàng ngàn bộ phim, hàng triệu câu chuyện đang chờ bạn khám phá.
          </p>
          <Link
            to="/search"
            className="inline-flex items-center gap-4 px-12 py-6 bg-white text-blue-600 font-bold text-xl rounded-full shadow-2xl hover:shadow-3xl transform hover:scale-110 transition-all duration-300"
          >
            <Film className="w-8 h-8" />
            Bắt Đầu Ngay Hôm Nay
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-10 text-center text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-800">
        <p>© 2025 Film Character Search • Được xây dựng với ❤️ và AI</p>
      </footer>
    </div>
  );
}