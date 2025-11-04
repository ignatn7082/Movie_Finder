import React, { useState } from "react";
import AdminSidebar from "./AdminSidebar";
import AdminHeader from "./AdminHeader";
import AdminPanel from "./AdminPanel";

export default function AdminDashboard() {
  const [darkMode, setDarkMode] = useState(true);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    document.documentElement.classList.toggle("dark", newMode);
  };

  return (
    <div className="flex bg-[#0f172a] text-gray-100 min-h-screen">
      {/* Sidebar trái */}
      <AdminSidebar />

      {/* Vùng nội dung */}
      <div className="flex flex-col flex-1 min-h-screen">
        {/* Header cố định */}
        <AdminHeader darkMode={darkMode} toggleDarkMode={toggleDarkMode} />

        {/* Nội dung chính */}
        <main className="flex-1 bg-[#111827] p-8 overflow-y-auto">
          <div className="max-w-5xl mx-auto">
            <AdminPanel />
          </div>
        </main>
      </div>
    </div>
  );
}
