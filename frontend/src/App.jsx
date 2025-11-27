// src/App.jsx
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet
} from "react-router-dom";

// Pages
import Home from "./pages/Home";
import Search from "./pages/Search";
import Dataset from "./pages/Dataset";
import About from "./pages/About";
import MoviesList from "./pages/MoviesList";

// Components
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ChatBotButton from "./components/ChatBotButton";
import ChatBotPanel from "./components/ChatBotPanel";
import ProtectedRoute from "./components/ProtectedRoute";

// Admin
import AdminDashboard from "./pages/admin/DashboardHome";
import AdminPanel from "./pages/admin/AdminPanel";
import MoviesPanel from "./pages/admin/MoviePanel";
import AdminSettings from "./pages/admin/AdminSetting";

// Auth
import Login from "./pages/Login";
import Register from "./pages/Register";
import Forbidden from "./pages/Forbidden";

// Context
import { ChatBotProvider, useChatBot } from "./context/ChatBotContext";

// Chatbot toàn cục
function GlobalChat() {
  const { isOpen, toggleChat, closeChat } = useChatBot();
  return (
    <>
      <ChatBotButton onClick={toggleChat} />
      {isOpen && <ChatBotPanel onClose={closeChat} />}
    </>
  );
}

// Layout chung cho toàn bộ trang user (có Navbar + Footer)
function UserLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white">
      <Navbar />
      <div className="h-20 lg:h-24" /> {/* Khoảng trống cho navbar fixed */}
      <main className="flex-1">
        <Outlet /> {/* Nội dung trang con */}
      </main>
      <Footer />
    </div>
  );
}

// Layout riêng cho khu vực Admin (có Sidebar + Header riêng)
function AdminLayout() {
  return (
    <ProtectedRoute roles={["admin"]}>
      <AdminDashboard />
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <ChatBotProvider>
      <Router>
        <Routes>

          {/* ===== TRANG USER – DÙNG NAVBAR CHUNG ===== */}
          <Route element={<UserLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<Search />} />
            <Route path="/movies" element={<MoviesList />} />
            <Route path="/dataset" element={<Dataset />} />
            <Route path="/about" element={<About />} />
          </Route>

          {/* ===== KHU VỰC ADMIN – DÙNG LAYOUT RIÊNG (Sidebar + Header) ===== */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={
              <div className="p-8 text-3xl font-bold text-gray-100">
                Chào mừng đến bảng điều khiển quản trị!
              </div>
            } />
            <Route path="users" element={<AdminPanel />} />
            <Route path="movies" element={<MoviesPanel />} />
            <Route path="settings" element={<AdminSettings />} />
          </Route>

          {/* ===== AUTH ===== */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/403" element={<Forbidden />} />

          {/* ===== FALLBACK ===== */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Chatbot luôn hiện ở mọi trang */}
        <GlobalChat />
      </Router>
    </ChatBotProvider>
  );
}