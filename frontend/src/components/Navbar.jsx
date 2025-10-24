import { useState } from "react";
import { Film, Search, Info, Database, Sun, Moon, Home  } from "lucide-react";
import { Link } from "react-router-dom"; // nếu bạn đang dùng react-router

function Navbar() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    document.documentElement.classList.toggle("dark", newMode);
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

        {/* Menu items */}
        <ul className="hidden md:flex space-x-6 text-gray-700 dark:text-gray-300 font-medium">
          <li className="hover:text-blue-600 dark:hover:text-blue-400 transition cursor-pointer flex items-center gap-1">
            <Home size={18} />
            <Link to="/">Trang Chủ</Link>
          </li>
          <li className="hover:text-blue-600 dark:hover:text-blue-400 transition cursor-pointer flex items-center gap-1">
            <Search size={18} />
            <Link to="/search">Tìm Kiếm</Link>
          </li>
          <li className="hover:text-blue-600 dark:hover:text-blue-400 transition cursor-pointer flex items-center gap-1">
            <Film size={18} />
            <Link to="/movies" >Danh sách phim</Link>

          </li>
          <li className="hover:text-blue-600 dark:hover:text-blue-400 transition cursor-pointer flex items-center gap-1">
            <Info size={18} />
            <Link to="/about">Giới Thiệu</Link>
          </li>
        </ul>

        {/* Dark mode toggle */}
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
          title="Chuyển chế độ sáng/tối"
        >
          {darkMode ? (
            <Sun size={22} className="text-yellow-400" />
          ) : (
            <Moon size={22} className="text-gray-600 dark:text-gray-300" />
          )}
        </button>
      </div>
    </nav>
  );
}

export default Navbar;

