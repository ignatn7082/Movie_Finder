
import { useState, useEffect, useRef } from "react";
import { Loader2 } from "lucide-react";
import { useChatBot } from "../context/ChatBotContext";
import { API_ENDPOINTS } from "../config/api";

export default function ChatBotPanel({ onClose }) {
  const { messages, setMessages, clearChat } = useChatBot();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Gửi tin nhắn người dùng
  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setMessages((prev) => [...prev, { from: "user", text: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      //  Fetch được di chuyển vào đúng phạm vi
      const res = await fetch(API_ENDPOINTS.chat, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: messages.map((m) => ({
            role: m.from === "user" ? "user" : "assistant",
            content: m.text,
          })),
          prompt: userMessage,
        }),
      });

      const data = await res.json();
      const botReply = data.reply || "🤖 Xin lỗi, mình chưa thể trả lời điều đó.";

      setMessages((prev) => [
        ...prev,
        {
          from: "bot",
          text: botReply,
          relatedMovies: data.related_movies || [],
          intent: data.intent,
        },
      ]);
    } catch (err) {
      console.error("Chatbot error:", err);
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "⚠️ Lỗi kết nối với máy chủ AI." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Tự động cuộn xuống khi có tin nhắn mới
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="fixed bottom-20 right-6 w-96 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-2xl shadow-2xl p-4 flex flex-col z-50">
      {/* Header */}
      <div className="flex justify-between items-center mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">
        <h3 className="font-semibold text-lg text-blue-600">🎥 Trợ lý phim AI</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={clearChat}
            className="text-gray-500 hover:text-yellow-500 text-sm"
            title="Xóa hội thoại"
          >
            🧹
          </button>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-red-500 text-xl leading-none"
            title="Đóng"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-3 pr-2 space-y-2 max-h-80 custom-scrollbar">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex flex-col ${m.from === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`px-3 py-2 rounded-xl max-w-[85%] text-sm whitespace-pre-line ${
                m.from === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              }`}
            >
              {m.text}
            </div>

{/* Gợi ý phim */}
{["recommend", "fallback_suggest"].includes(m.intent) && m.relatedMovies?.length > 0 && (
  <div className="mt-2 bg-gray-50 dark:bg-gray-800 rounded-lg p-2 w-full">
    <p className="text-xs text-gray-500 mb-1 italic">
      🎬 Gợi ý từ hệ thống ({m.intent})
    </p>
    <div className="grid grid-cols-2 gap-2">
      {m.relatedMovies.map((movie, idx) => (
        <div
          key={idx}
          className="flex items-center gap-2 bg-gray-100 dark:bg-gray-900 rounded-md p-2 hover:shadow-sm transition"
        >
          {movie.poster ? (
            <img
              src={movie.poster}
              alt={movie.title}
              className="w-10 h-14 rounded-md object-cover"
            />
          ) : (
            <div className="w-10 h-14 bg-gray-300 rounded-md" />
          )}
          <div>
            <p className="text-xs font-semibold">{movie.title}</p>
            <p className="text-xs text-gray-500">{movie.release_date}</p>
          </div>
        </div>
      ))}
    </div>
  </div>
)}

          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-gray-400 text-sm mt-2">
            <Loader2 className="animate-spin w-4 h-4" />
            Đang phản hồi...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2 items-center">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Nhập câu hỏi về phim..."
          className="flex-1 p-2 text-sm rounded-lg border border-gray-300 dark:border-gray-700 dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 outline-none"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        >
          Gửi
        </button>
      </div>
    </div>
  );
}
