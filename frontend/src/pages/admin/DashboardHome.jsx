// src/pages/admin/DashboardHome.jsx
import React, { useState, useEffect } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { 
  Users, 
  Film, 
  Settings, 
  LogOut, 
  Menu, 
  X, 
  BarChart3,
  Shield,
  Bell,
  Sun,
  Moon
} from "lucide-react";

export default function AdminDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();

  const adminName = localStorage.getItem("admin_username") || "Admin";

  // Dark mode tự động + lưu cài đặt
  useEffect(() => {
    const saved = localStorage.getItem("darkMode");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = saved ? saved === "true" : prefersDark;
    
    setDarkMode(initial);
    document.documentElement.classList.toggle("dark", initial);
  }, []);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    document.documentElement.classList.toggle("dark", newMode);
    localStorage.setItem("darkMode", newMode);
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_username");
    navigate("/login/admin");
  };

  // ← QUAN TRỌNG: chỉ "Tổng quan" mới có end: true
  const navItems = [
    { to: "/admin",         icon: BarChart3, label: "Tổng quan",         end: true },
    { to: "/admin/users",   icon: Users,     label: "Quản lý người dùng" },
    { to: "/admin/movies",  icon: Film,      label: "Quản lý phim" },
    { to: "/admin/settings",icon: Settings, label: "Cài đặt hệ thống" },
  ];

  const activeClass = "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-xl shadow-purple-500/20";
  const inactiveClass = "text-gray-400 hover:bg-gray-800 hover:text-white";

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-gray-100">
      {/* Top Navbar cố định */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-gray-900/95 backdrop-blur-xl border-b border-gray-800 shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-3 rounded-xl bg-gray-800 hover:bg-gray-700 transition-all hover:scale-110"
            >
              {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl">
                <Shield className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Admin Panel
                </h1>
                <p className="text-xs text-gray-500">MovieFinder Management System</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-5">
            <button className="relative p-3 rounded-xl bg-gray-800 hover:bg-gray-700 transition">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
            </button>

            <button
              onClick={toggleDarkMode}
              className="p-3 rounded-xl bg-gray-800 hover:bg-gray-700 transition-all hover:scale-110"
            >
              {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-gray-400" />}
            </button>

            <div className="flex items-center gap-4 px-4 py-2 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-2xl border border-blue-500/30">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center font-bold text-white shadow-lg">
                {adminName.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="font-semibold text-white">{adminName}</p>
                <p className="text-xs text-gray-400">Quản trị viên</p>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-5 py-3 bg-gradient-to-r from-red-600 to-pink-600 rounded-xl font-bold shadow-lg hover:shadow-red-500/50 hover:scale-105 transition-all"
            >
              <LogOut className="w-5 h-5" />
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      <div className="flex pt-20">
        {/* Sidebar có thể thu gọn */}
        <aside className={`fixed left-0 top-20 h-full bg-gray-900/95 backdrop-blur-xl border-r border-gray-800 transition-all duration-300 ${sidebarOpen ? "w-72" : "w-20"}`}>
          <nav className="p-4 space-y-3">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}   // ← Chỉ "Tổng quan" mới có end: true → fix lỗi nhảy về home
                className={({ isActive }) =>
                  `flex items-center gap-4 px-4 py-4 rounded-2xl transition-all duration-300 group relative ${
                    isActive ? activeClass : inactiveClass
                  }`
                }
              >
                <item.icon className="w-6 h-6 flex-shrink-0" />
                <span className={`font-medium transition-opacity ${sidebarOpen ? "opacity-100" : "opacity-0"}`}>
                  {item.label}
                </span>

                {/* Tooltip khi sidebar thu gọn */}
                {!sidebarOpen && (
                  <div className="absolute left-full ml-2 px-3 py-2 bg-gray-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 shadow-xl">
                    {item.label}
                  </div>
                )}
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? "ml-72" : "ml-20"}`}>
          <div className="p-8">
            <div className="mb-8">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Chào mừng trở lại, {adminName}!
              </h2>
              <p className="text-gray-400 mt-2">Quản lý hệ thống MovieFinder một cách dễ dàng</p>
            </div>

            <div className="bg-gray-900/50 backdrop-blur-sm rounded-3xl border border-gray-800 p-8 min-h-screen">
              <Outlet />
            </div>
          </div>
        </main>
      </div>

      {/* Overlay mobile khi sidebar mở */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}