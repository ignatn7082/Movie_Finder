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
import AdminPanel from "./pages/AdminPanel";
import Login from "./pages/Login";
import LoginAdmin from "./pages/LoginAdmin";
import LoginUser from "./pages/LoginUser";
import Register from "./pages/Register";
import Forbidden from "./pages/Forbidden";
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

//  Layout chỉ hiện Navbar + Footer khi đã đăng nhập
function LayoutWithNavbar({ children }) {
  const isLoggedIn =
    localStorage.getItem("user_token") || localStorage.getItem("admin_token");

  if (!isLoggedIn) {
    //  Nếu chưa đăng nhập, điều hướng về trang đăng nhập user
    return <Navigate to="/login/user" replace />;
  }

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

          {/*  Chỉ admin mới vào được */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute roles={["admin"]}>
                <LayoutWithNavbar>
                  <AdminPanel />
                </LayoutWithNavbar>
              </ProtectedRoute>
            }
          />

          {/* ========================= */}
          {/* Các trang KHÔNG có Navbar */}
          {/* ========================= */}
          {/* <Route path="/login" element={<Login />} /> */}
          <Route path="/login/admin" element={<LoginAdmin />} />
          <Route path="/login/user" element={<LoginUser />} />
          <Route path="/register" element={<Register />} />
          <Route path="/403" element={<Forbidden />} />

          {/* Mặc định điều hướng về trang chủ */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Chatbot luôn hiển thị (dù login hay chưa) */}
        <GlobalChat />
      </Router>
    </ChatBotProvider>
  );
}
