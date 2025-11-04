import React from "react";
import { Bell, Sun, Moon } from "lucide-react";

export default function AdminHeader({ darkMode, toggleDarkMode }) {
  const username = localStorage.getItem("admin_username") || "Admin";

  return (
    <header className="flex justify-between items-center bg-[#1e293b] border-b border-gray-700 px-6 py-3 shadow-md">
      <h2 className="text-lg font-medium text-gray-200">
        Xin chào, <span className="text-blue-400 font-semibold">{username}</span>
      </h2>

      <div className="flex items-center space-x-4">
        <button className="text-gray-400 hover:text-gray-300">
          <Bell size={20} />
        </button>
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-lg hover:bg-gray-700 transition"
        >
          {darkMode ? (
            <Sun size={20} className="text-yellow-400" />
          ) : (
            <Moon size={20} className="text-gray-400" />
          )}
        </button>
      </div>
    </header>
  );
}
