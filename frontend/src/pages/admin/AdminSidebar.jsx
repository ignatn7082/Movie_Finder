import React from "react";
import { Users, Film, Settings, LogOut } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

export default function AdminSidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_username");
    navigate("/login/admin");
  };

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-4 py-2 rounded-lg transition ${
      isActive
        ? "bg-blue-600 text-white"
        : "text-gray-300 hover:bg-gray-800 hover:text-white"
    }`;

  return (
    <aside className="bg-[#0b1120] w-64 min-h-screen flex flex-col border-r border-gray-800">
      <div className="p-5 text-lg font-semibold text-blue-400 flex items-center gap-2 border-b border-gray-800">
        🎬 Admin Dashboard
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <NavLink to="/admin" className={linkClass}>
          <Users size={18} /> Người dùng
        </NavLink>
        <NavLink to="/admin/movies" className={linkClass}>
          <Film size={18} /> Quản lý phim
        </NavLink>
        <NavLink to="/admin/settings" className={linkClass}>
          <Settings size={18} /> Cài đặt
        </NavLink>
      </nav>

      <div className="p-4 border-t border-gray-800">
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-red-400 hover:text-red-500 transition"
        >
          <LogOut size={18} /> Đăng xuất
        </button>
      </div>
    </aside>
  );
}
