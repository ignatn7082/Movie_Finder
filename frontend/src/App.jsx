import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Search from "./pages/Search";
import Dataset from "./pages/Dataset";
import About from "./pages/About";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import MoviesList from "./pages/MoviesList";
import ChatBotButton from "./components/ChatBotButton";
import ChatBotPanel from "./components/ChatBotPanel";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminDashboard from "./pages/admin/DashboardHome";
import LoginAdmin from "./pages/LoginAdmin";
import LoginUser from "./pages/LoginUser";
import Register from "./pages/Register";
import Forbidden from "./pages/Forbidden";
import MoviesPanel from "./pages/admin/MoviePanel";
import { ChatBotProvider, useChatBot } from "./context/ChatBotContext";


function GlobalChat() {
  const { isOpen, toggleChat, closeChat } = useChatBot();
  return (
    <>
      <ChatBotButton onClick={toggleChat} />
      {isOpen && <ChatBotPanel onClose={closeChat} />}
    </>
  );
}

/**
 * Layout hiển thị Navbar + Footer chỉ khi user/admin đã đăng nhập
 */
//  Layout chỉ hiện Navbar + Footer khi đã đăng nhập và KHÔNG phải admin
function LayoutWithNavbar({ children }) {
  const userToken = localStorage.getItem("user_token");
  const adminToken = localStorage.getItem("admin_token");

  // Nếu là admin → không hiển thị Navbar, chỉ hiển thị nội dung
  if (adminToken) {
    return <div className="min-h-screen flex flex-col">{children}</div>;
  }

  // Nếu chưa đăng nhập → chuyển hướng về login user
  if (!userToken) {
    return <Navigate to="/login/user" replace />;
  }

  // Nếu là user → hiển thị Navbar + Footer như bình thường
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="h-16" />
      <main className="flex-1 container mx-auto px-4 py-6">{children}</main>
      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <ChatBotProvider>
      <Router>
        <Routes>
          {/* ========================= */}
          {/* Các trang có Navbar + Footer */}
          {/* ========================= */}
          <Route
            path="/"
            element={
              <LayoutWithNavbar>
                <Home />
              </LayoutWithNavbar>
            }
          />
          <Route
            path="/search"
            element={
              <LayoutWithNavbar>
                <Search />
              </LayoutWithNavbar>
            }
          />
          <Route
            path="/dataset"
            element={
              <LayoutWithNavbar>
                <Dataset />
              </LayoutWithNavbar>
            }
          />
          <Route
            path="/about"
            element={
              <LayoutWithNavbar>
                <About />
              </LayoutWithNavbar>
            }
          />
          <Route
            path="/movies"
            element={
              <LayoutWithNavbar>
                <MoviesList />
              </LayoutWithNavbar>
            }
          />

          {/* ========================= */}
          {/* Khu vực chỉ dành cho Admin */}
          {/* ========================= */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute roles={["admin"]}>
              
                  <AdminDashboard />
               
              </ProtectedRoute>
            }
          />

          {/* ========================= */}
          {/* Các trang KHÔNG có Navbar */}
          {/* ========================= */}
          <Route index element={<MoviesPanel />} />
          <Route path="/login/admin" element={<LoginAdmin />} />
          <Route path="/login/user" element={<LoginUser />} />
          <Route path="/register" element={<Register />} />
          <Route path="/403" element={<Forbidden />} />

          {/* ========================= */}
          {/* Fallback */}
          {/* ========================= */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Chatbot luôn hiển thị */}
        <GlobalChat />
      </Router>
    </ChatBotProvider>
  );
}
