// src/components/Navbar.jsx
import { useState, useEffect } from "react";
import { 
  Film, 
  Search, 
  Home, 
  Shield, 
  Info, 
  Menu, 
  X, 
  Sun, 
  Moon, 
  User, 
  LogOut,
  Crown
} from "lucide-react";
import { Link, useNavigate, useLocation } from "react-router-dom";

export default function Navbar() {
  const [darkMode, setDarkMode] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Kiểm tra trạng thái đăng nhập
  const userToken = localStorage.getItem("user_token");
  const adminToken = localStorage.getItem("admin_token");
  const username = localStorage.getItem("user_username") || localStorage.getItem("admin_username") || "Guest";
  const isLoggedIn = !!userToken || !!adminToken;
  const isAdmin = !!adminToken;

  // Dark mode tự động + lưu cài đặt
  useEffect(() => {
    const saved = localStorage.getItem("darkMode");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = saved !== null ? saved === "true" : prefersDark;
    
    setDarkMode(initial);
    document.documentElement.classList.toggle("dark", initial);
  }, []);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    document.documentElement.classList.toggle("dark", newMode);
    localStorage.setItem("darkMode", String(newMode));
  };

  const handleLogout = () => {
    localStorage.clear(); // Xóa hết token, username, darkMode vẫn giữ
    localStorage.setItem("darkMode", String(darkMode)); // giữ dark mode
    navigate("/login");
    window.location.reload();
  };

  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Navbar chính - Fixed */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-2xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">

          {/* Logo + Brand */}
          <Link to="/" className="flex items-center gap-4 group">
            <div className="p-3 bg-gradient-to-br from-red-600 via-purple-600 to-pink-600 rounded-2xl shadow-2xl group-hover:scale-110 transition-all duration-300">
              <Film className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-red-500 via-purple-500 to-pink-500 bg-clip-text text-transparent tracking-tight">
              MovieFinder
            </h1>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center gap-1">
            <Link
              to="/"
              className={`flex items-center gap-3 px-6 py-3 rounded-2xl font-bold transition-all duration-300 ${
                isActive("/") 
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-xl shadow-purple-500/30" 
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              <Home className="w-5 h-5" />
              Trang chủ
            </Link>

            <Link
              to="/movies"
              className={`flex items-center gap-3 px-6 py-3 rounded-2xl font-bold transition-all duration-300 ${
                isActive("/movies")
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-xl"
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              <Film className="w-5 h-5" />
              Phim
            </Link>

            <Link
              to="/search"
              className={`flex items-center gap-3 px-6 py-3 rounded-2xl font-bold transition-all duration-300 ${
                isActive("/search")
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-xl"
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              <Search className="w-5 h-5" />
              Tìm kiếm
            </Link>

            <Link
              to="/about"
              className={`flex items-center gap-3 px-6 py-3 rounded-2xl font-bold transition-all duration-300 ${
                isActive("/about")
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-xl"
                  : "text-gray-300 hover:bg-white/10 hover:text-white"
              }`}
            >
              <Info className="w-5 h-5" />
              Giới thiệu
            </Link>

            {/* Nút QUẢN TRỊ - CHỈ HIỆN CHO ADMIN */}
            {isAdmin && (
              <Link
                to="/admin"
                className="flex items-center gap-3 px-7 py-3 rounded-2xl bg-gradient-to-r from-red-600 via-orange-600 to-pink-600 text-white font-black shadow-2xl shadow-red-600/50 hover:shadow-red-600/70 hover:scale-105 transition-all duration-300 ml-4"
              >
                <Crown className="w-6 h-6" />
                QUẢN TRỊ
              </Link>
            )}
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-5">

            {/* Dark Mode */}
            <button
              onClick={toggleDarkMode}
              className="p-3 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-md transition-all hover:scale-110"
            >
              {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-gray-400" />}
            </button>

            {/* User Section */}
            {isLoggedIn ? (
              <div className="flex items-center gap-4">
                {/* Avatar + Info */}
                <div className="flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-purple-600/20 to-pink-600/20 rounded-2xl border border-purple-500/30">
                  <div className="relative">
                    <div className="w-11 h-11 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-black text-xl shadow-lg">
                      {username.charAt(0).toUpperCase()}
                    </div>
                    {isAdmin && (
                      <Crown className="absolute -top-2 -right-2 w-6 h-6 text-yellow-400 drop-shadow-lg" />
                    )}
                  </div>
                  <div className="hidden sm:block">
                    <p className="text-white font-bold">{username}</p>
                    <p className="text-xs text-gray-300">{isAdmin ? "Quản trị viên" : "Thành viên"}</p>
                  </div>
                </div>

                {/* Logout */}
                <button
                  onClick={handleLogout}
                  className="p-3 bg-red-600/20 hover:bg-red-600/40 rounded-xl transition-all hover:scale-110"
                  title="Đăng xuất"
                >
                  <LogOut className="w-5 h-5 text-red-400" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  to="/login"
                  className="px-7 py-3 font-bold text-white hover:bg-white/10 rounded-2xl transition-all hover:scale-105"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="px-7 py-3 font-black text-white bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl shadow-xl hover:shadow-pink-500/50 hover:scale-105 transition-all"
                >
                  Đăng ký
                </Link>
              </div>
            )}

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-3 rounded-xl bg-white/10 hover:bg-white/20 transition"
            >
              {mobileMenuOpen ? <X className="w-6 h-6 text-white" /> : <Menu className="w-6 h-6 text-white" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden absolute top-full left-0 right-0 bg-black/95 backdrop-blur-2xl border-t border-white/10 shadow-2xl">
            <div className="px-6 py-8 space-y-3">
              <Link to="/" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-4 px-6 py-4 rounded-2xl hover:bg-white/10 text-white font-bold text-lg">
                <Home className="w-6 h-6" /> Trang chủ
              </Link>
              <Link to="/movies" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-4 px-6 py-4 rounded-2xl hover:bg-white/10 text-white font-bold text-lg">
                <Film className="w-6 h-6" /> Phim
              </Link>
              <Link to="/search" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-4 px-6 py-4 rounded-2xl hover:bg-white/10 text-white font-bold text-lg">
                <Search className="w-6 h-6" /> Tìm kiếm
              </Link>
              {isAdmin && (
                <Link to="/admin" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-4 px-6 py-4 rounded-2xl bg-gradient-to-r from-red-600 to-pink-600 text-white font-black text-lg shadow-lg">
                  <Crown className="w-6 h-6" /> QUẢN TRỊ HỆ THỐNG
                </Link>
              )}
              <Link to="/about" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-4 px-6 py-4 rounded-2xl hover:bg-white/10 text-white font-bold text-lg">
                <Info className="w-6 h-6" /> Giới thiệu
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Spacer */}
      <div className="h-24" />
    </>
  );
}