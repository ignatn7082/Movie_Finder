// components/search/SearchTabs.jsx
import { Image, Type } from "lucide-react";

export default function SearchTabs({ tab, setTab, onTabChange }) {
  const handleTabClick = (newTab) => {
    if (tab !== newTab) {
      setTab(newTab);
      onTabChange();
    }
  };

  return (
    <div className="flex justify-center mb-10">
      <div className="inline-flex bg-gray-100 dark:bg-gray-700 p-2 rounded-2xl shadow-inner">
        <button
          onClick={() => handleTabClick("image")}
          className={`flex items-center px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300 ${
            tab === "image"
              ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          }`}
        >
          <Image className="w-6 h-6 mr-3" />
          Tìm bằng Ảnh
        </button>
        <button
          onClick={() => handleTabClick("text")}
          className={`flex items-center px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300 ${
            tab === "text"
              ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          }`}
        >
          <Type className="w-6 h-6 mr-3" />
          Tìm bằng Văn Bản
        </button>
      </div>
    </div>
  );
}