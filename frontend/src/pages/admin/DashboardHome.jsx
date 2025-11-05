// src/pages/admin/DashboardHome.jsx
import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { Users, Film, Settings, LogOut } from "lucide-react";

export default function AdminDashboard() {
  const linkClass = ({ isActive }) =>
    `flex items-center gap-2 px-4 py-2 rounded-md text-sm transition-all duration-200 ${
      isActive
        ? "bg-blue-600 text-white"
        : "text-gray-400 hover:bg-gray-800 hover:text-white"
    }`;

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_username");
    window.location.href = "/login/admin";
  };

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 p-4 flex flex-col border-r border-gray-700">
        <h2 className="text-xl font-semibold mb-6 text-blue-400">
          🎬 Admin Panel
        </h2>

        <nav className="space-y-2 flex-1">
          <NavLink to="/admin" end className={linkClass}>
            <Users size={18} /> Quản lý người dùng
          </NavLink>
          <NavLink to="/admin/movies" className={linkClass}>
            <Film size={18} /> Quản lý phim
          </NavLink>
          <NavLink to="/admin/settings" className={linkClass}>
            <Settings size={18} /> Cài đặt
          </NavLink>
        </nav>

        <button
          onClick={handleLogout}
          className="mt-auto flex items-center gap-2 px-4 py-2 rounded-md bg-red-600 hover:bg-red-700 text-white text-sm"
        >
          <LogOut size={16} /> Đăng xuất
        </button>
      </aside>

      {/* Nội dung chính */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-gray-800 px-6 py-3 flex items-center justify-between border-b border-gray-700">
          <h1 className="text-lg font-semibold text-gray-100">
            Bảng điều khiển quản trị
          </h1>
          <span className="text-gray-400 text-sm">
            {localStorage.getItem("admin_username")}
          </span>
        </header>

        {/*  Đây là nơi các trang con sẽ hiển thị */}
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
