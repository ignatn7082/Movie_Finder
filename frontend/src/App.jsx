import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Search from "./pages/Search";
import Dataset from "./pages/Dataset";
import About from "./pages/About";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import MoviesList from "./pages/MoviesList";
import ChatBotButton from "./components/ChatBotButton";
import ChatBotPanel from "./components/ChatBotPanel";
import { ChatBotProvider, useChatBot } from "./context/ChatBotContext";

// Component gắn chatbot toàn cục
function GlobalChat() {
  const { isOpen, toggleChat, closeChat } = useChatBot();

  return (
    <>
      <ChatBotButton onClick={toggleChat} />
      {isOpen && <ChatBotPanel onClose={closeChat} />}
    </>
  );
}

export default function App() {
  return (
    <ChatBotProvider>
      <Router>
        <div className="min-h-screen flex flex-col">
          {/* Navbar cố định */}
          <Navbar />
          <div className="h-16" />

          {/* Nội dung chính */}
          <main className="flex-1 container mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/search" element={<Search />} />
              <Route path="/dataset" element={<Dataset />} />
              <Route path="/about" element={<About />} />
              <Route path="/movies" element={<MoviesList />} />
            </Routes>
          </main>

          {/* Footer */}
          <Footer />
        </div>

        {/* Chatbot hiển thị ở tất cả các trang */}
        <GlobalChat />
      </Router>
    </ChatBotProvider>
  );
}
