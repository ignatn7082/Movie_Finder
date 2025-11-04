import { useState } from "react";
import { Film, Search, Info, Home, Shield, Sun, Moon } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();

  const userToken = localStorage.getItem("user_token");
  const adminToken = localStorage.getItem("admin_token");

  let role = "";
  let username = "";

  if (adminToken) {
    role = "admin";
    username = localStorage.getItem("admin_username");
  } else if (userToken) {
    role = "user";
    username = localStorage.getItem("user_username");
  }

  // Nếu chưa đăng nhập → return null
  if (!userToken && !adminToken) return null;

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    document.documentElement.classList.toggle("dark", newMode);
  };

  const handleLogout = (type) => {
    if (type === "admin") {
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_username");
    } else {
      localStorage.removeItem("user_token");
      localStorage.removeItem("user_username");
    }
    navigate("/login/user");
  };

  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-md border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <Film className="text-blue-600 dark:text-blue-400" size={28} />
          <h1 className="text-xl font-bold text-gray-800 dark:text-gray-200">
            MovieFinder
          </h1>
        </div>

        {/* Menu chính */}
        <ul className="hidden md:flex space-x-6 text-gray-700 dark:text-gray-300 font-medium">
          <li><Link to="/" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"><Home size={18}/>Trang Chủ</Link></li>
          <li><Link to="/search" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"><Search size={18}/>Tìm Kiếm</Link></li>
          <li><Link to="/movies" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"><Film size={18}/>Danh Sách Phim</Link></li>

          {/* Chỉ hiện khi có admin */}
          {adminToken && (
            <li>
              <Link to="/admin" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1">
                <Shield size={18}/>Quản Trị
              </Link>
            </li>
          )}
          <li><Link to="/about" className="hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"><Info size={18}/>Giới Thiệu</Link></li>
        </ul>

        {/* Khu vực bên phải */}
        <div className="flex items-center space-x-4">
          {/* Dark mode */}
          <button onClick={toggleDarkMode} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition">
            {darkMode ? <Sun size={22} className="text-yellow-400" /> : <Moon size={22} className="text-gray-600 dark:text-gray-300" />}
          </button>

          {/* Nếu có user/admin */}
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {role === "admin" ? "🛡️ Admin" : "👤 User"}: <b>{username}</b>
            </span>
            <button
              onClick={() => {
                localStorage.clear();
                navigate("/login/user");
              }}
              className="text-red-500 hover:underline text-sm"
            >
              Đăng xuất
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
