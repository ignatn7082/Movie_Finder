// import { createContext, useContext, useState } from "react";

// const ChatBotContext = createContext();

// export const ChatBotProvider = ({ children }) => {
//   const [isOpen, setIsOpen] = useState(false);

//   const openChat = () => setIsOpen(true);
//   const closeChat = () => setIsOpen(false);
//   const toggleChat = () => setIsOpen((prev) => !prev);

//   return (
//     <ChatBotContext.Provider value={{ isOpen, openChat, closeChat, toggleChat }}>
//       {children}
//     </ChatBotContext.Provider>
//   );
// };

// export const useChatBot = () => useContext(ChatBotContext);


import { createContext, useContext, useEffect, useState } from "react";

const ChatBotContext = createContext();

export function ChatBotProvider({ children }) {
  const STORAGE_KEY = "chatbot_messages";
  const OPEN_KEY = "chatbot_open";

  //  Khởi tạo từ localStorage nếu có
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved
        ? JSON.parse(saved)
        : [
            {
              from: "bot",
              text: "🎬 Xin chào! Mình là trợ lý phim AI. Hôm nay bạn muốn tìm phim, tóm tắt hay so sánh nội dung nào?",
            },
          ];
    } catch {
      return [
        {
          from: "bot",
          text: "🎬 Xin chào! Mình là trợ lý phim AI. Hôm nay bạn muốn tìm phim, tóm tắt hay so sánh nội dung nào?",
        },
      ];
    }
  });

  const [isOpen, setIsOpen] = useState(() => {
    try {
      return localStorage.getItem(OPEN_KEY) === "true";
    } catch {
      return false;
    }
  });

  //  Tự động lưu mỗi khi hội thoại hoặc trạng thái thay đổi
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(OPEN_KEY, isOpen.toString());
  }, [isOpen]);

  //  Các hàm tiện ích
  const toggleChat = () => setIsOpen((prev) => !prev);
  const closeChat = () => setIsOpen(false);
  const clearChat = () =>
    setMessages([
      {
        from: "bot",
        text: "🎬 Xin chào! Mình là trợ lý phim AI. Hôm nay bạn muốn tìm phim, tóm tắt hay so sánh nội dung nào?",
      },
    ]);

  return (
    <ChatBotContext.Provider
      value={{ isOpen, toggleChat, closeChat, messages, setMessages, clearChat }}
    >
      {children}
    </ChatBotContext.Provider>
  );
}

export const useChatBot = () => useContext(ChatBotContext);
